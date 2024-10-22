from dotenv import dotenv_values
from dataclasses import dataclass, asdict
import databox

config = dotenv_values()


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
        count_column (float or int): Column to use for count values

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


def push_data(data):
    """Function to push data to Databox

    Args:
        data (list[dict]): List of dictionaries to push to Databox
    """
    ### New version of SDK
    # Configuration setup for the Databox API client
    # The API token is used as the username for authentication
    # It's recommended to store your API token securely, e.g., in an environment variable
    configuration = databox.Configuration(  # type:ignore
        host="https://push.databox.com", username=config["databox_token"], password=""
    )

    # It's crucial to specify the correct Accept header for the API request
    with databox.ApiClient(  # type:ignore
        configuration,
        "Accept",
        "application/vnd.databox.v2+json",
    ) as api_client:
        api_instance = databox.DefaultApi(api_client)  # type:ignore

        # Define the data to be pushed to the Databox Push API# Prepare the data you want to push to Databox
        # The 'key' should match a metric in your Databox account, 'value' is the data point, 'unit' is optional, and 'date' is the timestamp of the data point
        # push_data = [
        #     {
        #         "key": "sales2",
        #         "value": 100,
        #         "unit": "USD",
        #         "date": "2021-01-01T00:00:00Z",
        #     }
        # ]
        push_data = data
        try:
            api_instance.data_post(push_data=push_data)
        except Exception as e:
            # Handle any other unexpected exceptions
            print("An unexpected error occurred: %s\n" % e)
