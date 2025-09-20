"""
Resume Strength Heatmap Analyzer
Creates visual heatmaps showing resume strengths across different dimensions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


STRENGTH_CATEGORIES = {
    'technical_skills': {
        'weight': 0.25,
        'keywords': ['python', 'java', 'javascript', 'sql', 'machine learning', 'data science', 'aws', 'docker'],
        'subcategories': ['programming', 'databases', 'cloud', 'ai_ml', 'devops']
    },
    'soft_skills': {
        'weight': 0.20,
        'keywords': ['leadership', 'communication', 'teamwork', 'problem solving', 'project management'],
        'subcategories': ['leadership', 'communication', 'collaboration', 'management']
    },
    'experience': {
        'weight': 0.25,
        'keywords': ['experience', 'years', 'senior', 'lead', 'manager', 'director'],
        'subcategories': ['years_experience', 'leadership_roles', 'industry_experience']
    },
    'education': {
        'weight': 0.15,
        'keywords': ['bachelor', 'master', 'phd', 'degree', 'university', 'college'],
        'subcategories': ['degree_level', 'relevance', 'prestige']
    },
    'achievements': {
        'weight': 0.15,
        'keywords': ['achieved', 'increased', 'improved', 'award', 'certification', 'published'],
        'subcategories': ['quantified_results', 'awards', 'certifications', 'publications']
    }
}

def analyze_resume_strengths(resume_text: str, jd_requirements: Dict = None) -> Dict[str, any]:
    """
    Analyze resume strengths across multiple dimensions.
    
    Args:
        resume_text: Resume text content
        jd_requirements: Job description requirements
    
    Returns:
        Comprehensive strength analysis
    """
    try:

        strength_scores = {}
        detailed_analysis = {}
        
        for category, config in STRENGTH_CATEGORIES.items():
            score, details = calculate_category_strength(resume_text, category, config, jd_requirements)
            strength_scores[category] = score
            detailed_analysis[category] = details
        

        overall_score = calculate_overall_strength(strength_scores)
        

        insights = generate_strength_insights(strength_scores, detailed_analysis)
        

        recommendations = generate_strength_recommendations(strength_scores, jd_requirements)
        

        strength_matrix = create_strength_matrix(strength_scores, detailed_analysis)
        
        return {
            'overall_strength': round(overall_score, 2),
            'category_scores': strength_scores,
            'detailed_analysis': detailed_analysis,
            'strength_matrix': strength_matrix,
            'insights': insights,
            'recommendations': recommendations,
            'analysis_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing resume strengths: {e}")
        return {
            'overall_strength': 0,
            'category_scores': {},
            'detailed_analysis': {},
            'strength_matrix': {},
            'insights': ['Error in strength analysis'],
            'recommendations': ['Unable to generate recommendations'],
            'analysis_date': datetime.now().isoformat()
        }

def calculate_category_strength(resume_text: str, category: str, config: Dict, jd_requirements: Dict = None) -> Tuple[float, Dict]:
    """Calculate strength score for a specific category."""
    try:
        score = 0
        details = {
            'keyword_matches': [],
            'subcategory_scores': {},
            'jd_alignment': 0
        }
        

        keywords = config['keywords']
        matched_keywords = []
        for keyword in keywords:
            if keyword.lower() in resume_text.lower():
                matched_keywords.append(keyword)
                score += 10
        
        details['keyword_matches'] = matched_keywords
        

        subcategories = config['subcategories']
        for subcat in subcategories:
            subcat_score = calculate_subcategory_score(resume_text, subcat, category)
            details['subcategory_scores'][subcat] = subcat_score
            score += subcat_score * 0.1
        

        if jd_requirements:
            jd_alignment = calculate_jd_alignment(resume_text, category, jd_requirements)
            details['jd_alignment'] = jd_alignment
            score += jd_alignment * 0.2
        

        max_possible = len(keywords) * 10 + len(subcategories) * 10 + 20
        normalized_score = min((score / max_possible) * 100, 100)
        
        return round(normalized_score, 2), details
        
    except Exception as e:
        logger.error(f"Error calculating category strength for {category}: {e}")
        return 0, {}

def calculate_subcategory_score(resume_text: str, subcategory: str, category: str) -> float:
    """Calculate score for a specific subcategory."""
    try:

        subcategory_patterns = {
            'programming': ['python', 'java', 'javascript', 'c++', 'sql', 'html', 'css'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'database'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud', 'docker', 'kubernetes'],
            'ai_ml': ['machine learning', 'artificial intelligence', 'deep learning', 'neural networks'],
            'devops': ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'deployment'],
            'leadership': ['led', 'managed', 'directed', 'supervised', 'team lead'],
            'communication': ['presented', 'communicated', 'collaborated', 'negotiated'],
            'collaboration': ['team', 'collaborated', 'worked with', 'cross-functional'],
            'management': ['managed', 'directed', 'supervised', 'coordinated'],
            'years_experience': [r'\d+\+?\s*years?', r'\d+\+?\s*yrs?'],
            'leadership_roles': ['manager', 'director', 'lead', 'head of', 'vp', 'ceo'],
            'industry_experience': ['experience in', 'worked in', 'industry'],
            'degree_level': ['bachelor', 'master', 'phd', 'doctorate'],
            'relevance': ['computer science', 'engineering', 'business', 'finance'],
            'prestige': ['university', 'college', 'institute', 'school'],
            'quantified_results': [r'\d+%', r'\$\d+', r'\d+x', r'increased', r'decreased'],
            'awards': ['award', 'recognition', 'honor', 'achievement'],
            'certifications': ['certified', 'certification', 'license', 'credential'],
            'publications': ['published', 'paper', 'article', 'research']
        }
        
        patterns = subcategory_patterns.get(subcategory, [])
        if not patterns:
            return 0
        
        score = 0
        for pattern in patterns:
            if subcategory in ['years_experience', 'quantified_results']:

                import re
                matches = re.findall(pattern, resume_text, re.IGNORECASE)
                score += len(matches) * 5
            else:

                if pattern.lower() in resume_text.lower():
                    score += 10
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating subcategory score for {subcategory}: {e}")
        return 0

def calculate_jd_alignment(resume_text: str, category: str, jd_requirements: Dict) -> float:
    """Calculate alignment with job description requirements."""
    try:
        if not jd_requirements:
            return 0
        
        alignment_score = 0
        

        must_have = jd_requirements.get('must_have', [])
        if must_have:
            matched_must_have = sum(1 for skill in must_have 
                                  if skill.lower() in resume_text.lower())
            alignment_score += (matched_must_have / len(must_have)) * 50
        

        good_to_have = jd_requirements.get('good_to_have', [])
        if good_to_have:
            matched_good_to_have = sum(1 for skill in good_to_have 
                                      if skill.lower() in resume_text.lower())
            alignment_score += (matched_good_to_have / len(good_to_have)) * 30
        
        return min(alignment_score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating JD alignment: {e}")
        return 0

def calculate_overall_strength(strength_scores: Dict[str, float]) -> float:
    """Calculate overall strength score."""
    try:
        total_score = 0
        total_weight = 0
        
        for category, score in strength_scores.items():
            weight = STRENGTH_CATEGORIES.get(category, {}).get('weight', 0.2)
            total_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            return total_score / total_weight
        else:
            return 0
            
    except Exception as e:
        logger.error(f"Error calculating overall strength: {e}")
        return 0

def create_strength_matrix(strength_scores: Dict[str, float], detailed_analysis: Dict) -> Dict[str, any]:
    """Create strength matrix for heatmap visualization."""
    try:
        matrix = {
            'categories': list(strength_scores.keys()),
            'scores': list(strength_scores.values()),
            'subcategory_breakdown': {}
        }
        

        for category, details in detailed_analysis.items():
            subcategory_scores = details.get('subcategory_scores', {})
            matrix['subcategory_breakdown'][category] = subcategory_scores
        
        return matrix
        
    except Exception as e:
        logger.error(f"Error creating strength matrix: {e}")
        return {}

def generate_strength_insights(strength_scores: Dict[str, float], detailed_analysis: Dict) -> List[str]:
    """Generate insights from strength analysis."""
    insights = []
    
    try:

        if strength_scores:
            strongest = max(strength_scores.items(), key=lambda x: x[1])
            weakest = min(strength_scores.items(), key=lambda x: x[1])
            
            insights.append(f"Strongest area: {strongest[0].replace('_', ' ').title()} ({strongest[1]:.1f}%)")
            insights.append(f"Area for improvement: {weakest[0].replace('_', ' ').title()} ({weakest[1]:.1f}%)")
        

        overall = calculate_overall_strength(strength_scores)
        if overall >= 80:
            insights.append("Excellent overall resume strength")
        elif overall >= 70:
            insights.append("Good overall resume strength")
        elif overall >= 60:
            insights.append("Average resume strength")
        else:
            insights.append("Resume needs significant improvement")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating strength insights: {e}")
        return ['Error generating insights']

def generate_strength_recommendations(strength_scores: Dict[str, float], jd_requirements: Dict = None) -> List[str]:
    """Generate recommendations based on strength analysis."""
    recommendations = []
    
    try:

        for category, score in strength_scores.items():
            if score < 60:
                category_name = category.replace('_', ' ').title()
                recommendations.append(f"Focus on improving {category_name} (current: {score:.1f}%)")
        

        if jd_requirements:
            must_have = jd_requirements.get('must_have', [])
            if must_have:
                recommendations.append(f"Ensure all must-have skills are highlighted: {', '.join(must_have[:3])}")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating strength recommendations: {e}")
        return ['Error generating recommendations']


def test_strength_analyzer():
    """Test strength analyzer with sample resume."""
    sample_resume = """
    John Doe - Software Engineer
    
    Experience:
    - 5 years Python development
    - Led team of 8 developers
    - Increased system performance by 40%
    - AWS and Docker expertise
    
    Education:
    - Bachelor of Computer Science, MIT
    
    Skills:
    - Python, Java, SQL, Machine Learning
    - Leadership, Project Management
    """
    
    sample_jd = {
        'must_have': ['Python', 'Leadership', 'AWS'],
        'good_to_have': ['Docker', 'Machine Learning', 'SQL']
    }
    
    analysis = analyze_resume_strengths(sample_resume, sample_jd)
    print("Strength Analysis:")
    print(f"Overall Strength: {analysis['overall_strength']}%")
    print(f"Category Scores: {analysis['category_scores']}")

if __name__ == "__main__":
    test_strength_analyzer()