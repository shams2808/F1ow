from pyspark.sql import SparkSession
from pyspark.sql.functions import col, monotonically_increasing_id, avg, count, sum, when
import boto3
from io import BytesIO
import sys
sys.path.insert(0, 'src')
from fetch_f1_data import fetch_total_rounds

BUCKET_NAME = "f1ow-data-417521971713"
SEASONS = [2023, 2024, 2025]

def create_spark_session():
    return SparkSession.builder \
        .appName("F1ow-StarSchema") \
        .getOrCreate()

def read_silver_data(spark):
    s3 = boto3.client('s3')
    all_dfs = []
    for season in SEASONS:
        total_rounds = fetch_total_rounds(season)
        for round_num in range(1, total_rounds + 1):
            response = s3.get_object(
                Bucket=BUCKET_NAME,
                Key=f"silver/spark/{season}/race_results/round_{round_num}.parquet"
            )
            import pandas as pd
            pdf = pd.read_parquet(BytesIO(response['Body'].read()))
            all_dfs.append(spark.createDataFrame(pdf))
    
    result = all_dfs[0]
    for df in all_dfs[1:]:
        result = result.unionAll(df)
    return result

def create_dim_driver(df):
    return df.select(
        col("driver_id"),
        col("driver_code"),
        col("driver_name"),
        col("driver_nationality")
    ).distinct()

def create_dim_constructor(df):
    return df.select(
        col("constructor_id"),
        col("constructor_name")
    ).distinct()

def create_dim_race(df):
    return df.select(
        col("season"),
        col("round"),
        col("race_name"),
        col("circuit_name"),
        col("country"),
        col("date")
    ).distinct()

def create_fact_race_results(df):
    return df.select(
        col("season"),
        col("round"),
        col("driver_id"),
        col("constructor_id"),
        col("grid_position"),
        col("finish_position"),
        col("points"),
        col("laps"),
        col("status"),
        col("fastest_lap_time"),
        col("fastest_lap_rank")
    )

def save_table(df, table_name):
    s3 = boto3.client('s3')
    import pandas as pd
    buffer = BytesIO()
    df.toPandas().to_parquet(buffer, index=False)
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"gold/star_schema/{table_name}/{table_name}.parquet",
        Body=buffer.getvalue()
    )
    print(f"Saved {table_name} to gold/star_schema/")

def main():
    spark = create_spark_session()
    
    print("Reading silver data...")
    df = read_silver_data(spark)
    
    print("Creating dimension tables...")
    dim_driver = create_dim_driver(df)
    dim_constructor = create_dim_constructor(df)
    dim_race = create_dim_race(df)
    fact_race_results = create_fact_race_results(df)
    
    print("Saving star schema tables...")
    save_table(dim_driver, "dim_driver")
    save_table(dim_constructor, "dim_constructor")
    save_table(dim_race, "dim_race")
    save_table(fact_race_results, "fact_race_results")
    
    print("Star schema complete!")
    spark.stop()

if __name__ == "__main__":
    main()