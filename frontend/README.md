# Clinical AI Assistant Frontend

This is the React frontend for the Clinical AI Assistant with complete multi-tenancy support.

## Features

- **Authentication System**: Secure JWT-based login/signup
- **Multi-Tenant Dashboard**: Each doctor sees only their patients
- **AI Chat Interface**: Integrated LLM chat with patient context
- **File Upload**: Upload PDF lab results for processing
- **RAG Search**: Medical literature search functionality
- **Patient Management**: Add, view, and search patients

## API Integration

The frontend integrates with the following backend endpoints:

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh

### Patient Management
- `GET /api/patients/` - Get all patients (filtered by user)
- `GET /api/patients/{id}` - Get specific patient
- `POST /api/patients/add` - Add new patient
- `GET /api/mcp/patient/{id}` - Get patient via MCP

### AI & Chat
- `POST /api/llm/query` - LLM chat queries
- `POST /api/rag-search` - Medical literature search

### File Upload
- `POST /api/upload-lab-results/` - Upload PDF lab results

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. The frontend will be available at `http://localhost:3001`

## Multi-Tenancy

The system automatically handles multi-tenancy:
- Each doctor creates their own account
- All data (patients, lab results, etc.) is automatically filtered by user
- JWT tokens handle authentication and user context
- Complete data isolation between different doctors

## Usage

1. **Registration**: Create a doctor account at `/signup`
2. **Login**: Access the system at `/login`
3. **Dashboard**: Main interface with 3 panels:
   - Left: Patient list with search and add functionality
   - Center: Lab results display
   - Right: AI chat with file upload and RAG search

## Components

- `PatientList.jsx` - Patient management with add/search
- `LabResults.jsx` - Lab results display
- `ChatPanel.jsx` - AI chat with file upload and RAG search
- `Dashboard.jsx` - Main layout and navigation
- `Login.jsx` / `Signup.jsx` - Authentication forms

## API Service

All backend communication is handled through `services/api.js` with:
- Automatic JWT token management
- Request/response interceptors
- Automatic token refresh on 401 errors
- Organized API functions by domain

The frontend is fully integrated with the multi-tenant backend and ready for production use.