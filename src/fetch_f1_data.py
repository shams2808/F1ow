import requests
import boto3
import json

# Constants
BUCKET_NAME = "f1ow-data-417521971713"
SEASONS = [2023, 2024, 2025]

def fetch_total_rounds(season):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(f'https://api.jolpi.ca/ergast/f1/{season}.json', headers=headers, timeout=30)
        data = response.json()
        return len(data['MRData']['RaceTable']['Races'])
    except Exception as e:
        print(f"Error fetching total rounds for season {season}: {e}")
        return 0

def fetch_race_result(season, round_num):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(f'https://api.jolpi.ca/ergast/f1/{season}/{round_num}/results.json', headers=headers, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error fetching F1 data for season {season}: {e}")
        return {}
    
def fetch_standings(season, standings_type):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(f'https://api.jolpi.ca/ergast/f1/{season}/{standings_type}.json', headers=headers, timeout=30)
        return response.json()
    except Exception as e:
        print(f"Error fetching F1 standings for season {season}: {e}")
        return {}

def upload_to_s3(data, bucket, key):
    s3_client = boto3.client('s3')
    try:
        s3_client.put_object(Bucket=bucket, Key=key, Body=json.dumps(data))
    except Exception as e:
        print(f"Error uploading to S3: {e}")


def main():
    for season in SEASONS:
        total_rounds = fetch_total_rounds(season)
        for round_num in range(1, total_rounds + 1):
            print(f"Fetching data for season {season}, round {round_num}...")
            data = fetch_race_result(season, round_num)
            if data:
                upload_to_s3(data, BUCKET_NAME, f"raw/{season}/race_results/round_{round_num}.json")
        print(f"Fetching driver standings for season {season}...")
        standings_driver=fetch_standings(season, "driverStandings")
        if standings_driver:
            upload_to_s3(standings_driver, BUCKET_NAME, f"raw/{season}/driver_standings.json")
        print(f"Fetching constructor standings for season {season}...")
        standings_constructors=fetch_standings(season, "constructorStandings")
        if standings_constructors:
            upload_to_s3(standings_constructors, BUCKET_NAME, f"raw/{season}/constructor_standings.json")
        print(f"Season {season} complete!")

if __name__ == "__main__":
    main()