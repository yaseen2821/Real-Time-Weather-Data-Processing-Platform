from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from kafka import KafkaConsumer
import boto3

# Initialize Spark session
spark = SparkSession.builder \
    .appName("WeatherDataProcessing") \
    .getOrCreate()

# Kafka consumer configuration
KAFKA_BOOTSTRAP_SERVERS = '<broker-url>:9092'
KAFKA_TOPIC = 'weather-data'

# AWS S3 configuration
s3 = boto3.client('s3')
S3_BUCKET = 'weather-data-bucket'

# Define the schema for incoming weather data
schema = 'coord struct<lon:float, lat:float>, weather array<struct<main:string, description:string>>, main struct<temp:float, pressure:int, humidity:int>, name string'

# Read from Kafka topic
weather_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .load()

# Convert the value (Kafka payload) to string and apply the schema
weather_df = weather_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.coord.lon", "data.coord.lat", "data.main.temp", "data.main.pressure", "data.main.humidity", "data.name")

# Transformation: Convert temperature from Kelvin to Celsius
weather_df = weather_df.withColumn("temp_celsius", (col("temp") - 273.15))

# Write data to S3
query = weather_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("checkpointLocation", "/tmp/spark-checkpoints") \
    .option("path", f"s3a://{S3_BUCKET}/weather-data/") \
    .start()

query.awaitTermination()
