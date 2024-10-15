import boto3

# AWS Redshift credentials
redshift_client = boto3.client('redshift')
redshift_cluster_identifier = '<your-cluster-id>'
database_name = '<database-name>'
table_name = '<table-name>'
iam_role = '<redshift-iam-role>'

# Load processed data from S3 to Redshift
s3_path = f"s3://{S3_BUCKET}/weather-data/"
copy_query = f"""
    COPY {table_name}
    FROM '{s3_path}'
    IAM_ROLE '{iam_role}'
    FORMAT AS PARQUET;
"""

# Execute the query in Redshift
redshift_client.execute_statement(Database=database_name, Sql=copy_query)
