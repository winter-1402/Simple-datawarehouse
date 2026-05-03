from botocore.exceptions import ClientError
import requests
import boto3
from botocore.client import Config
import io
import pandas as pd 
import numpy as np
from datetime import datetime

def create_data_time():
    now = pd.to_datetime('now')
    dates = pd.date_range(start=datetime(2025, 5, 3), end=now, freq='D')
    data_time = pd.DataFrame({
        'date_id': range(len(dates)),
        'year': dates.year,
        'month': dates.month,
        'day': dates.day
    })
    return data_time

# Define helper functions for S3 interactions and data transformation
def check_and_create_bucket(bucket_name):
    try:
        s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000', # Include http:// or https:// here
    aws_access_key_id='system_user',
    aws_secret_access_key='system_password',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1' # MinIO defaults to us-east-1 if not specified
)

        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' đã tồn tại.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"Bucket chưa tồn tại. Đang tạo '{bucket_name}'...")
            s3.create_bucket(Bucket=bucket_name)
            print("Tạo thành công!")
        else:
            print(f"Lỗi không xác định: {e}")
            
def check_and_get_file_exists(bucket_name, filename):
    s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000', # Include http:// or https:// here
    aws_access_key_id='system_user',
    aws_secret_access_key='system_password',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1' # MinIO defaults to us-east-1 if not specified
)
    try:
        data = s3.get_object(Bucket=bucket_name, Key=filename)
        if filename.endswith('.csv'):
            data = pd.read_csv(io.BytesIO(data['Body'].read()))
        elif filename.endswith('.parquet'):
            data = pd.read_parquet(io.BytesIO(data['Body'].read()))
        return data
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            return None
        else:
            print(f"Lỗi không xác định: {e}")
            return None

def put_data_into_s3(url, bucket_name):
    s3 = boto3.client(
    's3',
    endpoint_url='http://minio:9000', # Include http:// or https:// here
    aws_access_key_id='system_user',
    aws_secret_access_key='system_password',
    config=Config(signature_version='s3v4'),
    region_name='us-east-1' # MinIO defaults to us-east-1 if not specified
)
    filename = url.split("/")[-1]
    check_file = check_and_get_file_exists(bucket_name, filename)
    if check_file is not None:
        print(f"File '{filename}' đã tồn tại trong bucket '{bucket_name}'. Bỏ qua upload.")
        return True
    try:
        if url.startswith("http"):
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            s3.put_object(Bucket=bucket_name, Key=filename, Body=response.content)
        else :
            with open(url, 'rb') as file_data:
                s3.put_object(Bucket=bucket_name, Key=filename, Body=file_data)
        print(f"✅ Successfully uploaded {filename} to bucket '{bucket_name}'")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
def transform_data(data, taxi_type):
    if data is None:
        return None
    data_time = create_data_time()
    if taxi_type == 'yellow':
        pickup_col = 'tpep_pickup_datetime'
        dropoff_col = 'tpep_dropoff_datetime'
    else:
        pickup_col = 'lpep_pickup_datetime'
        dropoff_col = 'lpep_dropoff_datetime'
        
    data['RatecodeID'] = data['RatecodeID'].fillna(99).astype(np.int64)
    data['payment_type'] = data['payment_type'].fillna(5).astype(np.int64)
    for i in ['passenger_count','congestion_surcharge']:
        data[i] = data[i].fillna(0).astype(np.int64)
        
    data[pickup_col] = pd.to_datetime(data[pickup_col])
    data[dropoff_col] = pd.to_datetime(data[dropoff_col])
    data['pickup_date'] = data[pickup_col].dt.date
    data['pickup_time'] = data[pickup_col].dt.time
    data['duration'] = data[dropoff_col] - data[pickup_col]
    data['duration'] = data['duration'].astype(str).str.split(' ').str[-1]# Convert duration to minutes
    data['duration'] = data['duration'].str.replace('+', '')  

    # Set datetime làm index
    data_time['date'] = pd.to_datetime(data_time[['year', 'month', 'day']])
    data_time = data_time.set_index('date')
    # Map dựa vào index
    data['date_id'] = data['pickup_date'].map(data_time['date_id'])
    data['date_id'] = data['date_id'].fillna(0).astype(np.int64)  # Fill NaN with 0 and convert to int
    
    data.drop(columns=[pickup_col, dropoff_col], inplace=True)  # Drop the datetime columns as they are not relevant for green taxis
    data = data.drop(columns=['store_and_fwd_flag','pickup_date']) 
    return data

def transform_yellow_data(yellow_data):
    yellow_data = transform_data(yellow_data, 'yellow')
    if yellow_data is None:
        return None, None, None
    yellow_data['Airport_fee'] = yellow_data['Airport_fee'].fillna(0).astype(np.int64)     
    yellow_data['trip_type'] = 0
    yellow_data['type_id'] = 1
    
    yellow_taxi_data_info = yellow_data[['trip_type', 'type_id','VendorID', 'passenger_count', 'trip_distance', 'RatecodeID','PULocationID','DOLocationID']]
    yellow_taxi_data_time = yellow_data[['date_id', 'pickup_time', 'duration']]
    yellow_taxi_data_time = yellow_taxi_data_time.rename(columns={'date_id': 'pickup_date_id'})
    yellow_taxi_data_payment = yellow_data[['payment_type', 'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 'total_amount', 'congestion_surcharge','Airport_fee','cbd_congestion_fee']]
    
    print("Yellow data transformed successfully!")
    return yellow_taxi_data_info, yellow_taxi_data_time, yellow_taxi_data_payment

def transform_green_data(green_data):
    green_data = transform_data(green_data, 'green')
    if green_data is None:
        return None, None, None
    green_data['trip_type'] = green_data['trip_type'].fillna(0).astype(np.int64)
    green_data = green_data.drop(columns=['ehail_fee'])
    green_data['Airport_fee'] = 0.0
    green_data['type_id'] = 2
    green_data['Airport_fee'] =  0   

    green_taxi_data_info = green_data[[ 'trip_type', 'type_id','VendorID', 'passenger_count', 'trip_distance', 'RatecodeID','PULocationID','DOLocationID',]]
    green_taxi_data_time = green_data[['date_id', 'pickup_time', 'duration']]
    green_taxi_data_time = green_taxi_data_time.rename(columns={'date_id': 'pickup_date_id'})
    green_taxi_data_payment = green_data[['payment_type', 'fare_amount', 'extra', 'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 'total_amount', 'congestion_surcharge','Airport_fee','cbd_congestion_fee']]
     
    print("Green data transformed successfully!")
    return green_taxi_data_info, green_taxi_data_time, green_taxi_data_payment

def get_max_trip_id():
    response  = check_and_get_file_exists('data', 'taxi_data_info.csv') 
    if response is not None:
        max_id = response['trip_id'].max()
    else:
        max_id = 0
    return max_id
