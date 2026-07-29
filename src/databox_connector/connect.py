from dotenv import load_dotenv
from dataclasses import dataclass, asdict
import databox
import os

load_dotenv()


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


# databox_client = Client(config["databox_token"])


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

def create_migrated_dataset_records(metric_name:str, datasetId:str):
    pass

def push_dataset_records():
    pass
