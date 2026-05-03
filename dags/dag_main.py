from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts import download_data, transform_data, load_data

# Giả sử bạn để 3 file script trong thư mục cùng cấp với DAG
# hoặc import các hàm xử lý từ chúng

def process_file_1():
    download_data.main()
    print("Đang chạy file 1: Trích xuất dữ liệu...")

def process_file_2():
    transform_data.main()   
    print("Đang chạy file 2: Tính toán trừ ngày hiện tại...")

def process_file_3():
    load_data.main()
    print("Đang chạy file 3: Đẩy dữ liệu vào Postgres...")

with DAG(
    dag_id='sequence_3_files',
    start_date=datetime(2026, 6, 1),
    schedule_interval= '0 0 1 * *',  # Monthly
    catchup=False
) as dag:
    
    t1 = PythonOperator(task_id='run_file_1', python_callable=process_file_1)
    t2 = PythonOperator(task_id='run_file_2', python_callable=process_file_2)
    t3 = PythonOperator(task_id='run_file_3', python_callable=process_file_3)

    # THIẾT LẬP THỨ TỰ: 1 xong mới đến 2, 2 xong mới đến 3
    t1 >> t2 >> t3