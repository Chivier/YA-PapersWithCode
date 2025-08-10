# YA-PapersWithCode Setup Guide

## Quick Start

This project consists of a Python FastAPI backend and a React frontend. Use the provided scripts to set up and run both components.

### Prerequisites

- **macOS** or **Linux** operating system
- **Python 3.8+** (backend will install `uv` if not present)
- **Node.js 16+** and **npm** (for frontend)

### Installation & Running

#### 1. Start the Backend

Open a terminal and run:
```bash
./start_backend.sh
```

This script will:
- ✅ Check and install `uv` (Python package manager) if needed
- ✅ Create a Python virtual environment
- ✅ Install all Python dependencies
- ✅ Download PapersWithCode data files (first run only)
- ✅ Initialize the SQLite database
- ✅ Start the API server on http://localhost:8000

#### 2. Start the Frontend

Open another terminal and run:
```bash
./start_frontend.sh
```

This script will:
- ✅ Check Node.js and npm installation
- ✅ Install npm dependencies
- ✅ Check if backend is running
- ✅ Start the React dev server on http://localhost:5173

### Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Stopping the Services

Press `Ctrl+C` in each terminal to stop the respective service.

## Production Deployment with Docker

This guide explains how to deploy YA-PapersWithCode to production using Docker and Nginx Proxy Manager.

### Prerequisites for Production

- Docker and Docker Compose installed
- Nginx Proxy Manager configured (or any reverse proxy)
- Domain name pointed to your server
- SSL certificate (can use Let's Encrypt)

### Deployment Steps

#### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/yourusername/YA-PapersWithCode.git
cd YA-PapersWithCode

# Copy production configuration
cp .env.production.example .env

# Edit the configuration
nano .env
```

**Important settings to update:**

```bash
# Core Settings
DEPLOYMENT_MODE=api_mode  # or 'local' for PASA models
SKIP_MODEL_DOWNLOAD=true  # Skip HuggingFace downloads if using OpenAI

# Domain
DOMAIN=papers-with-code.arcane-read.com
BACKEND_URL=https://papers-with-code.arcane-read.com
CORS_ORIGINS=https://papers-with-code.arcane-read.com

# OpenAI API (if using api_mode)
OPENAI_API_KEY=your-openai-api-key-here

# Security
SECRET_KEY=generate-a-secure-random-key-here
```

#### 2. Build and Start Services

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### 3. Initialize Database (First Time Only)

```bash
# Enter backend container
docker exec -it ya-pwc-backend bash

# Initialize database
python init_database.py

# Build embeddings for better search (optional but recommended)
python build_embeddings.py --datasets --papers

# Exit container
exit
```

#### 4. Configure Nginx Proxy Manager

In your Nginx Proxy Manager, create proxy hosts:

**For the main domain:**
- Domain: `papers-with-code.arcane-read.com`
- Forward to: `backend:8000` for `/api` paths
- Forward to: `frontend:3000` for `/` paths
- Enable SSL, Force SSL, HTTP/2

**Custom locations:**
- `/api` → `http://backend:8000`
- `/docs` → `http://backend:8000/docs`
- `/health` → `http://backend:8000/health`

### Port Configuration

The application supports flexible port configuration through environment variables:

```bash
# In your .env file
BACKEND_PORT=8000   # Backend API port
FRONTEND_PORT=3000  # Frontend port
REDIS_PORT=6379     # Redis cache port
```

Docker Compose will use these values automatically.

### Environment Variables

Key configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEPLOYMENT_MODE` | `local`, `api_mode`, or `model_only` | `api_mode` |
| `SKIP_MODEL_DOWNLOAD` | Skip downloading PASA models | `true` |
| `OPENAI_API_KEY` | OpenAI API key for AI search | Required for api_mode |
| `SECRET_KEY` | Secret key for security | **Must change!** |
| `CORS_ORIGINS` | Allowed CORS origins | Your domain |
| `BACKEND_PORT` | Backend API port | `8000` |
| `FRONTEND_PORT` | Frontend port | `3000` |

### Health Monitoring

```bash
# Check backend health
curl https://your-domain.com/api/health

# Check container status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Maintenance

#### Update Application

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

#### Backup Database

```bash
# Create backup
docker exec ya-pwc-backend sqlite3 paperswithcode.db ".backup /app/backup.db"

# Copy to host
docker cp ya-pwc-backend:/app/backup.db ./backups/backup-$(date +%Y%m%d).db
```

#### Clear Cache

```bash
# Clear Redis cache
docker exec ya-pwc-redis redis-cli FLUSHALL
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :8000

# Change port in .env if needed
BACKEND_PORT=8001
```

#### CORS Errors

1. Check `CORS_ORIGINS` in `.env` includes your domain
2. Restart backend: `docker-compose restart backend`

#### Database Issues

```bash
# Check if database exists
docker exec ya-pwc-backend ls -la paperswithcode.db

# Reinitialize if needed
docker exec ya-pwc-backend python init_database.py
```

#### Memory Issues with Embeddings

If using local mode and running out of memory:
1. Switch to `api_mode` with OpenAI
2. Or set `DEVICE=cpu` in `.env`
3. Or generate embeddings in smaller batches

### Backend Issues

1. **Port 8000 already in use**: The script will automatically try to stop the existing process.
2. **uv installation fails**: Install manually from https://github.com/astral-sh/uv
3. **Database errors**: Delete `paperswithcode.db` and `.initialized` files, then restart

### Frontend Issues

1. **Node.js not installed**: 
   - macOS: `brew install node`
   - Linux: `sudo apt install nodejs npm`
2. **Port 5173 already in use**: The script will automatically try to stop the existing process.
3. **Backend not running**: Start the backend first using `./start_backend.sh`

## Manual Setup (Alternative)

If the scripts don't work for your environment:

### Backend
```bash
cd data/ya-paperswithcode-database
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python init_database.py
python api_server.py
```

### Frontend
```bash
cd frontend/ya-paperswithcode
npm install
npm run dev
```

## Performance Optimization

1. **Enable Redis Cache**: Included in docker-compose
2. **Pre-build Embeddings**: Run `build_embeddings.py` after setup
3. **Use CDN**: Configure CDN for static assets
4. **Enable Compression**: Configure in your reverse proxy

## Security Recommendations

1. **Change Default Secrets**: Always change `SECRET_KEY` in production
2. **Use HTTPS**: Configure SSL in your reverse proxy
3. **Rate Limiting**: Configure in Nginx Proxy Manager
4. **Regular Updates**: Keep Docker images updated
5. **Backup Regularly**: Set up automated database backups

## Development Notes

- The backend uses SQLite for data storage
- Data files are downloaded from the official PapersWithCode repository
- The frontend is built with React, TypeScript, and Tailwind CSS
- Both services support hot-reloading for development
- Redis is used for caching in production

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review this guide
3. Open an issue on GitHub