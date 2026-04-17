# Deploying HEAT Clinical Assistant to Render

This guide explains how to deploy the HEAT Clinical Assistant application to [Render](https://render.com).

## Architecture Overview

The application consists of:
- **Backend**: FastAPI application with MCP (Model Context Protocol) server for database operations
- **Frontend**: React/Vite static site
- **Database**: PostgreSQL (managed by Render)

## Prerequisites

1. A [Render](https://render.com) account
2. A GitHub/GitLab repository with your code
3. A GROQ API key for LLM functionality

## Quick Deploy with Render Blueprint

The easiest way to deploy is using the `render.yaml` Blueprint:

### Step 1: Push Code to Repository

Ensure all changes are committed and pushed to your Git repository.

### Step 2: Create New Blueprint on Render

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Blueprint**
3. Connect your Git repository
4. Render will detect `render.yaml` and show all services to be created

### Step 3: Configure Environment Variables

Before deploying, set the following **secret** environment variable in the Render dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your GROQ API key for LLM operations | Yes |

The following are automatically configured:
- `DATABASE_URL` - PostgreSQL connection string (from Render managed database)
- `SECRET_KEY` - Auto-generated JWT secret
- All other environment variables are set via `render.yaml`

### Step 4: Deploy

Click **Apply** to create all services. Render will:
1. Create a PostgreSQL database
2. Build and deploy the backend
3. Build and deploy the frontend static site

## Manual Deployment

If you prefer manual deployment:

### 1. Create PostgreSQL Database

1. Go to Render Dashboard → **New** → **PostgreSQL**
2. Choose a name (e.g., `heat-postgres`)
3. Select the **Free** plan
4. Note the connection details

### 2. Deploy Backend

1. Go to **New** → **Web Service**
2. Connect your repository
3. Configure:
   - **Name**: `heat-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Health Check Path**: `/api/health`
4. Add environment variables (see table above)
5. Deploy

### 3. Deploy Frontend

1. Go to **New** → **Static Site**
2. Connect your repository
3. Configure:
   - **Name**: `heat-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
4. Add environment variable:
   - `VITE_API_URL`: Your backend URL (e.g., `heat-backend.onrender.com`)
5. Deploy

## MCP Server Integration

The MCP (Model Context Protocol) server is automatically started with the backend service:

1. **Startup Script** (`backend/start.sh`):
   - Fixes DATABASE_URL format for SQLAlchemy
   - Runs database migrations
   - Starts MCP Database Server in background
   - Starts FastAPI application

2. **MCP Server Features**:
   - Handles all database operations via controlled tools
   - Provides database access control layer
   - Supports patient management, user authentication, and custom queries

3. **How it works**:
   - The MCP server (`app.mcp.db_server`) runs as a background process
   - The FastAPI app uses `app.mcp.client` to check if MCP is running
   - All database operations go through the MCP client

## Environment Variables Reference

### Backend Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `POSTGRES_*` | Database credentials | From Render DB |
| `SECRET_KEY` | JWT signing secret | Auto-generated |
| `GROQ_API_KEY` | GROQ API key | Required |
| `MCP_SERVER_HOST` | MCP server host | `127.0.0.1` |
| `MCP_SERVER_PORT` | MCP server port | `9000` |
| `SKIP_MCP_CHECK` | Skip MCP process check | `false` |
| `FRONTEND_URL` | Frontend URL for CORS | Auto-configured |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | `7` |
| `CHROMA_DB_PATH` | ChromaDB storage path | `/app/chroma_data` |
| `GROQ_MODEL` | GROQ model to use | `llama-3.1-8b-instant` |

### Frontend Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (without protocol) |

## Post-Deployment Steps

### 1. Run Database Migrations

Migrations run automatically on deployment via `start.sh`. If needed manually:

```bash
# SSH into backend service or use Render Shell
cd /app
alembic upgrade head
```

### 2. Verify Health Check

```bash
curl https://your-backend.onrender.com/api/health
```

Expected response:
```json
{"status": "ok", "mcp_status": "running"}
```

### 3. Test Authentication

```bash
# Signup
curl -X POST https://your-backend.onrender.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "password123"}'

# Login
curl -X POST https://your-backend.onrender.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'
```

## Troubleshooting

### MCP Server Not Running

If you see "MCP Database Server is not running" errors:

1. Check the backend logs in Render dashboard
2. Ensure `start.sh` is executable (it's set in Dockerfile)
3. Verify the MCP server process started:
   ```bash
   ps aux | grep db_server
   ```

### Database Connection Issues

1. Verify `DATABASE_URL` is set correctly
2. Check if the format is `postgresql+psycopg2://...` (SQLAlchemy format)
3. The `start.sh` script auto-converts `postgres://` to `postgresql+psycopg2://`

### CORS Errors

1. Check that `FRONTEND_URL` is set in backend env vars
2. Verify the frontend URL is in the CORS allowed origins
3. The backend allows all `*.onrender.com` subdomains

### Frontend Can't Connect to Backend

1. Verify `VITE_API_URL` is set correctly (without `https://`)
2. Check browser console for actual API calls
3. Ensure backend is running and healthy

## Scaling

### Upgrading Plans

1. Go to Render Dashboard → Your Service → Settings
2. Change the plan from Free to paid tiers
3. Paid plans offer:
   - More memory/CPU
   - No spin-down on idle
   - Custom domains
   - Persistent disks

### Adding Custom Domain

1. Go to Service Settings → Custom Domains
2. Add your domain
3. Configure DNS as instructed by Render

## Local Development vs Production

| Aspect | Local | Production (Render) |
|--------|-------|---------------------|
| Database | Local PostgreSQL | Render Managed PostgreSQL |
| MCP Server | Manual start required | Auto-started by `start.sh` |
| Frontend API | `http://localhost:8001` | `https://backend.onrender.com` |
| CORS | localhost only | All Render subdomains |

## Support

For issues specific to this application, check:
1. Backend logs in Render dashboard
2. Frontend browser console
3. Database connection in Render PostgreSQL dashboard

For Render-specific issues, see [Render Documentation](https://render.com/docs).
