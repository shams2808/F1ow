from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat, lit
from pyspark.sql.types import *
import boto3
import json
from io import BytesIO
from fetch_f1_data import fetch_total_rounds

BUCKET_NAME = "f1ow-data-417521971713"
SEASONS = [2023, 2024, 2025]

def create_spark_session():
    import os
    os.environ['PYSPARK_SUBMIT_ARGS'] = '--master local[*] pyspark-shell'
    return SparkSession.builder \
        .appName("F1ow-Transform") \
        .master("local[*]") \
        .config("spark.driver.host", "localhost") \
        .getOrCreate()

def read_bronze_data(spark, season, round_num):
    s3 = boto3.client('s3')
    response = s3.get_object(
        Bucket=BUCKET_NAME,
        Key=f"bronze/{season}/race_results/round_{round_num}.json"
    )
    data = json.loads(response['Body'].read())
    return data

def extract_race_records(data, season, round_num):
    race_info = data['MRData']['RaceTable']['Races'][0]
    records = []
    for result in race_info['Results']:
        records.append({
            "season": season,
            "round": round_num,
            "race_name": race_info['raceName'],
            "circuit_name": race_info['Circuit']['circuitName'],
            "country": race_info['Circuit']['Location']['country'],
            "date": race_info['date'],
            "driver_id": result['Driver']['driverId'],
            "driver_code": result['Driver']['code'],
            "driver_name": result['Driver']['givenName'] + " " + result['Driver']['familyName'],
            "driver_nationality": result['Driver']['nationality'],
            "constructor_id": result['Constructor']['constructorId'],
            "constructor_name": result['Constructor']['name'],
            "grid_position": int(result.get('grid', 0)),
            "finish_position": int(result.get('position', 0)),
            "points": float(result.get('points', 0)),
            "laps": int(result.get('laps', 0)),
            "status": result.get('status', None),
            "fastest_lap_time": result.get('FastestLap', {}).get('Time', {}).get('time', None),
            "fastest_lap_rank": int(result.get('FastestLap', {}).get('rank', 0)) if result.get('FastestLap') else None
        })
    return records

def save_to_s3_parquet_spark(df, season, round_num):
    s3 = boto3.client('s3')
    buffer = BytesIO()
    pandas_df = df.toPandas()
    pandas_df.to_parquet(buffer, index=False)
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"silver/spark/{season}/race_results/round_{round_num}.parquet",
        Body=buffer.getvalue()
    )
    print(f"Saved season {season} round {round_num} to silver/spark")

def main():
    spark = create_spark_session()
    
    for season in SEASONS:
        total_rounds = fetch_total_rounds(season)
        for round_num in range(1, total_rounds + 1):
            print(f"Processing season {season}, round {round_num}...")
            data = read_bronze_data(spark, season, round_num)
            records = extract_race_records(data, season, round_num)
            df = spark.createDataFrame(records)
            save_to_s3_parquet_spark(df, season, round_num)
        print(f"Season {season} complete!")
    
    spark.stop()

if __name__ == "__main__":
    main()
    