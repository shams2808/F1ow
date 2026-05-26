import boto3
import json
import pandas as pd
from io import BytesIO
import sys
sys.path.insert(0, 'src')
from fetch_f1_data import fetch_total_rounds

BUCKET_NAME = "f1ow-data-417521971713"
SEASONS = [2023, 2024, 2025]

s3 = boto3.client("s3")

def read_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(response['Body'].read())

def transform_race_results(data, season, round_num):
    race_info = data['MRData']['RaceTable']['Races'][0]
    race_name = race_info['raceName']
    circuit_name = race_info['Circuit']['circuitName']
    country = race_info['Circuit']['Location']['country']
    date = race_info['date']

    results = []
    for race in data['MRData']['RaceTable']['Races'][0]['Results']:
        results.append( {
            "season": season,
            "round": round_num,
            "racename": race_name,
            "circuitname": circuit_name,
            "country": country,
            "date": date,
            "driverid": race['Driver']['driverId'],
            "driver_code": race['Driver']['code'],
            "driver_name": race['Driver']['givenName'] + " " + race['Driver']['familyName'],
            "driver_nationality": race['Driver']['nationality'],
            "constructorid": race['Constructor']['constructorId'],
            "constructor_name": race['Constructor']['name'],
            "grid_position": race['grid'],
            "finish_position": race['position'],
            "points": race['points'],
            "laps": race['laps'],
            "status": race['status'],
            "fastest_lap_time": race.get('FastestLap', {}).get('Time', {}).get('time', None),
            "fastest_lap_rank": race.get('FastestLap', {}).get('rank', None)
        })
    return results

def save_to_s3_parquet(df, bucket, key):
    out_buffer = BytesIO()
    df.to_parquet(out_buffer, index=False)
    s3.put_object(Bucket=bucket, Key=key, Body=out_buffer.getvalue())

def main():
    for season in SEASONS:
        total_rounds = fetch_total_rounds(season)
        for round_num in range(1, total_rounds + 1):
            print(f"Transforming data for season {season}, round {round_num}...")
            data = read_from_s3(BUCKET_NAME, f"bronze/{season}/race_results/round_{round_num}.json")
            transformed_data = transform_race_results(data, season, round_num)
            df = pd.DataFrame(transformed_data)
            save_to_s3_parquet(df, BUCKET_NAME, f"silver/{season}/race_results/round_{round_num}.parquet")
        print(f"Season {season} transformation complete!")

if __name__ == "__main__":
    main()