from sqlalchemy import create_engine
from scripts.function_helper import check_and_get_file_exists   # The driver for PostgreSQL

# 1. Initialize the S3 client pointing to MinIO
def main():
    data_info = check_and_get_file_exists('data', 'taxi_data_info.csv')
    data_payment = check_and_get_file_exists('data', 'taxi_data_payment.csv')
    data_time = check_and_get_file_exists('data', 'taxi_data_time.csv')
    zone_lookup = check_and_get_file_exists('data', 'taxi_zone_lookup.csv')
    data_time_lookup = check_and_get_file_exists('data', 'data_time.csv')
    
    # Column mapping: CSV names → Database column names
    trip_info_mapping = {
        'VendorID': 'vendorid',
        'RatecodeID': 'ratecodeid',
        'PULocationID': 'pulocationid',
        'DOLocationID': 'dolocationid',
    }
    
    data_payment_mapping = {
        'Airport_fee': 'airport_fee'
    }
    
    zone_mapping = {
        'LocationID': 'location_id',
        'Borough': 'borough',
        'Zone': 'zone_name',
        'service_zone': 'service_zone'
    }
    
    # Rename columns to match database schema
    data_info = data_info.rename(columns=trip_info_mapping)
    data_payment = data_payment.rename(columns=data_payment_mapping)
    zone_lookup = zone_lookup.rename(columns=zone_mapping)
    
    # Connect to PostgreSQL
    engine = create_engine('postgresql://airflow:airflow@localhost:5432/airflow')
    
    try:
        
        zone_lookup.to_sql('dim_location', engine, chunksize=1000, if_exists='append', index=False)
        print("✅ Zone lookup data inserted successfully!")
        data_time_lookup.to_sql('dim_date', engine, chunksize=1000, if_exists='append', index=False)
        print("✅ Date lookup data inserted successfully!")
        
        data_info.to_sql('trip_info', engine, chunksize=1000, if_exists='append', index=False)
        print("✅ Trip info data inserted successfully!")
        data_payment.to_sql('trip_data_payment', engine, chunksize=1000, if_exists='append', index=False)
        print("✅ Payment data inserted successfully!")
        data_time.to_sql('trip_data_time', engine, chunksize=1000, if_exists='append', index=False)
        print("✅ Time data inserted successfully!")
    
        print("\n🎉 All data loaded successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()