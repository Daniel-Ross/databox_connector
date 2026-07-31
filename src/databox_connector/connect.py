from dotenv import load_dotenv
from dataclasses import dataclass, asdict
import databox
from datetime import datetime, timezone
import os
import requests

load_dotenv()


now = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


# Create classes for Databox metrics
@dataclass
class DataboxEntry:
    key: str
    value: int
    date: str


@dataclass
class DataboxDimmedEntry:
    key: str
    value: str
    date: str
    attributes: list[dict]


@dataclass
class MigratedDatasetEntry:
    dateInserted: str
    metricKey: str
    metricName: str
    value: int
    unit: str
    periodFrom: str
    periodTo: str
    dimension: str


def create_databox_records(databox_dict, metric_name):
    """Create non-dimension Databox records

    Args:
        databox_dict (dict): Dictionary of date and count values
        metric_name (str): Name of the metric

    Returns:
        list: List of record dictionaries
    """
    entries = []
    for created_date, count in databox_dict.items():
        created_date_str = created_date
        entry = DataboxEntry(key=metric_name, value=round(count, 2), date=created_date_str)
        entries.append(asdict(entry))
    return entries


def create_databox_dimensioned_records(records, metric_name, dim_type, date_column, count_column):
    """Create dimensioned Databox records

    Args:
        records (list[dict]): List of record dictionaries
        metric_name (str): Name of the metric
        dim_type (_type_): _description_
        date_column (str): Date column
        count_column (str): Column to use for count values

    Returns:
        list[dict] : List of record dictionaries
    """
    entries = []
    for record in records:
        created_date_str = record[date_column]
        entry = DataboxDimmedEntry(
            key=metric_name,
            value=round(record[count_column], 2),
            date=created_date_str,
            attributes=[{"key": dim_type, "value": record[dim_type]}],
        )
        entries.append(asdict(entry))
    return entries


def push_data(data, token=os.getenv("databox_token")):
    """Function to push data to Databox

    Args:
        data (list[dict]): List of dictionaries to push to Databox
    """
    configuration = databox.Configuration(  # type:ignore
        host="https://push.databox.com", username=token, password=""
    )

    with databox.ApiClient(  # type:ignore
        configuration,
        "Accept",
        "application/vnd.databox.v2+json",
    ) as api_client:
        api_instance = databox.DefaultApi(api_client)  # type:ignore
        push_data = data
        try:
            api_instance.data_post(push_data=push_data)
        except Exception as e:
            print("An unexpected error occurred: %s\n" % e)


def create_migrated_dataset_records(
    records: list[dict],
    metric_name: str,
    metric_key: str,
    value_col: str,
    date_col: str,
    dimension_col: str = "",
) -> list[dict]:
    """Create dataset records formatted for Databox migration.

    Args:
        records (list[dict]): List of record dictionaries
        metric_name (str): Display name of the metric
        metric_key (str): Unique key identifying the metric
        value_col (str): Column to use for the metric value
        date_col (str): Column to use for the period dates
        dimension_col (str): Column to use for the dimension value

    Returns:
        list[dict]: List of formatted dataset entry dictionaries
    """
    entries = []
    for record in records:
        entry = MigratedDatasetEntry(
            dateInserted=now,
            metricKey=metric_key,
            metricName=metric_name,
            value=round(record[value_col], 2),
            unit="",
            periodFrom=record[date_col],
            periodTo=record[date_col],
            dimension=record[dimension_col],
        )
        entries.append(asdict(entry))
    return entries

def push_dataset_data(data:list[dict], dataset_id:str, api_key:str | None = os.getenv("databox_api")) -> None:
    """Push data to a Databox dataset via the REST API.

    Args:
        data (list[dict]): List of record dictionaries to push
        dataset_id (str): ID of the target Databox dataset
        api_key (str | None): Databox API key; defaults to the DATABOX_API env var
    """
    if api_key:
        dataset_url = f"https://api.databox.com/v1/datasets/{dataset_id}/data"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        response = requests.post(dataset_url, json=data, headers=headers)
        print(response.json())
    else:
        print("No api_key provided. Aborting push.")
    pass


def push_dataset_records(records: list[dict], dataset_id:str) -> None:
    """Push dataset records to Databox in batches of 100 or fewer.

    Args:
        records (list[dict]): List of record dictionaries to push
    """
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        push_dataset_data(data=batch, dataset_id=dataset_id)
