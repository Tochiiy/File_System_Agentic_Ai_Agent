"""
Agentic AI Console - Consolidated Vercel API
This script manages both the AI backend and the serving of static assets
for a seamless single-origin deployment on Vercel.
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .Agent import run_agent
import os

# Initialize FastAPI App
app = FastAPI(title="Agentic AI Console")

# Determine the absolute path to the 'public' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# ── DATA MODELS ─────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    prompt: str

class AgentResponse(BaseModel):
    response: str

# ── API ENDPOINTS ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {"status": "ok", "director": PUBLIC_DIR}

@app.post("/api/agent", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        result = run_agent(request.prompt)
        return AgentResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")

# ── STATIC ASSETS & UI ────────────────────────────────────────────────────────

@app.get("/")
async def serve_home():
    """Explicitly serve the main UI."""
    index_path = os.path.join(PUBLIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "index.html not found", "path": index_path}

# Mount the 'public' directory to serve CSS, JS, and Images
# Using html=True allows it to serve index.html automatically if hit
if os.path.exists(PUBLIC_DIR):
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")
