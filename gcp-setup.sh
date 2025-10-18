# Set your project ID (choose a unique name)
export PROJECT_ID="devops-oracle-$(date +%s)"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID --name="DevOps Oracle"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com

# Create service account
gcloud iam service-accounts create devops-oracle-sa \
  --display-name="DevOps Oracle Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:devops-oracle-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:devops-oracle-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"

# Download service account key
gcloud iam service-accounts keys create ~/devops-oracle-key.json \
  --iam-account=devops-oracle-sa@${PROJECT_ID}.iam.gserviceaccount.com

echo "Google Cloud setup complete!"
echo "Project ID: $PROJECT_ID"
echo "Service account key saved to: ~/devops-oracle-key.json"