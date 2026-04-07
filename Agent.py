"""
Agentic AI Core Logic
This module defines the ReAct agent powered by LangGraph, incorporating
file system tools and proactive path detection.
"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env (OPENROUTER_API_KEY, OPENROUTER_BASE_URL)
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
base_url = os.getenv("OPENROUTER_BASE_URL")

# ── FILE PATH DETECTION ──────────────────────────────────────────────────────
# These regex patterns detect Windows and Unix-style absolute/relative file paths.
WINDOWS_PATH_RE = re.compile(r'[A-Za-z]:\\(?:[^\\\/:*?"<>|\r\n]+\\)*[^\\\/:*?"<>|\r\n]*')
UNIX_PATH_RE    = re.compile(r'\/(?:[^\/\0\s]+\/)*[^\/\0\s]+\.\w+')

def extract_file_paths(text: str) -> list[str]:
    """
    Extracts all Windows and Unix file paths from a given user message.
    Used for proactive tool calls before the LLM processing if needed.
    """
    return WINDOWS_PATH_RE.findall(text) + UNIX_PATH_RE.findall(text)


# ── TOOLS ────────────────────────────────────────────────────────────────────

@tool
def read_file(file_path: str) -> str:
    """
    Read the contents of a file from the local filesystem.
    Args:
        file_path (str): The absolute or relative path to the file.
    Returns:
        str: The content of the file or an error message.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file(file_path: str, content: str) -> str:
    """
    Write (or overwrite) content to a file.
    Args:
        file_path (str): Target path for the file.
        content (str): Text content to write.
    Returns:
        str: Success confirmation or error message.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to '{file_path}'."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def append_file(file_path: str, content: str) -> str:
    """
    Append content to an existing file without deleting its original content.
    Args:
        file_path (str): Target path for the file.
        content (str): Text content to append.
    Returns:
        str: Success confirmation or error message.
    """
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully appended to '{file_path}'."
    except Exception as e:
        return f"Error appending to file: {str(e)}"


@tool
def list_directory(dir_path: str) -> str:
    """
    List the contents of a specified directory.
    Args:
        dir_path (str): The path to investigate.
    Returns:
        str: A formatted list of files and directories.
    """
    try:
        entries = os.listdir(dir_path)
        if not entries:
            return f"Directory '{dir_path}' is empty."
        lines = []
        for entry in sorted(entries):
            full = os.path.join(dir_path, entry)
            tag = "[DIR] " if os.path.isdir(full) else "[FILE]"
            lines.append(f"{tag} {entry}")
        return "\n".join(lines)
    except FileNotFoundError:
        return f"Error: Directory '{dir_path}' not found."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# Define the toolset for the agent
TOOLS = [read_file, write_file, append_file, list_directory]

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────

SYSTEM_MESSAGE = """
You are a helpful AI assistant with the ability to read and write files on the user's computer.

## FILE PATH DETECTION
When the user's message contains a file path (Windows like C:\\Users\\file.txt or Unix like /home/user/file.py),
you MUST automatically use read_file on that path without asking — unless the user's intent is clearly to write.
If multiple paths are detected, read all of them and summarize each.

## TOOLS AVAILABLE
- read_file: Read any file by its path.
- write_file: Create or overwrite a file with new content.
- append_file: Add content to the end of an existing file.
- list_directory: List all files and folders in a directory.

## GUIDELINES
- Auto-detect and act on file paths in the user's message immediately.
- When writing or appending, format content cleanly (e.g., proper indentation for code).
- If a file operation fails, explain why and suggest a fix.
- Never guess a file path — ask the user if you're unsure.
- Always explain what action you took and what you found.

You are precise, reliable, and proactive about handling files.
"""


# ── LLM + AGENT INITIALIZATION ──────────────────────────────────────────────

# Configure LLM (Using OpenRouter as the provider)
llm = ChatOpenAI(
    model="deepseek/deepseek-chat",
    api_key=api_key,
    base_url=base_url,
    temperature=0
)

# Create the ReAct agent with LangGraph
agent = create_react_agent(
    model=llm,
    tools=TOOLS,
    prompt=SYSTEM_MESSAGE
)


# ── AGENT RUNNER ─────────────────────────────────────────────────────────────

def run_agent(user_input: str) -> str:
    """
    Main entry point to execute the agent.
    1. Detects paths for logging.
    2. Invokes the agent with user input.
    3. Extracts and returns the final response string.
    """
    print("\n--- Agent Running ---")

    # Log detected file paths to the server console for debug transparency
    paths = extract_file_paths(user_input)
    if paths:
        print(f"[Path Detector] Found: {paths}")

    try:
        # Invoke the agent graph
        response = agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })

        # Return the last message from the agent's message history
        if response and "messages" in response and response["messages"]:
            final_message = response["messages"][-1].content
            print(f"Agent: {final_message}")
            return str(final_message)

        return "No response generated."

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Agent error: {str(e)}"


# ── INTERACTIVE CLI MODE ──────────────────────────────────────────────────────

if __name__ == "__main__":
    # Allows developers to test the agent logic directly via terminal
    print("--- Starting Agent CLI Mode ---")
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break
            run_agent(user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break