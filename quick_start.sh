#!/bin/bash

echo "🚀 DevOps Oracle - Quick Start"
echo "================================"

# Step 1: Python environment
echo "📦 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install elasticsearch google-cloud-aiplatform google-cloud-bigquery \
    langchain langgraph fastapi uvicorn python-dotenv vertexai

# Step 2: Generate sample data
echo "📝 Generating sample data..."
python generate_sample_data.py

# Step 3: Create Elasticsearch index
echo "🔍 Creating Elasticsearch index..."
python elasticsearch_setup.py

# Step 4: Ingest data
echo "📥 Ingesting data with embeddings..."
python ingest_data.py

echo "✅ Setup complete! Ready to build the API and frontend."