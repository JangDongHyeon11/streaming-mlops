import os
import time
import json
import requests
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import create_engine
from db_utils import (
    open_db_session,
    unique_list_from_col,
    get_table_from_engine,
    prepare_db,
)

TRAINING_SERVICE_SERVER = os.getenv("TRAINING_SERVICE_SERVER", "nginx")
TRAINING_SERVICE_URL_PREFIX = os.getenv("TRAINING_SERVICE_URL_PREFIX", "api/trainers/")
FORECAST_ENDPOINT_URL = os.getenv(
    "FORECAST_ENDPOINT_URL", f"http://nginx/api/forecasters/forecast"
)
SALES_TABLE_NAME = os.getenv("SALES_TABLE_NAME", "rossman_sales")
FORECAST_TABLE_NAME = os.getenv("FORECAST_TABLE_NAME", "forecast_results")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_CONNECTION_URL = os.getenv(
    "DB_CONNECTION_URL",
    f"postgresql://spark_user:admin1234@postgres:{POSTGRES_PORT}/spark_pg_db",
)

def get_all_store_product():
    engine = create_engine(DB_CONNECTION_URL)
    table = get_table_from_engine(engine,SALES_TABLE_NAME)
    session = open_db_session(engine)
    store_ids = unique_list_from_col(session, table, column="store")
    product_names = unique_list_from_col(session, table, column="productname")
    return {"store": store_ids, "productname": product_names}
    
def wait_until_status(
    endpoint, status_to_wait_for, poll_interval=5, timeout_seconds=30
):
    start = time.time()
    while time.time() - start <= timeout_seconds:
        resp = requests.get(endpoint)
        resp = resp.json()
        train_job_id, status = resp["train_job_id"], resp["status"]
        print(f"status: {status}")
        if str(status) in status_to_wait_for:
            break
        time.sleep(poll_interval)