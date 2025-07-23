import sys
from pathlib import Path

src_path = Path(__file__).resolve().parent.parent / 'src'
sys.path.append(str(src_path))

from main import run_main_02_03_ktb

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta, datetime

default_args = {
    'owner':'airflow',
    'depends_on_past':False,
    'email_on_failure':False,
    'email_on_retry':False,
    'retries':1,
    'retry_delay':timedelta(minutes=1),
}

with DAG(
    dag_id="02_03_ktb_pipe_etl_ist_sinir_kapilari_giris_yapan_vatandas",
    default_args=default_args,
    description='A DAG to run data processing script',
    schedule_interval='0 3 * * *',
    start_date=datetime(2025, 7, 11),
    catchup=False
) as dag:
    
    run_data_processing = PythonOperator(
        task_id='run_main_02_03_ktb',
        python_callable=run_main_02_03_ktb,
    )