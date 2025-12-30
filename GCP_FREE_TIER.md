# GCP Free Tier Setup for NAIA Wrestling API

Complete guide to deploying the NAIA Wrestling API using Google Cloud Platform's **Always Free** tier.

## 🎁 GCP Free Tier Overview

Google Cloud offers two types of free usage:

### 1. **90-Day Free Trial**
- **$300 credit** to use within 90 days
- Access to all GCP services
- No automatic charges after trial ends (you must upgrade)

### 2. **Always Free Tier** (What we'll use)
- Permanently free (as long as you stay within limits)
- Includes Cloud Run, Cloud Storage, Cloud Build, and more
- Perfect for small projects and APIs

## 📊 Always Free Services for This Project

### Cloud Run (API Hosting)
```
✅ FREE MONTHLY ALLOCATION:
- 2 million requests
- 360,000 GB-seconds of memory
- 180,000 vCPU-seconds of compute time
- 1 GB network egress (North America)

CONFIGURATION FOR FREE TIER:
- Memory: 512 MB (our current setting)
- CPU: 1 vCPU (our current setting)
- Max instances: 10 (our current setting)
- Min instances: 0 (important - no always-on costs)
```

### Cloud Build (Docker Image Building)
```
✅ FREE MONTHLY ALLOCATION:
- 120 build-minutes per day
- 10 GB storage for build artifacts

OUR USAGE:
- ~2-3 minutes per build
- Triggered only on code push
- Well within free limits
```

### Container Registry (Image Storage)
```
✅ FREE MONTHLY ALLOCATION:
- 5 GB storage
- Unlimited egress to Cloud Run

OUR USAGE:
- ~200-300 MB per Docker image
- Can store ~15-20 versions
- Images deleted automatically by Cloud Build
```

### Cloud Storage (Future Use)
```
✅ FREE MONTHLY ALLOCATION:
- 5 GB standard storage
- 5,000 Class A operations
- 50,000 Class B operations

POTENTIAL USE:
- Store CSV files separately
- Backup data
- Logs storage
```

## 💰 Cost Estimate for This API

### Typical Monthly Usage (Free Tier)

**Low Traffic (10K requests/month):**
```
Requests: 10,000
Memory:   ~0.5 GB-seconds per request
CPU:      ~0.1 vCPU-seconds per request
Network:  ~10 MB

COST: $0.00 (well within free tier)
```

**Moderate Traffic (100K requests/month):**
```
Requests: 100,000
Memory:   ~50 GB-seconds
CPU:      ~10 vCPU-seconds
Network:  ~100 MB

COST: $0.00 (within free tier)
```

**Heavy Traffic (1M requests/month):**
```
Requests: 1,000,000
Memory:   ~500 GB-seconds
CPU:      ~100 vCPU-seconds
Network:  ~1 GB

COST: $0.00 (within free tier limits!)
```

**Beyond Free Tier (2M+ requests/month):**
```
Requests: 2,100,000 (100K over free tier)
Additional cost: ~$0.08
Memory cost: ~$0.05
Total: ~$0.15/month
```

### Break-Even Analysis

You can handle approximately:
- **2 million API requests per month** = FREE
- **5-10K requests per day** = FREE
- **200-400 requests per hour** = FREE

## 🚀 Setup Instructions (Free Tier)

### Step 1: Create GCP Account

1. **Go to:** https://cloud.google.com/free

2. **Sign up with:**
   - Google account (ady.das@lanternpartners.ai recommended)
   - Credit card (required but won't be charged unless you upgrade)

3. **Activate Free Trial:**
   - Get $300 credit for 90 days
   - After 90 days, drops to Always Free tier automatically

### Step 2: Create New Project

```bash
# Install gcloud CLI (if not installed)
# Mac:
brew install --cask google-cloud-sdk

# Or download: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Create project (choose a unique project ID)
export PROJECT_ID="lantern-sports-data"  # Change if needed
gcloud projects create $PROJECT_ID --name="Lantern Sports Data"

# Set as default
gcloud config set project $PROJECT_ID

# Link billing account (required even for free tier)
# Get billing account ID
gcloud billing accounts list

# Link billing (replace with your billing account ID)
gcloud billing projects link $PROJECT_ID \
  --billing-account=XXXXXX-XXXXXX-XXXXXX
```

### Step 3: Enable Required APIs (Free)

```bash
# Enable Cloud Run API (FREE)
gcloud services enable run.googleapis.com

# Enable Cloud Build API (FREE)
gcloud services enable cloudbuild.googleapis.com

# Enable Container Registry API (FREE)
gcloud services enable containerregistry.googleapis.com

# Enable Artifact Registry API (FREE - newer than Container Registry)
gcloud services enable artifactregistry.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled
```

### Step 4: Create Service Account for GitHub Actions

```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions Deployment" \
  --description="Service account for automated deployments"

# Get service account email
export SA_EMAIL="github-actions@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant minimum required permissions (FREE)
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.builder"

# Create service account key
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=$SA_EMAIL

# Display key (copy for GitHub)
cat ~/gcp-key.json

# IMPORTANT: Delete key file after copying to GitHub
rm ~/gcp-key.json
```

### Step 5: Configure GitHub Secrets

1. **Go to:** https://github.com/adydas-lantern/lantern-sports-data/settings/secrets/actions

2. **Add secrets:**

   **GCP_PROJECT_ID**
   ```
   Value: lantern-sports-data (your project ID)
   ```

   **GCP_SA_KEY**
   ```
   Value: (paste entire JSON from gcp-key.json)
   ```

### Step 6: Deploy via GitHub Actions

```bash
# Trigger deployment by pushing to main
cd /path/to/wrestlingStandingScreenScrape
git add .
git commit -m "Trigger GCP deployment"
git push origin main

# Or manually trigger workflow
# Go to: https://github.com/adydas-lantern/lantern-sports-data/actions
# Click: "Deploy to GCP Cloud Run (Production)"
# Click: "Run workflow"
```

### Step 7: Monitor Deployment

```bash
# Watch deployment in terminal
gcloud run services list --platform=managed

# View logs
gcloud run services logs read naia-wrestling-api \
  --region=us-central1 \
  --limit=50

# Get service URL
gcloud run services describe naia-wrestling-api \
  --region=us-central1 \
  --format='value(status.url)'
```

## 🎯 Optimize for Free Tier

### Current Configuration (Already Optimized)

```yaml
# In .github/workflows/deploy-production.yml
--memory 512Mi           # ✅ 512 MB (optimal for free tier)
--cpu 1                  # ✅ 1 vCPU (optimal)
--max-instances 10       # ✅ Prevents runaway costs
--min-instances 0        # ✅ CRITICAL: No always-on costs
--timeout 60             # ✅ 60 seconds (reasonable)
```

### To Stay 100% Free

**DO:**
- ✅ Keep `min-instances: 0` (no always-on costs)
- ✅ Use 512 MB memory (optimal)
- ✅ Monitor usage: https://console.cloud.google.com/run
- ✅ Set budget alerts (see below)
- ✅ Delete old container images periodically

**DON'T:**
- ❌ Set `min-instances > 0` (charges even when idle)
- ❌ Increase memory beyond 512 MB (wastes free quota)
- ❌ Deploy to expensive regions (use us-central1)
- ❌ Leave development/staging services running 24/7

## 📊 Set Up Budget Alerts (Free Protection)

```bash
# Create budget alert (warns before charges)
gcloud billing budgets create \
  --billing-account=XXXXXX-XXXXXX-XXXXXX \
  --display-name="Free Tier Alert" \
  --budget-amount=1 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100

# You'll get emails at 50%, 90%, and 100% of $1 budget
```

Or via Console:
1. Go to: https://console.cloud.google.com/billing/budgets
2. Create Budget:
   - Name: "Free Tier Protection"
   - Budget: $1.00
   - Alerts: 50%, 90%, 100%
   - Email: ady.das@lanternpartners.ai

## 📈 Monitor Usage (Stay Within Free Tier)

### Check Current Usage

```bash
# Cloud Run metrics
gcloud run services describe naia-wrestling-api \
  --region=us-central1 \
  --format='value(status.url)'

# View in console
# Go to: https://console.cloud.google.com/run
# Click on service → Metrics tab
```

### Monthly Quota Check

1. **Go to:** https://console.cloud.google.com/apis/dashboard
2. **View:** Quotas & System Limits
3. **Check:** Cloud Run API quotas

### Cost Explorer

1. **Go to:** https://console.cloud.google.com/billing
2. **Click:** "Reports"
3. **View:** Daily/monthly costs (should be $0.00)

## 🔧 Troubleshooting Free Tier

### Issue: "Billing account required"

**Solution:**
```bash
# Link billing account (even for free tier)
gcloud billing accounts list
gcloud billing projects link $PROJECT_ID \
  --billing-account=XXXXXX-XXXXXX-XXXXXX
```

### Issue: "Quota exceeded"

**Solution:**
- Check you haven't exceeded 2M requests/month
- Wait until next month for quota reset
- Or upgrade to paid tier (very cheap beyond free tier)

### Issue: "Unexpected charges"

**Possible causes:**
1. `min-instances > 0` (change to 0)
2. Multiple services running (delete unused)
3. Old container images (clean up)

**Fix:**
```bash
# Set min instances to 0
gcloud run services update naia-wrestling-api \
  --region=us-central1 \
  --min-instances=0

# Delete old images
gcloud container images list
gcloud container images delete [IMAGE_URL]
```

## 💡 Tips to Maximize Free Tier

### 1. Use Regions Wisely
```bash
# FREE egress within same region
# us-central1 (Iowa) = cheapest region
--region=us-central1
```

### 2. Implement Caching
```python
# Add caching to reduce compute time
from functools import lru_cache

@lru_cache(maxsize=128)
def get_schools():
    # Expensive operation cached
    return data_loader.get_all_schools()
```

### 3. Optimize Docker Image
```dockerfile
# Use slim base image (faster builds, less storage)
FROM python:3.11-slim

# Multi-stage build (smaller image)
# Clean up in same layer
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
```

### 4. Clean Up Regularly
```bash
# Delete old container images (>30 days)
gcloud container images list-tags gcr.io/$PROJECT_ID/naia-wrestling-api \
  --filter="timestamp.datetime < -P30D" \
  --format="get(digest)" | \
  xargs -I {} gcloud container images delete \
  "gcr.io/$PROJECT_ID/naia-wrestling-api@{}" --quiet
```

## 📝 Summary: Completely Free Setup

**To stay 100% free:**
1. ✅ Use Always Free tier (not trial credits)
2. ✅ Keep `min-instances: 0`
3. ✅ Stay under 2M requests/month
4. ✅ Use us-central1 region
5. ✅ Set budget alerts at $1
6. ✅ Monitor usage monthly
7. ✅ Clean up old images

**Expected cost: $0.00/month** for typical API usage (up to 2M requests)

## 🚀 Quick Start Command

```bash
# Complete free tier setup in one go
export PROJECT_ID="lantern-sports-data"

gcloud projects create $PROJECT_ID --name="Lantern Sports Data"
gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com

# Add GitHub secrets
# Then push to GitHub - deployment happens automatically!
```

## 📞 Support

- **GCP Free Tier Docs:** https://cloud.google.com/free/docs/free-cloud-features
- **Cloud Run Pricing:** https://cloud.google.com/run/pricing
- **Budget Alerts:** https://cloud.google.com/billing/docs/how-to/budgets
- **Billing Support:** https://console.cloud.google.com/billing

---

**Bottom Line:** This API can run completely free on GCP for up to **2 million requests per month** using the Always Free tier!
