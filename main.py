"""
Agentic AI Console - Backend Server
This script initializes the FastAPI application, mounts the static assets,
and exposes the agent's logic through a RESTful API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from Agent import run_agent
import os
#import uvicorn

# Initialize FastAPI App
app = FastAPI(title="Agentic AI Console")

# ── DATA MODELS ─────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    """Data model for the incoming user prompt."""
    prompt: str

class AgentResponse(BaseModel):
    """Data model for the agent response."""
    response: str

# ── API ENDPOINTS ─────────────────────────────────────────────────────────────

@app.post("/agent", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """
    Invokes the AI agent with the provided prompt.
    The agent is capable of reading and writing files based on natural language input.
    """
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
        # Run the agent logic from Agent.py
        result = run_agent(request.prompt)
        return AgentResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

# ── STATIC FILE SERVING ───────────────────────────────────────────────────────

# Mount the 'static' directory to serve CSS, JS, and Images
# This allows the frontend to access /static/styles.css, etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    """Serves the main conversation UI (index.html)."""
    return FileResponse(os.path.join("static", "index.html"))

# ── SERVER CONFIGURATION ─────────────────────────────────────────────────────

if __name__ == "__main__":
    pass
    # host: 0.0.0.0 makes it accessible on the local network
    # port: 8000 is the standard port for FastAPI/Uvicorn development
    #print("Agentic Console is starting on http://localhost:8000")
    #uvicorn.run(app, host="0.0.0.0", port=8000)
