import requests
import os

BASE_URL = "http://localhost:11434/api"
REQUEST_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "20"))

def generate(prompt, model="llama3"):
    try:
        response = requests.post(
            f"{BASE_URL}/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        return f"Error: {str(e)}"


def embed(text, model="nomic-embed-text"):
    try:
        response = requests.post(
            f"{BASE_URL}/embeddings",
            json={
                "model": model,
                "prompt": text
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception:
        return []