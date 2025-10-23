terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "devops-oracle-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudresourcemanager.googleapis.com",
  ])
  
  service            = each.value
  disable_on_destroy = false
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "devops_oracle" {
  location      = var.region
  repository_id = "devops-oracle"
  description   = "DevOps Oracle container images"
  format        = "DOCKER"
  
  depends_on = [google_project_service.required_apis]
}

# Service Account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "devops-oracle-run-sa"
  display_name = "DevOps Oracle Cloud Run Service Account"
}

# Grant necessary permissions to service account
resource "google_project_iam_member" "cloud_run_sa_vertex" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_secret" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Secret Manager Secrets
resource "google_secret_manager_secret" "elastic_cloud_id" {
  secret_id = "elastic-cloud-id"
  
  replication {
    auto {}
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "elastic_api_key" {
  secret_id = "elastic-api-key"
  
  replication {
    auto {}
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "vertex_ai_key" {
  secret_id = "vertex-ai-key"
  
  replication {
    auto {}
  }
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Build Service Account permissions
resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_sa_user" {
  project = var.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

resource "google_project_iam_member" "cloudbuild_artifact_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${var.project_number}@cloudbuild.gserviceaccount.com"
}

# Cloud Build Trigger (connected to GitHub)
resource "google_cloudbuild_trigger" "main_trigger" {
  name        = "devops-oracle-deploy"
  description = "Deploy DevOps Oracle on push to main"
  
  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }
  
  filename = "cloudbuild.yaml"
  
  substitutions = {
    _REGION           = var.region
    _BACKEND_SERVICE  = "devops-oracle-api"
    _FRONTEND_SERVICE = "devops-oracle-frontend"
    _ARTIFACT_REGISTRY = "devops-oracle"
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_artifact_registry_repository.devops_oracle
  ]
}

# Cloud Monitoring Alert Policy (optional but recommended)
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "DevOps Oracle - High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate > 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration        = "60s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = []
  
  alert_strategy {
    auto_close = "1800s"
  }
}