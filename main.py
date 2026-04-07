"""
Agentic AI Console - Main Backend Entry Point
This script initializes a FastAPI server to serve the frontend and provide an 
endpoint for interacting with the AI Agent.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Agent import run_agent
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

# Initialize FastAPI App
app = FastAPI(title="Agentic AI Console API")

# Mount the 'static' directory to serve frontend assets (CSS, JS, Images)
# Access these via /static/filename.ext
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── DATA MODELS ─────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    """Data model for the incoming user prompt."""
    prompt: str

class AgentResponse(BaseModel):
    """Data model for the agent response."""
    response: str

# ── ENDPOINTS ─────────────────────────────────────────────────────────────

@app.get("/")
def home():
    """Serves the main application UI (index.html)."""
    return FileResponse(os.path.join("static", "index.html"))


@app.post("/agent", response_model=AgentResponse)
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


# ── MAIN ENTRY ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start the server on host 0.0.0.0 and port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)