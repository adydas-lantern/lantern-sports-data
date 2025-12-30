# NAIA Wrestling Standings API

REST API for querying NAIA wrestling conference standings data (2020-2025).

## Features

- ✅ **FastAPI** with automatic OpenAPI/Swagger documentation
- ✅ **152 schools** across all NAIA conferences
- ✅ **376 standing entries** from 2020-2025
- ✅ RESTful endpoints for schools, conferences, and standings
- ✅ Pagination support
- ✅ Case-insensitive partial matching
- ✅ Ready for Google Cloud Run deployment
- ✅ Docker containerized

## Production Deployment

**Service URL:** https://naia-wrestling-api-ez2te3dujq-uc.a.run.app

### Authentication

The production API uses **IAM-based authentication**. To access the API:

**Option 1: Using gcloud (authenticated users)**
```bash
# Get an identity token
TOKEN=$(gcloud auth print-identity-token)

# Make authenticated requests
curl -H "Authorization: Bearer $TOKEN" \
  https://naia-wrestling-api-ez2te3dujq-uc.a.run.app/api/v1/stats
```

**Option 2: Grant specific users access**
```bash
# Grant invoker role to a user
gcloud run services add-iam-policy-binding naia-wrestling-api \
  --region=us-central1 \
  --member="user:email@example.com" \
  --role="roles/run.invoker"
```

**Option 3: For public access (requires org policy changes)**
```bash
# Attempt to make public (may be blocked by organization policy)
gcloud run services add-iam-policy-binding naia-wrestling-api \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Available Endpoints

- **API Info:** `GET /`
- **Health Check:** `GET /health`
- **Swagger UI:** `GET /docs`
- **ReDoc:** `GET /redoc`
- **Schools:** `GET /api/v1/schools`
- **Conferences:** `GET /api/v1/conferences`
- **Standings by Year:** `GET /api/v1/standings/{year}`
- **Statistics:** `GET /api/v1/stats`

## Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r api/requirements.txt
```

2. **Run the API:**
```bash
uvicorn api.main:app --reload --port 8080
```

3. **Access the API:**
- API Root: http://localhost:8080
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

### Docker

1. **Build the image:**
```bash
docker build -t naia-wrestling-api .
```

2. **Run the container:**
```bash
docker run -p 8080:8080 naia-wrestling-api
```

3. **Access the API:**
http://localhost:8080/docs

## API Endpoints

### Root

```
GET /                    # API information
GET /health              # Health check
```

### Schools

```
GET /api/v1/schools                  # List all schools
GET /api/v1/schools/{name}           # Get specific school
```

**Query Parameters:**
- `skip` - Number of records to skip (pagination)
- `limit` - Maximum records to return (default: 100)
- `conference` - Filter by conference name

**Example:**
```bash
curl "http://localhost:8080/api/v1/schools?limit=5"
curl "http://localhost:8080/api/v1/schools/Grand View"
curl "http://localhost:8080/api/v1/schools?conference=Heart of America"
```

### Conferences

```
GET /api/v1/conferences                     # List all conferences
GET /api/v1/conferences/{name}              # Get specific conference
GET /api/v1/conferences/{name}/standings    # Get conference standings by year
```

**Example:**
```bash
curl "http://localhost:8080/api/v1/conferences"
curl "http://localhost:8080/api/v1/conferences/Heart"
curl "http://localhost:8080/api/v1/conferences/Heart/standings"
```

### Standings

```
GET /api/v1/standings/{year}                      # Get all standings for year
GET /api/v1/standings/{year}/{conference}         # Get standings for year + conference
```

**Query Parameters:**
- `conference` - Filter standings by conference

**Example:**
```bash
curl "http://localhost:8080/api/v1/standings/2024"
curl "http://localhost:8080/api/v1/standings/2024?conference=Appalachian"
curl "http://localhost:8080/api/v1/standings/2024/Heart"
```

### Statistics

```
GET /api/v1/stats        # Database statistics
```

**Example:**
```bash
curl "http://localhost:8080/api/v1/stats"
```

## Response Examples

### School Response

```json
{
  "name": "Grand View (Iowa) - Mens",
  "division": "NAIA",
  "conference": "Heart of America Athletic Conference",
  "placements": [
    {
      "year": 2020,
      "place": 1,
      "conference": "Heart of America Athletic Conference"
    },
    {
      "year": 2021,
      "place": 1,
      "conference": "Heart of America Athletic Conference"
    }
  ]
}
```

### Conference Response

```json
{
  "name": "Heart of America Athletic Conference",
  "schools": [
    "Grand View (Iowa) - Mens",
    "Missouri Valley College",
    "..."
  ],
  "years_active": [2020, 2021, 2022, 2023, 2024, 2025]
}
```

### Standings Response

```json
{
  "year": 2024,
  "conference": "Heart of America Athletic Conference",
  "standings": [
    {
      "year": 2024,
      "conference": "Heart of America Athletic Conference",
      "place": 1,
      "school": "Grand View (Iowa) - Mens"
    },
    {
      "year": 2024,
      "conference": "Heart of America Athletic Conference",
      "place": 2,
      "school": "Missouri Baptist University - Mens"
    }
  ]
}
```

## Google Cloud Platform Deployment

### Prerequisites

1. **Install Google Cloud SDK:**
```bash
# Mac
brew install --cask google-cloud-sdk

# Or download from:
# https://cloud.google.com/sdk/docs/install
```

2. **Authenticate:**
```bash
gcloud auth login
gcloud auth configure-docker
```

3. **Set your project:**
```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
```

### Deploy to Cloud Run

**Option 1: Using the deployment script**
```bash
./deploy_gcp.sh
```

**Option 2: Manual deployment**

1. **Build and push image:**
```bash
gcloud builds submit --tag gcr.io/${GCP_PROJECT_ID}/naia-wrestling-api
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy naia-wrestling-api \
  --image gcr.io/${GCP_PROJECT_ID}/naia-wrestling-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10
```

3. **Get service URL:**
```bash
gcloud run services describe naia-wrestling-api \
  --region us-central1 \
  --format 'value(status.url)'
```

### Cloud Run Configuration

**Recommended Settings:**
- **Memory**: 512 MB (sufficient for CSV data)
- **CPU**: 1 vCPU
- **Max Instances**: 10 (adjust based on expected traffic)
- **Timeout**: 60 seconds
- **Authentication**: Allow unauthenticated (for public API)

**Environment Variables:**
None required - uses CSV files bundled in container

### Cost Estimation

Cloud Run pricing (us-central1):
- **Free tier**: 2 million requests/month
- **Beyond free tier**: ~$0.40 per million requests
- **Memory**: $0.0000025/GB-second
- **CPU**: $0.00002400/vCPU-second

**Estimated monthly cost for moderate usage:**
- 100K requests/month: **$0-2**
- 1M requests/month: **$5-10**

## Architecture

```
┌─────────────────────────────────────────┐
│         Client Application              │
│    (Browser, Mobile App, Scripts)       │
└──────────────┬──────────────────────────┘
               │
               │ HTTPS
               ▼
┌─────────────────────────────────────────┐
│      Google Cloud Run Service           │
│  ┌───────────────────────────────────┐  │
│  │     FastAPI Application           │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │   REST API Endpoints        │  │  │
│  │  │   - /api/v1/schools         │  │  │
│  │  │   - /api/v1/conferences     │  │  │
│  │  │   - /api/v1/standings       │  │  │
│  │  └─────────────────────────────┘  │  │
│  │              │                     │  │
│  │              ▼                     │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │      Data Loader            │  │  │
│  │  └─────────────────────────────┘  │  │
│  │              │                     │  │
│  │              ▼                     │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │      CSV Files              │  │  │
│  │  │  - NAIA_results.csv         │  │  │
│  │  │  - Complete_Sorted.csv      │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Data Schema

### School Model
```python
{
  "name": str,              # School name
  "division": str,          # "NAIA"
  "conference": str,        # Conference name
  "placements": [           # List of placements
    {
      "year": int,          # 2020-2025
      "place": int,         # 1-10+
      "conference": str     # Conference at that time
    }
  ]
}
```

### Standing Model
```python
{
  "year": int,             # 2020-2025
  "conference": str,       # Conference name
  "place": int,            # Placement (1-10+)
  "school": str           # School name
}
```

### Conference Model
```python
{
  "name": str,            # Conference name
  "schools": [str],       # List of school names
  "years_active": [int]   # Years with data
}
```

## Development

### Project Structure
```
.
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── data_loader.py       # CSV data loading
│   └── requirements.txt     # API dependencies
├── NAIA_blank - NAIA_results.csv      # Main data
├── NAIA_Complete_Sorted.csv           # Sorted data
├── Dockerfile                          # Container definition
├── deploy_gcp.sh                       # Deployment script
└── API_README.md                       # This file
```

### Adding New Endpoints

1. **Define Pydantic model** in `api/models.py`
2. **Add data method** in `api/data_loader.py`
3. **Create endpoint** in `api/main.py`
4. **Test locally**
5. **Deploy**

### Testing

```bash
# Install dependencies
pip install -r api/requirements.txt

# Run tests (add pytest when needed)
pytest

# Test locally
uvicorn api.main:app --reload

# Test with curl
curl http://localhost:8080/health
```

## Monitoring

### Cloud Run Metrics

View metrics in GCP Console:
```
https://console.cloud.google.com/run/detail/{REGION}/{SERVICE}/metrics
```

**Key metrics:**
- Request count
- Request latency
- Container instance count
- CPU utilization
- Memory utilization

### Logs

View logs:
```bash
gcloud run services logs read naia-wrestling-api --region us-central1
```

Or in GCP Console:
```
https://console.cloud.google.com/run/detail/{REGION}/{SERVICE}/logs
```

## Security

### Authentication

Current setup allows unauthenticated access (public API).

**To add authentication:**

1. **API Keys:**
```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.get("/api/v1/schools")
async def get_schools(api_key: str = Depends(api_key_header)):
    # Validate API key
    pass
```

2. **OAuth 2.0:**
```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

3. **Cloud IAM:**
```bash
gcloud run deploy --no-allow-unauthenticated
```

### CORS

Current setup allows all origins. For production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Build Fails

**Issue**: Container build fails
```bash
gcloud builds submit --tag gcr.io/${PROJECT_ID}/naia-wrestling-api
```

**Solutions**:
1. Check Docker syntax: `docker build -t test .`
2. Verify CSV files exist
3. Check file paths in Dockerfile

### Deployment Fails

**Issue**: Cloud Run deployment fails

**Solutions**:
1. Enable required APIs:
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

2. Check quotas:
```bash
gcloud compute project-info describe --project=${PROJECT_ID}
```

### Data Not Loading

**Issue**: `/health` shows `data_loaded: false`

**Solutions**:
1. Check CSV file paths in container
2. Verify CSV files copied correctly
3. Check logs: `gcloud run services logs read`

### High Latency

**Issue**: API responses slow

**Solutions**:
1. Increase memory: `--memory 1Gi`
2. Increase CPU: `--cpu 2`
3. Enable keep-alive connections
4. Add caching layer (Redis/Memcache)

## Future Enhancements

- [ ] Add scraping endpoint (POST /api/v1/scrape)
- [ ] PostgreSQL/Cloud SQL backend
- [ ] Redis caching layer
- [ ] GraphQL API
- [ ] WebSocket support for real-time updates
- [ ] Admin dashboard
- [ ] Rate limiting
- [ ] API versioning (v2)
- [ ] Automated testing (pytest)
- [ ] CI/CD pipeline
- [ ] Terraform/IaC deployment

## License

Educational and research purposes. NAIA data belongs to the National Association of Intercollegiate Athletics.

## Support

For issues or questions:
- Open an issue on GitHub
- Check Swagger docs: `/docs`
- Review Cloud Run logs
