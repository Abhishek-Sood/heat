# 🏥 HEAT - Healthcare AI Clinical Assistant

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![React](https://img.shields.io/badge/react-18.2-61dafb.svg)
![FastAPI](https://img.shields.io/badge/fastapi-latest-009688.svg)

**An intelligent, production-ready clinical assistant powered by LangGraph multi-agent orchestration, RAG pipelines, and modern LLMs.**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Deployment](#-deployment)

</div>

---

## ⚠️ Medical Disclaimer

> **This tool is for clinical decision support only. It does NOT provide final diagnoses or treatment decisions. All outputs require validation by a licensed healthcare professional. Never use this system as a substitute for professional medical judgment.**

---

## 🌟 Features

### Multi-Agent AI System
- **LangGraph Orchestrator** - Intelligent query routing and agent-to-agent (A2A) communication
- **Patient Context Agent** - Retrieves comprehensive patient data (labs, vitals, medications, history)
- **Text-to-SQL Agent** - Natural language to database queries with schema awareness
- **PubMed RAG Agent** - Evidence-based answers from medical literature using ChromaDB
- **Medication Recommendation Agent** - Combines patient data + research for treatment suggestions
- **Response Formatter Agent** - Converts technical outputs into human-friendly responses

### Clinical Capabilities
- 🔬 **Lab Results Analysis** - View, upload, and interpret laboratory results
- 💊 **Medication Management** - Track prescriptions, dosages, and schedules
- 📊 **Vital Signs Monitoring** - Real-time vitals tracking with abnormal value alerts
- 📋 **Patient Records** - Complete medical history at your fingertips
- 🚨 **Smart Alerts** - Automatic notifications for critical findings
- 💬 **AI Chat Interface** - Natural language queries about patients and medical topics

### Security & Safety
- 🔐 **JWT Authentication** - Secure user sessions with access/refresh tokens
- 🛡️ **Data Isolation** - User-scoped patient data (doctors only see their patients)
- 🚫 **Guardrails** - Built-in protections against harmful outputs
- 📝 **Audit Logging** - Complete agent activity traceability

### Technical Highlights
- **Model Context Protocol (MCP)** - Controlled database access layer
- **ChromaDB Vector Store** - Fast semantic search over medical literature
- **Groq LLM Integration** - High-performance inference with Llama 3.1
- **Alembic Migrations** - Version-controlled database schema
- **Docker Deployment** - One-command production setup
- **Render Blueprint** - Cloud deployment ready

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React + Vite)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Patient List│  │ Lab Results │  │  Chat Panel │  │ Auth (Login/Signup) │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ REST API
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                           BACKEND (FastAPI)                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    LangGraph Orchestrator                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │   │
│  │  │ Patient  │ │ Text-to- │ │ PubMed   │ │ Medication│ │ Response   │  │   │
│  │  │ Context  │ │ SQL      │ │ RAG      │ │ Recommend │ │ Formatter  │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │  MCP Client    │  │  RAG Pipeline    │  │  API Endpoints               │ │
│  │  (DB Control)  │  │  (ChromaDB)      │  │  /api/llm, /api/patients...  │ │
│  └────────────────┘  └──────────────────┘  └──────────────────────────────┘ │
└──────────┬────────────────────┬─────────────────────────┬───────────────────┘
           │                    │                         │
     ┌─────▼─────┐       ┌──────▼──────┐          ┌───────▼───────┐
     │ PostgreSQL │       │  ChromaDB   │          │   Groq API    │
     │ (Patient   │       │  (PubMed    │          │   (Llama 3.1) │
     │  Data)     │       │   Vectors)  │          │               │
     └────────────┘       └─────────────┘          └───────────────┘
```

### Agent Communication Flow

```
User Query → Classifier → Route Decision
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
   Patient Context      Text-to-SQL          PubMed RAG
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                   Response Formatter
                              │
                              ▼
                    Natural Language Response
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- Groq API Key ([Get one free](https://console.groq.com))

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/heat-clinical-assistant.git
cd heat-clinical-assistant

# Create environment file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Launch all services
docker-compose up --build

# Access:
# - Backend API: http://localhost:8000
# - Frontend:    http://localhost:8501
# - API Docs:    http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit ../.env with your configuration

# Run database migrations
alembic upgrade head

# Start MCP Database Server (in separate terminal)
python -m app.mcp.db_server

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:5173
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Database
POSTGRES_USER=heat_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=heat
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql://heat_user:your_secure_password@localhost:5432/heat

# LLM Configuration
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.1-8b-instant

# Authentication
SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# MCP Server
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=9000

# ChromaDB
CHROMA_DB_PATH=./backend/app/rag/chroma_data

# Application
PROJECT_NAME=HEAT Clinical Assistant
VERSION=1.0.0
API_PREFIX=/api
```

---

## 📚 API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/signup` | POST | Register new user |
| `/api/auth/login` | POST | Get access token |
| `/api/auth/refresh` | POST | Refresh access token |

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/llm/query` | POST | AI-powered query (main chat endpoint) |
| `/api/patients` | GET | List all patients (user-scoped) |
| `/api/patients/{id}` | GET | Get patient details |
| `/api/patients/{id}/lab-results` | GET | Get patient lab results |
| `/api/rag/search` | POST | Search medical literature |
| `/api/diagnose` | POST | Get diagnostic suggestions |
| `/api/recommend-treatment` | POST | Get treatment recommendations |

### Example: AI Chat Query

```bash
curl -X POST http://localhost:8000/api/llm/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest glucose levels for patient 1?",
    "patient_id": 1
  }'
```

**Response:**
```json
{
  "response": "Patient John Doe's most recent glucose test from January 15, 2024 shows a level of 105 mg/dL, which is within normal fasting range (70-100 mg/dL).",
  "agents_used": ["patient_context", "text_to_sql", "response_formatter"],
  "has_research_context": false,
  "source": "groq"
}
```

---

## 🗄️ Database Schema

```sql
-- Core patient data
patients (id, name, dob, gender, contact, address, user_id, created_at, updated_at)
lab_results (id, patient_id, user_id, timestamp, test_name, result, unit, reference_range)
vitals (id, patient_id, user_id, timestamp, type, value, unit)
medications (id, patient_id, user_id, name, dosage, frequency, start_date, end_date)
reports (id, patient_id, user_id, content, created_at)
alerts (id, patient_id, user_id, message, severity, created_at, resolved)

-- Conversations
conversations (id, patient_id, user_id, title, created_at)
messages (id, conversation_id, role, content, timestamp)

-- Authentication
users (id, username, email, password_hash, medical_license_id, is_active, created_at)
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=backend/app --cov-report=html

# Run specific test file
pytest tests/backend/test_agent_system.py -v

# Run specific test
pytest tests/backend/test_api.py::test_health_endpoint -v
```

### Test Categories
- `test_api.py` - API endpoint tests
- `test_agent_system.py` - Multi-agent orchestration tests
- `test_text_to_sql.py` - SQL generation tests
- `test_rag_ingestion.py` - RAG pipeline tests
- `test_patient_context.py` - Patient data retrieval tests

---

## ☁️ Deployment

### Render (Recommended)

The project includes a `render.yaml` Blueprint for one-click deployment:

1. Push code to GitHub/GitLab
2. Create a new Blueprint on [Render Dashboard](https://dashboard.render.com)
3. Connect your repository
4. Set `GROQ_API_KEY` in Render's environment variables
5. Click **Apply**

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### Manual Production Checklist

- [ ] Set strong `SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Configure PostgreSQL with proper credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for your frontend domain
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy for database

---

## 📁 Project Structure

```
heat-clinical-assistant/
├── backend/
│   ├── app/
│   │   ├── agents/              # AI agents
│   │   │   ├── langgraph_orchestrator.py
│   │   │   ├── patient_context_agent.py
│   │   │   ├── text_to_sql_agent.py
│   │   │   ├── pubmed_rag_agent.py
│   │   │   ├── medication_recommendation_agent.py
│   │   │   └── response_formatter_agent.py
│   │   ├── api/endpoints/       # REST API routes
│   │   ├── core/                # Config, auth, logging
│   │   ├── db/                  # Database models & schemas
│   │   ├── mcp/                 # Model Context Protocol
│   │   └── rag/                 # RAG pipeline components
│   ├── migrations/              # Alembic migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   └── services/            # API client
│   ├── package.json
│   └── Dockerfile
├── tests/                       # Test suites
├── docker-compose.yml
├── render.yaml                  # Render Blueprint
└── README.md
```

---

## 🔧 Configuration

### LLM Models

The system uses Groq's Llama 3.1 by default. To change models:

```env
GROQ_MODEL=llama-3.1-70b-versatile  # More capable, slower
GROQ_MODEL=llama-3.1-8b-instant     # Faster, good for most tasks
GROQ_MODEL=mixtral-8x7b-32768       # Alternative model
```

### RAG Pipeline

1. Place medical documents in `backend/app/rag/` folder
2. Run ingestion script:
   ```bash
   cd backend
   python -m app.rag.ingest
   ```
3. Documents are chunked, embedded, and stored in ChromaDB

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Python: Follow PEP 8, use Black formatter
- JavaScript: ESLint with React recommended rules
- Commits: Conventional Commits format

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent orchestration
- [Groq](https://groq.com/) - High-performance LLM inference
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API framework
- [React](https://react.dev/) - Frontend UI library

---

<div align="center">

**Built with ❤️ for healthcare professionals**

[Report Bug](https://github.com/yourusername/heat-clinical-assistant/issues) • [Request Feature](https://github.com/yourusername/heat-clinical-assistant/issues)

</div>
