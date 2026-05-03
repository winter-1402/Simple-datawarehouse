from dateutil.relativedelta import relativedelta
import pandas as pd 
from scripts.function_helper import get_max_trip_id, put_data_into_s3,check_and_get_file_exists,transform_yellow_data, transform_green_data , create_data_time
def main():    
    now = pd.to_datetime('now')
    df = {1: pd.DataFrame(), 2: pd.DataFrame(), 3: pd.DataFrame()}
    
    now = now - relativedelta(months=1)
    # Định dạng hiển thị (Tháng/Năm)
    month = now.month
    year = now.year
    
    while check_and_get_file_exists('raw-data', f'green_tripdata_{year}-{month:02d}.parquet') is None and check_and_get_file_exists('raw-data', f'yellow_tripdata_{year}-{month:02d}.parquet') is None:
    
        now = now - relativedelta(months=1)
        month = now.month
        year = now.year
        raw_yellow_taxi_data = transform_yellow_data(check_and_get_file_exists('raw-data', f'yellow_tripdata_{year}-{month:02d}.parquet'))
        raw_green_taxi_data = transform_green_data(check_and_get_file_exists('raw-data', f'green_tripdata_{year}-{month:02d}.parquet'))
        
        df[1] = pd.concat([raw_yellow_taxi_data[0], raw_green_taxi_data[0]], ignore_index=True)
        df[2] = pd.concat([raw_yellow_taxi_data[1], raw_green_taxi_data[1]], ignore_index=True)
        df[3] = pd.concat([raw_yellow_taxi_data[2], raw_green_taxi_data[2]], ignore_index=True)
    
    print(f"Đã xử lý dữ liệu taxi tháng {month}/{year}.")
    
    max_trip_id = get_max_trip_id()
    
    df[1]['trip_id'] = range(max_trip_id + 1, max_trip_id + len(df[1]) + 1)
    df[2]['trip_id'] = range(max_trip_id + 1, max_trip_id + len(df[2]) + 1)
    df[3]['trip_id'] = range(max_trip_id + 1, max_trip_id + len(df[3]) + 1)
    
    df[1].set_index('trip_id').to_csv('/opt/airflow/data/taxi_data_info.csv', index=True)
    df[2].set_index('trip_id').to_csv('/opt/airflow/data/taxi_data_time.csv', index=True)
    df[3].set_index('trip_id').to_csv('/opt/airflow/data/taxi_data_payment.csv', index=True)
    
    create_data_time().to_csv('/opt/airflow/data/data_time.csv', index=False)
    put_data_into_s3('data/data_time.csv', 'data')
    
    put_data_into_s3('data/taxi_data_info.csv', 'data')
    put_data_into_s3('data/taxi_data_time.csv', 'data')
    put_data_into_s3('data/taxi_data_payment.csv', 'data')

