import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

print("Starting ETL job...")

# Read raw data from S3
datasource0 = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={"paths": ["s3://${data_bucket}/raw/"]},
    format="csv",
    format_options={"withHeader": True}
)

print("Raw data count: ", datasource0.count())

# Simple transformation - convert price to float
def transform_data(rec):
    if 'price' in rec and rec['price']:
        try:
            rec["price"] = float(rec["price"])
        except:
            rec["price"] = 0.0
    return rec

transformed_data = Map.apply(frame=datasource0, f=transform_data)

print("Transformed data count: ", transformed_data.count())

# Write processed data to processed folder
glueContext.write_dynamic_frame.from_options(
    frame=transformed_data,
    connection_type="s3",
    connection_options={"path": "s3://${data_bucket}/processed/"},
    format="parquet"
)

print("ETL job completed successfully!")
job.commit()
