from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='elt_pipeline',
    default_args=default_args,
    description='ELT pipeline: extract from source_postgres, load to destination_postgres, transform with dbt',
    schedule_interval='0 3 * * *',  # Daily at 3 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['elt', 'postgres', 'dbt'],
) as dag:

    elt_task = DockerOperator(
        task_id='run_elt_script',
        image='elt_script:latest',
        api_version='auto',
        auto_remove=True,
        command='python elt_script.py',
        docker_url='unix://var/run/docker.sock',
        network_mode='elt_network',
        mounts=[
            Mount(
                source='/opt/airflow/elt',
                target='/app',
                type='bind',
            )
        ],
        environment={
            'SOURCE_POSTGRES_DB': 'source_db',
            'SOURCE_POSTGRES_USER': 'postgres',
            'SOURCE_POSTGRES_PASSWORD': 'secret',
            'DESTINATION_POSTGRES_DB': 'destination_db',
            'DESTINATION_POSTGRES_USER': 'postgres',
            'DESTINATION_POSTGRES_PASSWORD': 'secret',
        },
    )

    dbt_task = DockerOperator(
        task_id='run_dbt_transformations',
        image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
        api_version='auto',
        auto_remove=True,
        command='dbt run --profiles-dir /root --project-dir /dbt',
        docker_url='unix://var/run/docker.sock',
        network_mode='elt_network',
        mounts=[
            Mount(
                source='/opt/dbt',
                target='/dbt',
                type='bind',
            ),
            Mount(
                source='/root/.dbt',
                target='/root',
                type='bind',
            ),
        ],
        environment={
            'DBT_PROFILE': 'custom_postgres',
            'DBT_TARGET': 'dev',
        },
    )

    dbt_test_task = DockerOperator(
        task_id='run_dbt_tests',
        image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
        api_version='auto',
        auto_remove=True,
        command='dbt test --profiles-dir /root --project-dir /dbt',
        docker_url='unix://var/run/docker.sock',
        network_mode='elt_network',
        mounts=[
            Mount(
                source='/opt/dbt',
                target='/dbt',
                type='bind',
            ),
            Mount(
                source='/root/.dbt',
                target='/root',
                type='bind',
            ),
        ],
        environment={
            'DBT_PROFILE': 'custom_postgres',
            'DBT_TARGET': 'dev',
        },
    )

    # Pipeline order: ELT → dbt run → dbt test
    elt_task >> dbt_task >> dbt_test_task
