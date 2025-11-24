output "data_bucket_name" {
  description = "S3 data lake bucket name"
  value       = module.glue.data_bucket_name
}

output "glue_database_name" {
  description = "Glue database name"
  value       = module.glue.glue_database_name
}

output "glue_crawler_name" {
  description = "Glue crawler name"
  value       = module.glue.glue_crawler_name
}

output "glue_job_name" {
  description = "Glue ETL job name"
  value       = module.glue.glue_job_name
}
