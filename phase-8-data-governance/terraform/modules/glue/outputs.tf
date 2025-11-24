output "data_bucket_name" {
  description = "S3 data lake bucket name"
  value       = aws_s3_bucket.data_lake.bucket
}

output "glue_database_name" {
  description = "Glue database name"
  value       = aws_glue_catalog_database.ecom_data.name
}

output "glue_crawler_name" {
  description = "Glue crawler name"
  value       = aws_glue_crawler.ecom_crawler.name
}

output "glue_job_name" {
  description = "Glue ETL job name"
  value       = aws_glue_job.ecom_etl.name
}
