"""
Scoring engine for resume relevance calculation.
Implements hard-match (keyword) and soft-match (semantic) scoring.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_relevance_score(
    jd_text: str,
    resume_text: str,
    jd_skills: Dict[str, List[str]],
    hard_weight: float = 0.6,
    soft_weight: float = 0.4
) -> Dict[str, any]:
    """
    Calculate comprehensive relevance score between resume and job description.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
        jd_skills: Extracted skills from JD
        hard_weight: Weight for hard match score (0-1)
        soft_weight: Weight for soft match score (0-1)
    
    Returns:
        Dictionary with scoring results
    """
    try:

        hard_score = calculate_hard_match_score(resume_text, jd_skills)
        

        soft_score = calculate_soft_match_score(jd_text, resume_text)
        

        final_score = round(hard_weight * hard_score + soft_weight * soft_score, 2)
        

        verdict = determine_verdict(final_score)
        

        missing_skills = find_missing_skills(resume_text, jd_skills)
        
        return {
            'hard_pct': hard_score,
            'soft_pct': soft_score,
            'final_score': final_score,
            'verdict': verdict,
            'missing_skills': missing_skills,
            'hard_weight': hard_weight,
            'soft_weight': soft_weight
        }
        
    except Exception as e:
        logger.error(f"Error calculating relevance score: {e}")
        return {
            'hard_pct': 0,
            'soft_pct': 0,
            'final_score': 0,
            'verdict': 'Low',
            'missing_skills': [],
            'hard_weight': hard_weight,
            'soft_weight': soft_weight
        }

def calculate_hard_match_score(resume_text: str, jd_skills: Dict[str, List[str]]) -> float:
    """
    Calculate hard match score based on keyword/skill matching.
    
    Args:
        resume_text: Resume text
        jd_skills: Required skills from JD
    
    Returns:
        Hard match score (0-100)
    """
    if not resume_text or not jd_skills:
        return 0.0
    
    try:
        from .skill_extractor import extract_skills_from_resume, calculate_skill_match
        

        resume_skills = extract_skills_from_resume(resume_text)
        

        match_stats = calculate_skill_match(resume_skills, jd_skills)
        

        must_have_weight = 0.7
        good_to_have_weight = 0.3
        
        must_have_score = match_stats['must_have_score'] * 100
        good_to_have_score = match_stats['good_to_have_score'] * 100
        

        hard_score = (must_have_weight * must_have_score + 
                     good_to_have_weight * good_to_have_score)
        
        return min(100.0, max(0.0, hard_score))
        
    except Exception as e:
        logger.error(f"Error calculating hard match score: {e}")
        return 0.0

def calculate_soft_match_score(jd_text: str, resume_text: str) -> float:
    """
    Calculate soft match score using semantic similarity.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
    
    Returns:
        Soft match score (0-100)
    """
    if not jd_text or not resume_text:
        return 0.0
    
    try:

        try:
            from .embeddings import get_embeddings, calculate_similarity
            jd_embedding = get_embeddings([jd_text])[0]
            resume_embedding = get_embeddings([resume_text])[0]
            similarity = calculate_similarity(jd_embedding, resume_embedding)
            return similarity * 100
        except ImportError:
            logger.warning("Embeddings module not available, using TF-IDF fallback")
            return calculate_tfidf_similarity(jd_text, resume_text)
        
    except Exception as e:
        logger.error(f"Error calculating soft match score: {e}")
        return 0.0

def calculate_tfidf_similarity(jd_text: str, resume_text: str) -> float:
    """
    Calculate similarity using TF-IDF as fallback.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
    
    Returns:
        Similarity score (0-100)
    """
    try:

        texts = [jd_text, resume_text]
        

        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        
        tfidf_matrix = vectorizer.fit_transform(texts)
        

        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        

        return similarity * 100
        
    except Exception as e:
        logger.error(f"Error calculating TF-IDF similarity: {e}")
        return 0.0

def find_missing_skills(resume_text: str, jd_skills: Dict[str, List[str]]) -> List[str]:
    """
    Find skills that are required but missing from resume.
    
    Args:
        resume_text: Resume text
        jd_skills: Required skills from JD
    
    Returns:
        List of missing skills
    """
    if not resume_text or not jd_skills:
        return []
    
    try:
        from .skill_extractor import extract_skills_from_resume, calculate_skill_match
        

        resume_skills = extract_skills_from_resume(resume_text)
        

        match_stats = calculate_skill_match(resume_skills, jd_skills)
        

        missing_skills = match_stats['missing_must_have']
        

        if len(missing_skills) < 3:
            missing_skills.extend(match_stats['missing_good_to_have'][:3])
        
        return missing_skills[:5]
        
    except Exception as e:
        logger.error(f"Error finding missing skills: {e}")
        return []

def determine_verdict(final_score: float) -> str:
    """
    Determine verdict based on final score.
    
    Args:
        final_score: Final relevance score (0-100)
    
    Returns:
        Verdict string
    """
    if final_score >= 75:
        return "High"
    elif final_score >= 45:
        return "Medium"
    else:
        return "Low"

def calculate_skill_coverage(resume_skills: List[str], jd_skills: Dict[str, List[str]]) -> Dict[str, float]:
    """
    Calculate detailed skill coverage statistics.
    
    Args:
        resume_skills: Skills found in resume
        jd_skills: Required skills from JD
    
    Returns:
        Dictionary with coverage statistics
    """
    must_have = jd_skills.get('must_have', [])
    good_to_have = jd_skills.get('good_to_have', [])
    

    resume_skills_lower = [skill.lower() for skill in resume_skills]
    must_have_lower = [skill.lower() for skill in must_have]
    good_to_have_lower = [skill.lower() for skill in good_to_have]
    

    must_have_matches = len([skill for skill in must_have_lower if skill in resume_skills_lower])
    good_to_have_matches = len([skill for skill in good_to_have_lower if skill in resume_skills_lower])
    
    return {
        'must_have_coverage': must_have_matches / len(must_have) if must_have else 0,
        'good_to_have_coverage': good_to_have_matches / len(good_to_have) if good_to_have else 0,
        'total_coverage': (must_have_matches + good_to_have_matches) / (len(must_have) + len(good_to_have)) if (must_have or good_to_have) else 0,
        'must_have_matches': must_have_matches,
        'good_to_have_matches': good_to_have_matches
    }

def normalize_score(score: float, min_val: float = 0, max_val: float = 100) -> float:
    """
    Normalize score to 0-100 range.
    
    Args:
        score: Raw score
        min_val: Minimum possible value
        max_val: Maximum possible value
    
    Returns:
        Normalized score (0-100)
    """
    if max_val == min_val:
        return 0.0
    
    normalized = ((score - min_val) / (max_val - min_val)) * 100
    return max(0.0, min(100.0, normalized))


def test_scoring():
    """Test scoring with sample data."""
    sample_jd = "We need a Python developer with machine learning experience."
    sample_resume = "I am a Python developer with 3 years of experience in machine learning, pandas, and numpy."
    sample_skills = {
        'must_have': ['Python', 'Machine Learning'],
        'good_to_have': ['Pandas', 'Numpy', 'Git']
    }
    
    result = calculate_relevance_score(sample_jd, sample_resume, sample_skills)
    print("Scoring Test Results:")
    print(f"Hard Score: {result['hard_pct']:.1f}%")
    print(f"Soft Score: {result['soft_pct']:.1f}%")
    print(f"Final Score: {result['final_score']:.1f}%")
    print(f"Verdict: {result['verdict']}")
    print(f"Missing Skills: {result['missing_skills']}")

if __name__ == "__main__":
    test_scoring()