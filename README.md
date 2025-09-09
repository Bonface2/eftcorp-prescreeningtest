# EFT CORP Pre Screening Test README

To access the deliverables of this test, clone this repository:
 git clone <https://github.com/Bonface2/eftcorptest.git>  
 cd <insert repo-folder path>  

You will find:
1. eftcorp_test_dag.py - An Apache Airflow DAG in Python
2. eftcorppythontest.ipynb - A Python function that cleans null values, validates column types, and aggregates daily transaction totals by bank_id. (This function is also defined as a task in the DAG in 1.)
3. eftcorptest_dummydata.csv - The dummy data to be ingested, transformed, and loaded by the DAG. 
4. eftcorptest.sql - A SQL file with 2 SQL statements that query the Top 5 banks by transaction volume in the last 7 days and the Average transaction value per customer for a given month. The query assumes the structure of the file `eftcorptest_dummydata.xlsx` and uses the MySQL dialect. The excel is used as a reference because the data present in MySQL after running the DAG will be transformed to not include columns necessary for the requirements of this SQL test.
5. EFT Corp Pre Screening Test Dashboard.pbix - A Power BI dashboard file
6. eftcorptest_dummydata.xlsx - Dummy data in Excel format visualised by the dashboard in 5.

---

# Transaction ETL DAG

This Apache Airflow DAG ingests raw transaction CSV files, cleans and validates them, aggregates daily totals per bank, and loads the transformed CSVs to a MySQL database.

## Setup Instructions
These instructions assume that Apache Airflow service is already running and therefore skips Apache Airflow installation steps in the local machine.

1. **Upload the DAG**  
   - Copy the DAG file (`eftcorp_test_dag.py`) into your Airflow environment’s `dags/` folder.  
   - If using a managed service (e.g., MWAA, Astronomer, GCP Composer), upload via the UI, CLI, or S3/GCS mount depending on your platform.

2. **Install Dependencies**  
   Ensure the following Python packages are available in your Airflow environment:  
   - pandas  
   - sqlalchemy  
   - mysql-connector-python  
   For managed services, add these to the environment’s requirements file.  

3. **Prepare Input Data**  
   The DAG expects an input file named `eftcorptest_dummydata.csv` which is included in this repo.  

   - Copy the file into Airflow’s data folder:  
     ```bash
     mkdir -p /usr/local/airflow/data/
     cp eftcorptest_dummydata.csv /usr/local/airflow/data/
     ```
   - The DAG will look for the file at:  
     ```
     /usr/local/airflow/data/eftcorptest_dummydata.csv
     ```
   - Should you prefer a different location, edit:  
     ```python
     def ingest(filepath="/usr/local/airflow/data/eftcorptest_dummydata.csv"):
     ```
     to the preferred location.

4. **Run the DAG**  
   - In the Airflow UI, trigger the DAG `daily_transactions_etl` manually, or let it run on its schedule (daily at 08:00).  
   - The transformed CSV will be saved in the same directory with `_transformed.csv` suffix.  
   - Transformed data will also be loaded into MySQL (table: `daily_bank_aggregates`).  

5. **Transformation Logic**  
   The DAG performs the following steps:  
   - Drops rows with nulls  
   - Casts all columns to correct data types  
   - Filters out anomalous transactions (`amount > 10000`)  
   - Aggregates daily totals per bank  

6. **Output Schema**  
   The transformed CSV and MySQL table have the following schema:  
   - bank_id  
   - date  
   - daily_total_by_bank  

---

# Power BI Dashboard Setup

This dashboard visualises:  
- Daily total transaction volume  
- Top 5 banks by volume  
- Monthly trend comparison  
- Anomalous volume detection  

The instructions below assume that Power BI Desktop is installed locally. Publishing to Power BI Service was not possible due to license restrictions.

## Instructions
1. Clone this repo (already done if following earlier steps).  
2. Locate the dashboard file: 
3. Ensure the data file `eftcorptest_dummydata.xlsx` (included in the repo) is available.  
- If the file has been moved, update the path inside Power BI: **Home > Transform data > Data source settings**. This will point Power BI to wherever the Excel file is now located on your machine.
4. Double-click the `.pbix` file to open it in Power BI Desktop.  
5. Click **Refresh** in Power BI Desktop to load the latest data into the dashboard.  


Please feel free to contact me at **bonfacekmwaura@gmail.com** should you encounter any issues. I will be happy to help. Many thanks! 
