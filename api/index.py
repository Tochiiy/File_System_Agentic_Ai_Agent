"""
Agentic AI Console - Vercel API Entry Point
This script provides the /agent endpoint for Vercel deployments.
Static files (HTML, CSS, JS) are handled natively by Vercel from the root/public directory.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .Agent import run_agent
import os

# Initialize FastAPI App
app = FastAPI(title="Agentic AI Console API")

# ── DATA MODELS ─────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    """Data model for the incoming user prompt."""
    prompt: str

class AgentResponse(BaseModel):
    """Data model for the agent response."""
    response: str

# ── ENDPOINTS ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    """Health check endpoint for Vercel."""
    return {"status": "ok"}

@app.post("/api/agent", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """
    Invokes the AI agent with the provided prompt.
    The agent is capable of reading and writing files based on natural language input.
    """
    try:
        # Validate that the prompt is not empty
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Prompt cannot be empty")

        # Run the agent logic from Agent.py
        result = run_agent(request.prompt)
        return AgentResponse(response=result)
    except Exception as e:
        # Catch unexpected errors and return a 500 Internal Server Error
        raise HTTPException(status_code=500, detail=f"Error invoking Agent: {str(e)}")


