#!/bin/bash

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 DevOps Oracle - GCP Deployment${NC}"
echo "========================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first.${NC}"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform not found. Please install it first.${NC}"
    exit 1
fi

# Get project configuration
read -p "Enter your GCP Project ID: " PROJECT_ID
read -p "Enter your GCP Region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

echo ""
echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo ""

# Set active project
gcloud config set project $PROJECT_ID

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo -e "${GREEN}Step 1: Enable Required APIs${NC}"
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com \
    cloudresourcemanager.googleapis.com

echo -e "${GREEN}Step 2: Create Terraform State Bucket${NC}"
BUCKET_NAME="${PROJECT_ID}-terraform-state"
if ! gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
    gsutil mb -p $PROJECT_ID -l $REGION gs://$BUCKET_NAME
    gsutil versioning set on gs://$BUCKET_NAME
    echo "✅ Created Terraform state bucket"
else
    echo "✅ Terraform state bucket already exists"
fi

echo -e "${GREEN}Step 3: Store Secrets${NC}"
echo "Please provide your Elastic Cloud credentials:"
read -p "Elastic Cloud ID: " ELASTIC_CLOUD_ID
read -sp "Elastic API Key: " ELASTIC_API_KEY
echo ""

# Store secrets
echo -n "$ELASTIC_CLOUD_ID" | gcloud secrets create elastic-cloud-id \
    --data-file=- --replication-policy=automatic 2>/dev/null || \
    echo -n "$ELASTIC_CLOUD_ID" | gcloud secrets versions add elastic-cloud-id --data-file=-

echo -n "$ELASTIC_API_KEY" | gcloud secrets create elastic-api-key \
    --data-file=- --replication-policy=automatic 2>/dev/null || \
    echo -n "$ELASTIC_API_KEY" | gcloud secrets versions add elastic-api-key --data-file=-

echo "✅ Secrets stored"

echo -e "${GREEN}Step 4: Initialize Terraform${NC}"
cd terraform

# Create terraform.tfvars
cat > terraform.tfvars <<EOF
project_id     = "$PROJECT_ID"
project_number = "$PROJECT_NUMBER"
region         = "$REGION"
github_owner   = "your-github-username"
github_repo    = "devops-oracle"
EOF

terraform init
terraform plan
read -p "Apply Terraform configuration? (yes/no): " APPLY_TERRAFORM

if [ "$APPLY_TERRAFORM" == "yes" ]; then
    terraform apply -auto-approve
    echo "✅ Infrastructure created"
else
    echo "⚠️  Skipping Terraform apply"
fi

cd ..

echo -e "${GREEN}Step 5: Build and Deploy with Cloud Build${NC}"
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION=$REGION

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "Backend URL:"
gcloud run services describe devops-oracle-api --region=$REGION --format="value(status.url)"
echo ""
echo "Frontend URL:"
gcloud run services describe devops-oracle-frontend --region=$REGION --format="value(status.url)"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Update frontend/vite.config.js with the backend URL"
echo "2. Connect GitHub repository to Cloud Build"
echo "3. Push to main branch to trigger automatic deployment"