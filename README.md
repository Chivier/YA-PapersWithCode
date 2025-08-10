# YA-PapersWithCode

> **Yet Another Papers With Code** - A modern recreation of the Papers With Code platform

> [!IMPORTANT]
> **🚀 Seeking Compute Sponsors for AI Agent Search**
> 
> The advanced AI Agent Search feature requires significant computational resources. We are actively seeking compute sponsors to enable this feature on the public web version.
> 
> **Current Status:**
> - 🌐 **Web Version**: Agent Search is temporarily unavailable due to compute limitations
> - 💻 **Self-Hosted**: Full Agent Search functionality is available for local deployment
> - 🤝 **Sponsorship Needed**: GPU compute resources or cloud credits to enable public access
> 
> If you or your organization can provide compute resources, please open an issue with the label `compute-sponsorship`. Your support will enable free AI-powered search for the entire research community.
> 
> **Note**: Users can deploy their own instance with full Agent Search capabilities by following the [deployment guide](#-deployment).

A comprehensive machine learning research platform that provides access to academic papers, datasets, methods, and state-of-the-art benchmarks. This project aims to restore and enhance the functionality of the original Papers With Code website using modern web technologies.

## 🌟 Overview

YA-PapersWithCode is a full-stack application that recreates the popular Papers With Code platform, which provided a valuable service to the ML research community before its discontinuation. The project consists of:

- **Modern React Frontend** - Built with TypeScript, Tailwind CSS, and shadcn/ui components
- **FastAPI Backend** - Powered by SQLite database with full-text search capabilities
- **AI-Powered Search** - Advanced search agents for intelligent paper and dataset discovery
- **Data Pipeline** - Automated downloading and processing of research data

## ✨ Key Features

### 🔍 Intelligent Search
- **Multi-modal Search**: Papers, datasets, methods, and benchmarks
- **AI-Powered Agents**: Advanced search expansion using semantic understanding
- **Full-text Search**: SQLite-based search with optimization for research content
- **Smart Filtering**: Dynamic filters for modalities, tasks, languages, and more

### 📚 Research Content
- **Papers**: 50,000+ research papers with abstracts and code links
- **Datasets**: Comprehensive dataset catalog with 39 modalities and 500+ tasks
- **Methods**: Organized ML methods across domains (CV, NLP, RL, Audio)
- **Benchmarks**: State-of-the-art leaderboards and evaluation results

### 🎨 Modern Interface
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Real-time Filtering**: Instant search results with dynamic filters
- **Beautiful UI**: Modern design inspired by shadcn/ui components
- **Dark/Light Mode**: Adaptive theming for better user experience

### 🔧 Developer Features
- **RESTful API**: Comprehensive API with interactive documentation
- **Data Export**: JSON/CSV export functionality for research datasets
- **Extensible Architecture**: Modular design for easy feature additions
- **Docker Support**: Containerized deployment options

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (backend)
- **Node.js 16+** and **npm** (frontend)
- **Git** for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/YA-PapersWithCode.git
   cd YA-PapersWithCode
   ```

2. **Start the backend** (Terminal 1)
   ```bash
   ./start_backend.sh
   ```
   This will:
   - Install Python dependencies using `uv`
   - Download PapersWithCode data (first run only)
   - Initialize SQLite database
   - Start API server on http://localhost:8000

3. **Start the frontend** (Terminal 2)
   ```bash
   ./start_frontend.sh
   ```
   This will:
   - Install npm dependencies
   - Start React dev server on http://localhost:5173

4. **Access the application**
   - **Frontend**: http://localhost:5173
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
YA-PapersWithCode/
├── frontend/ya-paperswithcode/     # React frontend application
│   ├── src/
│   │   ├── components/             # UI components
│   │   │   ├── layout/            # Header, Footer, Layout
│   │   │   ├── papers/            # Paper-related components
│   │   │   ├── datasets/          # Dataset components
│   │   │   ├── methods/           # Method components
│   │   │   ├── search/            # Search components
│   │   │   └── ui/                # shadcn/ui base components
│   │   ├── pages/                 # Page components
│   │   ├── lib/                   # Utilities and API client
│   │   └── types/                 # TypeScript definitions
│   └── package.json               # Frontend dependencies
│
├── data/ya-paperswithcode-database/ # Backend API and database
│   ├── agent-search/              # AI search agents
│   │   ├── paper_search.py        # Paper search agent
│   │   ├── dataset_search.py      # Dataset search agent
│   │   ├── manager.py             # Search orchestration
│   │   └── config.json            # Agent configuration
│   ├── api_server.py              # FastAPI server
│   ├── models.py                  # Database models
│   ├── semantic_search.py         # Search functionality
│   └── schema.sql                 # Database schema
│
├── data/download_scripts/         # Data acquisition
│   ├── download.py                # Data downloader
│   └── README.md                  # Download documentation
│
├── start_backend.sh               # Backend startup script
├── start_frontend.sh              # Frontend startup script
└── requirements.txt               # Python dependencies
```

## 🔌 API Documentation

The backend provides a comprehensive RESTful API with the following endpoints:

### Papers
- `GET /api/v1/papers` - List papers with pagination
- `GET /api/v1/papers/{paper_id}` - Get specific paper
- `GET /api/v1/papers/arxiv/{arxiv_id}` - Get paper by arXiv ID
- `GET /api/v1/search?q={query}` - Full-text search

### Datasets & Methods
- `GET /api/v1/datasets` - List datasets with filtering
- `GET /api/v1/methods` - List ML methods
- `GET /api/v1/tasks` - List research tasks
- `GET /api/v1/evaluations` - Get benchmark results

### AI Search
- `POST /api/v1/ai-search` - Advanced AI-powered search
- `POST /api/v1/agent-search` - Multi-agent search orchestration

### Utilities
- `GET /api/v1/statistics` - Database statistics
- `GET /api/v1/export/{format}` - Data export (JSON/CSV)

Visit http://localhost:8000/docs for interactive API documentation.

## 🧠 AI Search Agents

The project includes sophisticated AI search agents that provide intelligent research discovery:

### Paper Search Agent
- **Multi-layer Expansion**: Discovers related papers through citation networks
- **Semantic Understanding**: Goes beyond keyword matching
- **Research Graph Traversal**: Explores connections between papers
- **Quality Ranking**: Prioritizes high-impact research

### Dataset Search Agent  
- **Task-aware Search**: Understands research task requirements
- **Modality Matching**: Finds datasets by data type (text, image, audio, etc.)
- **Domain-specific Filtering**: Specialized search for different ML domains
- **Compatibility Assessment**: Evaluates dataset suitability for specific tasks

### Search Manager
- **Agent Orchestration**: Coordinates multiple search agents
- **Query Understanding**: Automatically selects appropriate search strategies
- **Result Fusion**: Combines results from multiple agents
- **Performance Optimization**: Balances accuracy and response time

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **shadcn/ui** component library
- **React Router** for navigation
- **Axios** for API communication
- **React Query** for data fetching

### Backend
- **FastAPI** web framework
- **SQLite** database with FTS
- **Pydantic** for data validation
- **Uvicorn** ASGI server
- **Asyncio** for concurrent operations

### Data & Search
- **Full-text Search** with SQLite FTS
- **Semantic Search** capabilities
- **AI Search Agents** for intelligent discovery
- **Data Pipeline** for automated updates

## 📊 Data Sources

The project uses data from the official [PapersWithCode Data Repository](https://github.com/paperswithcode/paperswithcode-data):

- **papers-with-abstracts.json.gz** - 50,000+ research papers
- **links-between-papers-and-code.json.gz** - Code implementation links
- **evaluation-tables.json.gz** - Benchmark results
- **methods.json.gz** - ML methods and techniques
- **datasets.json.gz** - Research datasets catalog

Data is automatically downloaded and processed during the initial setup.

## 🚢 Deployment

```bash
cp .env.template .env

# Update .env manually

# Build backend
./start_backend.sh
# Build frontend
./start_frontend.sh
```


## 📝 TODO

- [ ] Implement AI agent for paper search.
- [ ] Provide modular agent search, allowing users to design their own search strategies.
- [ ] Provide Docker deployment.
- [ ] Fetch images for datasets.
- [ ] Integrate Hugging Face daily papers to the frontend (jump to [Hugging Face link](https://huggingface.co/papers)).
- [ ] Provide SOTA API, find SOTAs for datasets (next version, just like paperswithcode in [sota-extractor](https://github.com/paperswithcode/sota-extractor)).
- [ ] Use NocoDB + PostgreSQL to replace SQLite.
- [ ] Improve agent search ability.
- [ ] Use Redis to improve performance.

## 🤝 Contributing

We welcome contributions to improve YA-PapersWithCode! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Development Guidelines
- Follow TypeScript best practices
- Write comprehensive tests
- Update documentation for new features
- Ensure responsive design for frontend changes
- Follow REST API conventions for backend changes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The data from PapersWithCode is available under the Creative Commons Attribution-ShareAlike 4.0 International License (CC-BY-SA 4.0).

## 🙏 Acknowledgments

- [Papers With Code](https://github.com/paperswithcode) for their invaluable data and platform.
- [shadcn/ui](https://ui.shadcn.com/) for the beautiful and functional UI components.
- [Pasa](https://github.com/bytedance/pasa) by ByteDance for insights into advanced search architecture.
- [cline](https://github.com/cline/cline) for inspiration in developer tooling.
- The ML research community for their continuous contributions to open science.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/YA-PapersWithCode/issues) page
2. Review the [Setup Guide](SETUP.md) for troubleshooting
3. Create a new issue with detailed information
