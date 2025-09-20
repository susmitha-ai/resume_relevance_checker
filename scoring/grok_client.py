"""
Grok API client for text generation and embeddings.
Handles API calls with retry logic and error handling.
"""

import os
import requests
import time
import json
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv
import logging


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    import streamlit as st

    GROK_URL = st.secrets.get("grok", {}).get("api_url", os.getenv("GROK_API_URL", "https://api.grok.example/v1"))
    GROK_KEY = st.secrets.get("grok", {}).get("api_key", os.getenv("GROK_API_KEY", ""))
except:

    GROK_URL = os.getenv("GROK_API_URL", "https://api.grok.example/v1")
    GROK_KEY = os.getenv("GROK_API_KEY", "")


HEADERS = {
    "Authorization": f"Bearer {GROK_KEY}",
    "Content-Type": "application/json"
}

def grok_generate(
    prompt: str, 
    model: str = "grok-1", 
    max_tokens: int = 256, 
    temperature: float = 0.2
) -> Dict[str, Union[str, bool, dict]]:
    """
    Generate text using Grok API.
    
    Args:
        prompt: Input prompt
        model: Model name to use
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0-1)
    
    Returns:
        Dictionary with response or error
    """
    if not GROK_KEY or GROK_KEY == "sk-your-api-key-here":
        logger.warning("Grok API key not configured, returning mock response")
        return {
            "ok": True,
            "text": "Mock response: Please configure GROK_API_KEY in .env file",
            "raw": {"mock": True}
        }
    
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    

    endpoints = [
        f"{GROK_URL}/generate",
        f"{GROK_URL}/completions",
        f"{GROK_URL}/chat/completions"
    ]
    
    for endpoint in endpoints:
        try:
            response = make_api_request(endpoint, payload)
            if response.get("ok"):
                return response
        except Exception as e:
            logger.warning(f"Endpoint {endpoint} failed: {e}")
            continue
    
    return {
        "ok": False,
        "error": "All API endpoints failed"
    }

def grok_embeddings(texts: List[str], model: str = "grok-embeddings") -> Dict[str, Union[List[List[float]], bool, str]]:
    """
    Get embeddings using Grok API.
    
    Args:
        texts: List of texts to embed
        model: Embedding model name
    
    Returns:
        Dictionary with embeddings or error
    """
    if not GROK_KEY or GROK_KEY == "sk-your-api-key-here":
        logger.warning("Grok API key not configured, using fallback embeddings")
        return {
            "ok": True,
            "embeddings": [[0.1] * 384 for _ in texts],
            "raw": {"mock": True}
        }
    
    payload = {
        "model": model,
        "input": texts
    }
    

    endpoints = [
        f"{GROK_URL}/embeddings",
        f"{GROK_URL}/embed"
    ]
    
    for endpoint in endpoints:
        try:
            response = make_api_request(endpoint, payload)
            if response.get("ok"):

                raw_data = response.get("raw", {})
                if "data" in raw_data:
                    embeddings = [item.get("embedding", []) for item in raw_data["data"]]
                    return {
                        "ok": True,
                        "embeddings": embeddings,
                        "raw": raw_data
                    }
        except Exception as e:
            logger.warning(f"Embeddings endpoint {endpoint} failed: {e}")
            continue
    
    return {
        "ok": False,
        "error": "Embeddings API not available"
    }

def make_api_request(endpoint: str, payload: dict, max_retries: int = 3) -> Dict[str, Union[str, bool, dict]]:
    """
    Make API request with retry logic.
    
    Args:
        endpoint: API endpoint URL
        payload: Request payload
        max_retries: Maximum number of retries
    
    Returns:
        API response dictionary
    """
    for attempt in range(max_retries):
        try:
            response = requests.post(
                endpoint,
                headers=HEADERS,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        "ok": True,
                        "text": extract_text_from_response(data),
                        "raw": data
                    }
                except json.JSONDecodeError:
                    return {
                        "ok": False,
                        "error": "Invalid JSON response"
                    }
            
            elif response.status_code == 429:
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            elif response.status_code == 503:
                wait_time = 2 ** attempt
                logger.warning(f"Service unavailable, waiting {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            else:
                return {
                    "ok": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {
                "ok": False,
                "error": "Request timeout"
            }
        
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return {
                "ok": False,
                "error": f"Request failed: {e}"
            }
    
    return {
        "ok": False,
        "error": "Max retries exceeded"
    }

def extract_text_from_response(data: dict) -> str:
    """
    Extract text from API response.
    
    Args:
        data: API response data
    
    Returns:
        Extracted text
    """

    text_fields = [
        "text", "content", "message", "response", "answer", "output",
        "choices[0].text", "choices[0].message.content"
    ]
    
    for field in text_fields:
        if "." in field:

            parts = field.split(".")
            value = data
            try:
                for part in parts:
                    if part.startswith("[") and part.endswith("]"):

                        index = int(part[1:-1])
                        value = value[index]
                    else:
                        value = value[part]
                if value:
                    return str(value)
            except (KeyError, IndexError, TypeError):
                continue
        else:
            if field in data and data[field]:
                return str(data[field])
    

    for key, value in data.items():
        if isinstance(value, str) and value.strip():
            return value
    
    return "No text found in response"

def validate_api_key() -> bool:
    """
    Validate Grok API key.
    
    Returns:
        True if API key is valid, False otherwise
    """
    if not GROK_KEY or GROK_KEY == "sk-your-api-key-here":
        return False
    

    try:
        response = grok_generate("Test", max_tokens=5)
        return response.get("ok", False)
    except Exception:
        return False

def get_api_status() -> Dict[str, Union[str, bool]]:
    """
    Get API status and configuration.
    
    Returns:
        Dictionary with API status
    """
    return {
        "api_url": GROK_URL,
        "api_key_configured": bool(GROK_KEY and GROK_KEY != "sk-your-api-key-here"),
        "api_key_valid": validate_api_key() if GROK_KEY else False,
        "status": "configured" if GROK_KEY else "not_configured"
    }


def test_grok_client():
    """Test Grok client functionality."""
    print("Testing Grok client...")
    

    status = get_api_status()
    print(f"API Status: {status}")
    

    response = grok_generate("What is Python?", max_tokens=50)
    print(f"Generation test: {response.get('ok', False)}")
    if response.get('ok'):
        print(f"Response: {response.get('text', 'No text')[:100]}...")
    

    embeddings_response = grok_embeddings(["Python programming", "Machine learning"])
    print(f"Embeddings test: {embeddings_response.get('ok', False)}")
    if embeddings_response.get('ok'):
        print(f"Embeddings shape: {len(embeddings_response.get('embeddings', []))}")

if __name__ == "__main__":
    test_grok_client()