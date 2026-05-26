import boto3
import pandas as pd
from io import BytesIO
import sys
sys.path.insert(0, 'src')
from transform_f1_data import save_to_s3_parquet
from fetch_f1_data import fetch_total_rounds

BUCKET_NAME = "f1ow-data-417521971713"
SEASONS = [2023, 2024, 2025]

s3 = boto3.client("s3")

def read_parquet_from_s3(bucket, key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(BytesIO(response['Body'].read()))

def aggregate_driver_performance(df):
    df['points'] = pd.to_numeric(df['points'], errors='coerce')
    df['finish_position'] = pd.to_numeric(df['finish_position'], errors='coerce')

    result=df.groupby(['season', 'driverid', 'driver_name']).agg(
        total_races=('round', 'count'),
        total_wins=('finish_position', lambda x: (x == 1).sum()),
        podiums=('finish_position', lambda x: (x<=3).sum()),
        total_points=('points', lambda x:(x).sum()),
        avg_points_per_race=('points', 'mean')
    ).reset_index()
    
    return result

def aggregate_constructor_performance(df):
    df['points'] = pd.to_numeric(df['points'], errors='coerce')
    df['finish_position'] = pd.to_numeric(df['finish_position'], errors='coerce')

    cons=df.groupby(['season', 'constructorid', 'constructor_name']).agg(
        total_races=('round', 'nunique'),
        total_wins=('finish_position', lambda x: (x == 1).sum()),
        total_points=('points', lambda x:(x).sum()),
    ).reset_index()

    return cons

def main():
    all_data = []
    
    for season in SEASONS:
        total_rounds = fetch_total_rounds(season)
        for round_num in range(1, total_rounds+1):
            all_data.append(read_parquet_from_s3(BUCKET_NAME, f"silver/{season}/race_results/round_{round_num}.parquet"))
    
    df = pd.concat(all_data)
    
    save_to_s3_parquet(aggregate_driver_performance(df), BUCKET_NAME, "gold/driver_performance/driver_performance.parquet")
    save_to_s3_parquet(aggregate_constructor_performance(df), BUCKET_NAME, "gold/constructor_performance/constructor_performance.parquet")

if __name__ == "__main__":
    main()