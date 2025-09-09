from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from datetime import timedelta
import pandas as pd
from sqlalchemy import create_engine


# Default DAG arguments
DEFAULT_ARGS = {
    "owner": "bonface",      
    "depends_on_past": False,
    "email_on_failure": False,
    "email": ["alerts@eftcorp.com"],  # (placeholder)
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# DAG definition

with DAG(
    dag_id="daily_transactions_etl",
    description="ETL pipeline: ingest CSV → transform → load into MySQL",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 8 * * *",  # runs daily at 08:00 hrs
    start_date=days_ago(1),  # Ensure DAG is active immediately
    catchup=False, # No catchup needed
    tags=["eft", "transactions", "etl"],
) as dag:

    
    # Task 1: Ingest

    @task()
    def ingest(filepath="/usr/local/airflow/data/eftcorptest_dummydata.csv") -> str:
        """
        Ingest raw CSV file.

        """
        print(f"📥 Ingesting file: {filepath}")
        return filepath

    
    # Task 2: Transform

    @task()
    def transform(filepath: str) -> str:
        """
        Clean, validate, and aggregate transaction data.
        Removes anomalous amounts (> 10000).
        Saves to a transformed CSV file (ready for MySQL load).
        """
        # Step 0: Load CSV
        df = pd.read_csv(filepath)

        # Step 1: Drop nulls
        df = df.dropna()

        # Step 2: Enforce column types
        df["bank_id"] = df["bank_id"].astype(str)
        df["customer_id"] = df["customer_id"].astype(str)
        df["amount"] = df["amount"].astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Step 2b: Handle anomalous values (> 10000)
        anomalies = df[df["amount"] > 10000]
        if not anomalies.empty:
            anomaly_path = filepath.replace(".csv", "_anomalies.csv")  # Save anomolous values to separate file for inspection
            anomalies.to_csv(anomaly_path, index=False)
            print(f"⚠️ {len(anomalies)} anomalous rows saved to {anomaly_path}") 

        df = df[df["amount"] <= 10000]

        # Step 3: Aggregate daily totals per bank
        df["date"] = df["timestamp"].dt.date
        agg = (
            df.groupby(["bank_id", "date"], as_index=False)
            .agg(daily_total_by_bank=("amount", "sum"))
        )

        # Step 4: Save transformed file
        outpath = filepath.replace(".csv", "_transformed.csv")
        agg.to_csv(outpath, index=False)

        print(f"Transformed CSV written to {outpath}")
        print(agg.head())  # preview first rows
        return outpath

    
    # Task 3: Load

    @task()
    def load_to_mysql(filepath: str,
                  user="bonface",
                  password="bonface_pass",
                  host="mysql",  
                  port=3306,
                  db="eft_demo"):
    
    # Load transformed data into MySQL.
    # Ensures idempotency by truncating table before each load.
    
    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}")

    df = pd.read_csv(filepath)

    # Truncate existing data
    with engine.begin() as conn:
        conn.execute("TRUNCATE TABLE daily_bank_aggregates")

    # Insert fresh data
    df.to_sql("daily_bank_aggregates", con=engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into MySQL → {db}.daily_bank_aggregates (idempotent)")
