output "artifact_registry_url" {
  description = "Artifact Registry URL"
  value       = google_artifact_registry_repository.devops_oracle.name
}

output "service_account_email" {
  description = "Cloud Run Service Account Email"
  value       = google_service_account.cloud_run_sa.email
}

output "cloud_build_trigger_id" {
  description = "Cloud Build Trigger ID"
  value       = google_cloudbuild_trigger.main_trigger.id
}