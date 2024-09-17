from databox import Client
from dotenv import dotenv_values
from dataclasses import dataclass

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
    attributes: dict


def create_databox_records(databox_dict, metric_name):
    entries = []
    for created_date, count in databox_dict.items():
        created_date_str = created_date.strftime("%Y-%m-%d")
        entry = DataboxEntry(key=metric_name, value=count, date=created_date_str)
        entries.append(entry)
    return entries


def create_databox_dimensioned_records(records, metric_name, dim_type):
    entries = []
    for record in records:
        created_date_str = record["leads_createdon_date"].strftime("%Y-%m-%d")
        entry = DataboxDimmedEntry(
            key=metric_name,
            value=record["count"],
            date=created_date_str,
            attributes={dim_type: record["source_campaign"]},
        )
        entries.append(entry)
    return entries


databox_client = Client(config["databox_token"])
