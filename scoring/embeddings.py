"""
Embeddings module for semantic similarity calculation.
Supports sentence-transformers and Grok embeddings with fallback.
"""

import numpy as np
from typing import List, Optional, Union
import logging
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


_model_cache = {}

def get_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Get embeddings for a list of texts.
    
    Args:
        texts: List of text strings
        model_name: Name of the embedding model to use
    
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    try:

        try:
            from .grok_client import grok_embeddings
            grok_result = grok_embeddings(texts)
            if grok_result.get('ok'):
                return grok_result['embeddings']
        except ImportError:
            logger.warning("Grok client not available, using sentence-transformers")
        

        return get_sentence_transformer_embeddings(texts, model_name)
        
    except Exception as e:
        logger.error(f"Error getting embeddings: {e}")

        return [[0.0] * 384 for _ in texts]

def get_sentence_transformer_embeddings(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Get embeddings using sentence-transformers.
    
    Args:
        texts: List of text strings
        model_name: Name of the sentence transformer model
    
    Returns:
        List of embedding vectors
    """
    try:
        from sentence_transformers import SentenceTransformer
        

        if model_name not in _model_cache:
            logger.info(f"Loading sentence transformer model: {model_name}")
            _model_cache[model_name] = SentenceTransformer(model_name)
        
        model = _model_cache[model_name]
        

        embeddings = model.encode(texts, convert_to_tensor=False)
        

        return [embedding.tolist() for embedding in embeddings]
        
    except ImportError:
        logger.error("sentence-transformers not installed, using TF-IDF fallback")
        return get_tfidf_embeddings(texts)
    except Exception as e:
        logger.error(f"Error with sentence transformers: {e}")
        return get_tfidf_embeddings(texts)

def get_tfidf_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Get TF-IDF embeddings as fallback.
    
    Args:
        texts: List of text strings
    
    Returns:
        List of TF-IDF vectors
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.decomposition import TruncatedSVD
        

        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        

        svd = TruncatedSVD(n_components=100, random_state=42)
        embeddings = svd.fit_transform(tfidf_matrix)
        
        return embeddings.tolist()
        
    except Exception as e:
        logger.error(f"Error with TF-IDF embeddings: {e}")

        return [np.random.rand(100).tolist() for _ in texts]

def calculate_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
    
    Returns:
        Similarity score (0-1)
    """
    try:

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        

        return max(0.0, min(1.0, similarity))
        
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        return 0.0

def calculate_batch_similarity(embeddings1: List[List[float]], embeddings2: List[List[float]]) -> List[float]:
    """
    Calculate similarities between two lists of embeddings.
    
    Args:
        embeddings1: First list of embeddings
        embeddings2: Second list of embeddings
    
    Returns:
        List of similarity scores
    """
    similarities = []
    min_len = min(len(embeddings1), len(embeddings2))
    
    for i in range(min_len):
        similarity = calculate_similarity(embeddings1[i], embeddings2[i])
        similarities.append(similarity)
    
    return similarities

def get_text_similarity(text1: str, text2: str, model_name: str = "all-MiniLM-L6-v2") -> float:
    """
    Calculate similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        model_name: Embedding model to use
    
    Returns:
        Similarity score (0-1)
    """
    try:
        embeddings = get_embeddings([text1, text2], model_name)
        if len(embeddings) >= 2:
            return calculate_similarity(embeddings[0], embeddings[1])
        return 0.0
    except Exception as e:
        logger.error(f"Error calculating text similarity: {e}")
        return 0.0

def normalize_embeddings(embeddings: List[List[float]]) -> List[List[float]]:
    """
    Normalize embeddings to unit vectors.
    
    Args:
        embeddings: List of embedding vectors
    
    Returns:
        Normalized embeddings
    """
    normalized = []
    for embedding in embeddings:
        vec = np.array(embedding)
        norm = np.linalg.norm(vec)
        if norm > 0:
            normalized.append((vec / norm).tolist())
        else:
            normalized.append([0.0] * len(embedding))
    return normalized

def save_embeddings(embeddings: List[List[float]], file_path: str):
    """
    Save embeddings to file.
    
    Args:
        embeddings: List of embedding vectors
        file_path: Path to save file
    """
    try:
        import json
        with open(file_path, 'w') as f:
            json.dump(embeddings, f)
        logger.info(f"Saved embeddings to {file_path}")
    except Exception as e:
        logger.error(f"Error saving embeddings: {e}")

def load_embeddings(file_path: str) -> List[List[float]]:
    """
    Load embeddings from file.
    
    Args:
        file_path: Path to embeddings file
    
    Returns:
        List of embedding vectors
    """
    try:
        import json
        with open(file_path, 'r') as f:
            embeddings = json.load(f)
        logger.info(f"Loaded embeddings from {file_path}")
        return embeddings
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}")
        return []

def create_embedding_index(texts: List[str], model_name: str = "all-MiniLM-L6-v2") -> dict:
    """
    Create an embedding index for fast similarity search.
    
    Args:
        texts: List of texts to index
        model_name: Embedding model to use
    
    Returns:
        Dictionary with embeddings and metadata
    """
    try:
        embeddings = get_embeddings(texts, model_name)
        
        index = {
            'texts': texts,
            'embeddings': embeddings,
            'model_name': model_name,
            'dimension': len(embeddings[0]) if embeddings else 0
        }
        
        return index
        
    except Exception as e:
        logger.error(f"Error creating embedding index: {e}")
        return {'texts': [], 'embeddings': [], 'model_name': model_name, 'dimension': 0}

def search_similar_texts(query_text: str, index: dict, top_k: int = 5) -> List[tuple]:
    """
    Search for similar texts in the index.
    
    Args:
        query_text: Query text
        index: Embedding index
        top_k: Number of top results to return
    
    Returns:
        List of (text, similarity_score) tuples
    """
    try:
        if not index.get('embeddings'):
            return []
        

        query_embeddings = get_embeddings([query_text], index['model_name'])
        if not query_embeddings:
            return []
        
        query_embedding = query_embeddings[0]
        

        similarities = []
        for i, doc_embedding in enumerate(index['embeddings']):
            similarity = calculate_similarity(query_embedding, doc_embedding)
            similarities.append((index['texts'][i], similarity))
        

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
        
    except Exception as e:
        logger.error(f"Error searching similar texts: {e}")
        return []


def test_embeddings():
    """Test embedding functionality."""
    sample_texts = [
        "Python developer with machine learning experience",
        "Data scientist with Python and ML skills",
        "Software engineer with Java and Spring Boot"
    ]
    
    print("Testing embeddings...")
    embeddings = get_embeddings(sample_texts)
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
    
    if len(embeddings) >= 2:
        similarity = calculate_similarity(embeddings[0], embeddings[1])
        print(f"Similarity between first two texts: {similarity:.3f}")

if __name__ == "__main__":
    test_embeddings()