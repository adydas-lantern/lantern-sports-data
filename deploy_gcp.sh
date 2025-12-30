#!/bin/bash
# Deploy NAIA Wrestling API to Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="naia-wrestling-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "=========================================="
echo "NAIA Wrestling API - GCP Deployment"
echo "=========================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "=========================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Check if logged in
echo "Checking authentication..."
gcloud auth list

# Set project
echo "Setting project..."
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push container image
echo "Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --timeout 60 \
    --port 8080

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')

echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo "Service URL: ${SERVICE_URL}"
echo "API Docs: ${SERVICE_URL}/docs"
echo "Health Check: ${SERVICE_URL}/health"
echo "=========================================="
echo ""
echo "Test the API:"
echo "  curl ${SERVICE_URL}/health"
echo "  curl ${SERVICE_URL}/api/v1/schools?limit=5"
echo "=========================================="
