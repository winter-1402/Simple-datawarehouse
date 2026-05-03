from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from scripts.function_helper import check_and_create_bucket, put_data_into_s3

def main():
    check_and_create_bucket("raw-data")
    check_and_create_bucket("data")
    check_and_create_bucket("image")
        
    print("\n🚀 Starting to download taxi data and send to minIO...\n")

    now = datetime.now() 
    month = now.month
    year = now.year
    url_yellow_taxidata = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
    url_green_taxidata = f"https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet"

    while not (put_data_into_s3(url_yellow_taxidata, "raw-data") and  put_data_into_s3(url_green_taxidata, "raw-data")):   
        now = now - relativedelta(months=1)
        month = now.month
        year = now.year
        url_yellow_taxidata = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
        url_green_taxidata = f"https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet"
        
    url_zone_lookup = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    with requests.get(url_zone_lookup) as response:
        response.raise_for_status()
    with open('/opt/airflow/data/taxi_zone_lookup.csv', 'wb') as f:
        f.write(response.content)
    put_data_into_s3(url_zone_lookup, 'data')
    
    url_map = [
        "https://www.nyc.gov/assets/tlc/images/content/pages/about/taxi_zone_map_brooklyn.jpg",
        "https://www.nyc.gov/assets/tlc/images/content/pages/about/taxi_zone_map_manhattan.jpg",
        "https://www.nyc.gov/assets/tlc/images/content/pages/about/taxi_zone_map_queens.jpg",
        "https://www.nyc.gov/assets/tlc/images/content/pages/about/taxi_zone_map_staten_island.jpg"
    ]
    for url in url_map:
        put_data_into_s3(url, 'image')