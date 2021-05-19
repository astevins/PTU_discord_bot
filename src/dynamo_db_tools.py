import datetime
import os

import boto3
from dotenv import load_dotenv

load_dotenv()
ACCESS_ID = os.getenv("AWS_ACCESS_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS")


def __get_db_resource__():
    return boto3.resource("dynamodb", region_name="us-west-2", aws_access_key_id=ACCESS_ID,
                          aws_secret_access_key=SECRET_KEY)


def __get_db_client__():
    return boto3.client("dynamodb", region_name="us-west-2", aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY)


def __delete_old_table__(table_name):
    print("Deleting out of date table.")
    dynamodb_client = __get_db_client__()
    dynamodb_client.delete_table(TableName=table_name)
    waiter = dynamodb_client.get_waiter("table_not_exists")
    waiter.wait(TableName=table_name)
    create_table_if_new(table_name)


def create_table_if_new(table_name):
    dynamodb = __get_db_resource__()

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    "AttributeName": "id",
                    "KeyType": "HASH"
                },
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "id",
                    "AttributeType": "S"
                },
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1,
            }
        )
        print(f"Creating table [{table_name}]")
    except Exception as err:
        print(f"Table [{table_name}] already exists")
        return

    table.meta.client.get_waiter("table_exists").wait(TableName=table_name)
    print(f"Finished creating table [{table_name}]")


def put_item_single_value(table_name, id_, value):
    dynamodb = __get_db_resource__()

    table = dynamodb.Table(table_name)
    table.put_item(Item={"id": id_, "value": value})


def get_item_single_value(table_name, id_):
    dynamodb = __get_db_resource__()

    table = dynamodb.Table(table_name)

    response = table.get_item(Key={"id": id_})
    if "Item" in response:
        return response["Item"]["value"]
