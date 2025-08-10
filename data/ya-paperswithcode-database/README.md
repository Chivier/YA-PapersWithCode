# PapersWithCode Database & AI Search System

A comprehensive database and API server for PapersWithCode data with advanced AI-powered search capabilities.

> [!IMPORTANT]
> **🚀 Seeking Compute Sponsors**
> 
> The AI Agent Search feature requires significant computational resources to deliver optimal performance. We are actively seeking compute sponsors to help scale this service and make it freely available to the research community.
> 
> If you or your organization can provide GPU compute resources or cloud credits, please reach out to us. Your support will enable:
> - Faster search response times
> - Support for more concurrent users
> - Enhanced model capabilities
> - Continued free access for researchers worldwide
> 
> **Contact us**: Open an issue with the label `compute-sponsorship` or reach out directly through GitHub discussions.

## 🚀 Features

### Core Features
- **SQLite Database**: Optimized schema with full-text search capabilities
- **FastAPI Server**: High-performance REST API with auto-documentation
- **AI-Powered Search**: Advanced agent-based search using PASA models or OpenAI
- **Semantic Search**: Vector similarity search using embeddings
- **Multi-layer Search**: Automatic paper expansion and related content discovery

### Search Capabilities
- **Normal Search**: Traditional SQL-based full-text search
- **Agent Search**: AI-powered search with query understanding and expansion
- **Semantic Search**: Embedding-based similarity search
- **Hybrid Search**: Combines multiple search strategies for best results

### Data Resources
- **Papers**: 500K+ ML papers with abstracts and metadata
- **Datasets**: 15K+ datasets with descriptions and characteristics
- **Methods**: ML algorithms and techniques
- **Repositories**: Code implementations with GitHub links
- **Evaluation Results**: Benchmark scores and comparisons
- **Tasks**: Research problems and challenges

## 📦 Installation

### Quick Start
```bash
# Use the automated setup script
bash start_backend.sh
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Or using uv (recommended)
uv pip install -r requirements.txt
```

## 🔧 Configuration

### Deployment Modes

The system supports three deployment modes:

1. **Local Mode** (Default)
   - Uses local PASA models for AI search
   - Full database functionality
   - No external API dependencies

2. **API Mode**
   - Uses OpenAI GPT-5-mini for AI search
   - Requires OpenAI API key
   - Lower hardware requirements

3. **Model Only Mode**
   - Only AI model services
   - No database functionality
   - For dedicated model serving

### Configuration Files

```bash
# For local deployment
cp .env.template .env

# For OpenAI deployment
cp .env.openai.example .env

# Edit .env with your settings
```

## 🗄️ Database Setup

### 1. Download Data
```bash
# Data files will be downloaded automatically by start_backend.sh
# Or manually download:
curl -L -o papers-with-abstracts.json.gz https://production-media.paperswithcode.com/about/papers-with-abstracts.json.gz
gunzip papers-with-abstracts.json.gz
```

### 2. Initialize Database
```bash
python init_database.py
```

### 3. Build Embeddings (Optional but Recommended)
```bash
# Pre-build embeddings for faster semantic search
python build_embeddings.py --datasets --papers
```

## 🚀 Starting the Server

### Using the Startup Script (Recommended)
```bash
bash start_backend.sh
# Select deployment mode when prompted
```

### Manual Start
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the API server
python api_server.py
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Papers
- `GET /api/v1/papers` - List papers with pagination
- `GET /api/v1/papers/{paper_id}` - Get specific paper
- `GET /api/v1/papers/arxiv/{arxiv_id}` - Get paper by arXiv ID
- `POST /api/v1/papers/search/agent` - AI-powered paper search
- `GET /api/v1/search?q={query}` - Full-text search

### Datasets
- `GET /api/v1/datasets` - List datasets
- `GET /api/v1/datasets/{dataset_id}` - Get specific dataset
- `POST /api/v1/datasets/search/agent` - AI-powered dataset search
- `GET /api/v1/datasets/search?q={query}` - Dataset search

### Other Resources
- `GET /api/v1/repositories` - List code repositories
- `GET /api/v1/methods` - List methods
- `GET /api/v1/tasks` - List all tasks
- `GET /api/v1/evaluations` - Get evaluation results
- `GET /api/v1/statistics` - Database statistics

### Interactive Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

## 🤖 AI Agent Search

### How It Works
1. **Query Understanding**: AI analyzes the search query
2. **Initial Search**: Finds relevant papers/datasets
3. **Expansion**: Discovers related content
4. **Ranking**: Sorts results by relevance
5. **Filtering**: Applies user-specified filters

### Example Usage

#### Search for Papers
```bash
# AI-powered search
curl -X POST "http://localhost:8000/api/v1/papers/search/agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "transformer models for computer vision", "limit": 10}'

# Traditional search
curl "http://localhost:8000/api/v1/search?q=transformer"
```

#### Search for Datasets
```bash
# Find MNIST-related datasets
curl -X POST "http://localhost:8000/api/v1/datasets/search/agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "mnist related", "limit": 5}'

# Find image classification datasets
curl -X POST "http://localhost:8000/api/v1/datasets/search/agent" \
  -H "Content-Type: application/json" \
  -d '{"query": "image classification dataset", "limit": 10}'
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
cd test
python test_api_comprehensive.py

# Test frontend integration
python test_frontend_integration.py

# Test agent search
python test_agent_search.py
```

## 📊 Database Schema

### Main Tables
- `papers` - Research papers with abstracts
- `datasets` - ML datasets with metadata
- `repositories` - Code implementations
- `methods` - ML methods and algorithms
- `evaluation_results` - Benchmark results
- `tasks` - Research tasks/problems
- `paper_tasks` - Many-to-many relationship

### Indexes
- Full-text search on papers and datasets
- B-tree indexes on dates, IDs, and foreign keys
- Optimized for common query patterns

## 🔄 Updates and Maintenance

### Update Data
```bash
# Re-download latest data
rm *.json
bash start_backend.sh
# Select option to download fresh data
```

### Rebuild Embeddings
```bash
# Rebuild after data updates
rm -rf embeddings/
python build_embeddings.py --datasets --papers
```

### Clear Cache
```bash
# Clear API response cache
rm -rf cache/
```

## 🛠️ Troubleshooting

### Common Issues

1. **GPU Memory Issues**
   - Solution: Use CPU mode by setting `DEVICE=cpu` in .env
   - Or use OpenAI API mode which doesn't require GPU

2. **Missing Dependencies**
   ```bash
   uv pip install numpy faiss-cpu sentence-transformers
   ```

3. **Database Locked**
   - Stop all running instances
   - Check for zombie processes: `ps aux | grep python`

4. **Empty Search Results**
   - Ensure embeddings are built: `python build_embeddings.py`
   - Check data is loaded: `python -c "import sqlite3; conn=sqlite3.connect('paperswithcode.db'); print(conn.execute('SELECT COUNT(*) FROM papers').fetchone())"`

## 🚀 Performance Tips

1. **Pre-build Embeddings**: Always run `build_embeddings.py` after setup
2. **Use Caching**: Enable `ENABLE_CACHE=true` in .env
3. **Optimize Batch Size**: Adjust `EMBEDDING_BATCH_SIZE` based on RAM
4. **Use SSD Storage**: Place database on SSD for faster queries
5. **Limit Results**: Use reasonable `limit` values in searches

## 📝 Environment Variables

Key configuration options in `.env`:

```bash
# Deployment mode
DEPLOYMENT_MODE=local|api_mode|model_only

# For OpenAI mode
OPENAI_API_KEY=your-key-here
MODEL_NAME=gpt-5-mini-2025-08-07
EMBEDDING_MODEL=text-embedding-3-small

# Performance
MAX_SEARCH_RESULTS=50
CACHE_TTL=3600
ENABLE_CACHE=true

# Server
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

## 📈 Cost Optimization (OpenAI Mode)

When using OpenAI API:
- **GPT-5-mini**: ~$0.10/1M input, $0.40/1M output tokens
- **text-embedding-3-small**: $0.02/1M tokens
- **Estimated cost**: < $0.001 per search

Tips:
1. Enable aggressive caching
2. Use batch embeddings
3. Set appropriate token limits
4. Use temperature=0 for deterministic results

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project uses publicly available PapersWithCode data. Please refer to the original data license and attribution requirements.

## 🆘 Support

For issues or questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review test files in `/test` directory
3. Check API documentation at `http://localhost:8000/docs`
4. Open an issue on GitHub