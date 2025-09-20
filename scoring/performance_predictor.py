"""
Resume Performance Predictor
Predicts interview success probability and hiring likelihood based on resume analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SUCCESS_FACTORS = {
    'technology': {
        'high_impact': ['python', 'machine learning', 'aws', 'docker', 'kubernetes', 'git'],
        'medium_impact': ['sql', 'javascript', 'react', 'node.js', 'api', 'database'],
        'experience_weight': 0.4,
        'skills_weight': 0.3,
        'projects_weight': 0.2,
        'education_weight': 0.1
    },
    'finance': {
        'high_impact': ['excel', 'sql', 'python', 'financial modeling', 'risk analysis', 'cfa'],
        'medium_impact': ['vba', 'power bi', 'tableau', 'statistics', 'economics'],
        'experience_weight': 0.5,
        'skills_weight': 0.25,
        'certifications_weight': 0.15,
        'education_weight': 0.1
    },
    'marketing': {
        'high_impact': ['digital marketing', 'seo', 'google analytics', 'social media', 'content creation'],
        'medium_impact': ['adobe creative suite', 'email marketing', 'campaign management', 'data analysis'],
        'experience_weight': 0.4,
        'skills_weight': 0.3,
        'portfolio_weight': 0.2,
        'education_weight': 0.1
    },
    'default': {
        'high_impact': ['leadership', 'project management', 'communication', 'problem solving'],
        'medium_impact': ['teamwork', 'analytical skills', 'time management', 'adaptability'],
        'experience_weight': 0.4,
        'skills_weight': 0.3,
        'achievements_weight': 0.2,
        'education_weight': 0.1
    }
}

def predict_performance(resume_analysis: Dict, jd_analysis: Dict, industry: str = 'default') -> Dict[str, any]:
    """
    Predict interview success and hiring likelihood.
    
    Args:
        resume_analysis: Resume analysis results
        jd_analysis: Job description analysis
        industry: Industry type
    
    Returns:
        Performance prediction with confidence scores
    """
    try:

        factors = SUCCESS_FACTORS.get(industry, SUCCESS_FACTORS['default'])
        

        base_score = calculate_base_performance_score(resume_analysis, factors)
        

        interview_probability = calculate_interview_probability(resume_analysis, base_score)
        

        hiring_likelihood = calculate_hiring_likelihood(resume_analysis, jd_analysis, base_score)
        

        confidence = calculate_confidence_level(resume_analysis, jd_analysis)
        

        insights = generate_performance_insights(resume_analysis, base_score, industry)
        

        recommendations = generate_performance_recommendations(resume_analysis, factors)
        
        return {
            'base_performance_score': round(base_score, 2),
            'interview_probability': round(interview_probability, 2),
            'hiring_likelihood': round(hiring_likelihood, 2),
            'confidence_level': confidence,
            'performance_grade': get_performance_grade(base_score),
            'insights': insights,
            'recommendations': recommendations,
            'industry': industry,
            'prediction_date': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error predicting performance: {e}")
        return {
            'base_performance_score': 0,
            'interview_probability': 0,
            'hiring_likelihood': 0,
            'confidence_level': 'Low',
            'performance_grade': 'Unknown',
            'insights': ['Error in performance prediction'],
            'recommendations': ['Unable to generate recommendations'],
            'industry': industry,
            'prediction_date': datetime.now().isoformat()
        }

def calculate_base_performance_score(resume_analysis: Dict, factors: Dict) -> float:
    """Calculate base performance score from resume analysis."""
    try:
        score = 0
        

        experience_score = min(resume_analysis.get('hard_pct', 0), 100)
        score += experience_score * factors['experience_weight']
        

        skills_score = min(resume_analysis.get('soft_pct', 0), 100)
        score += skills_score * factors['skills_weight']
        

        projects_score = estimate_projects_score(resume_analysis)
        score += projects_score * factors.get('projects_weight', 0.2)
        

        education_score = estimate_education_score(resume_analysis)
        score += education_score * factors['education_weight']
        

        if 'certifications_weight' in factors:
            cert_score = estimate_certifications_score(resume_analysis)
            score += cert_score * factors['certifications_weight']
        
        return min(score, 100)
        
    except Exception as e:
        logger.error(f"Error calculating base performance score: {e}")
        return 0

def calculate_interview_probability(resume_analysis: Dict, base_score: float) -> float:
    """Calculate interview success probability."""
    try:

        base_prob = base_score * 0.8
        

        missing_skills = len(resume_analysis.get('missing_skills', []))
        missing_penalty = min(missing_skills * 5, 30)
        

        verdict = resume_analysis.get('verdict', 'Low')
        verdict_multiplier = {
            'High': 1.2,
            'Medium': 1.0,
            'Low': 0.8
        }.get(verdict, 0.8)
        
        probability = (base_prob - missing_penalty) * verdict_multiplier
        return max(0, min(probability, 100))
        
    except Exception as e:
        logger.error(f"Error calculating interview probability: {e}")
        return 0

def calculate_hiring_likelihood(resume_analysis: Dict, jd_analysis: Dict, base_score: float) -> float:
    """Calculate hiring likelihood."""
    try:

        likelihood = base_score * 0.7
        

        final_score = resume_analysis.get('final_score', 0)
        match_bonus = final_score * 0.3
        

        industry_multiplier = get_industry_multiplier(jd_analysis)
        
        likelihood = (likelihood + match_bonus) * industry_multiplier
        return max(0, min(likelihood, 100))
        
    except Exception as e:
        logger.error(f"Error calculating hiring likelihood: {e}")
        return 0

def calculate_confidence_level(resume_analysis: Dict, jd_analysis: Dict) -> str:
    """Calculate confidence level in the prediction."""
    try:
        confidence_score = 0
        

        if resume_analysis.get('final_score', 0) > 70:
            confidence_score += 30
        elif resume_analysis.get('final_score', 0) > 50:
            confidence_score += 20
        else:
            confidence_score += 10
        

        missing_skills = resume_analysis.get('missing_skills', [])
        if len(missing_skills) <= 3:
            confidence_score += 25
        elif len(missing_skills) <= 5:
            confidence_score += 15
        else:
            confidence_score += 5
        

        if jd_analysis and len(jd_analysis.get('must_have', [])) >= 3:
            confidence_score += 25
        else:
            confidence_score += 10
        

        hard_score = resume_analysis.get('hard_pct', 0)
        soft_score = resume_analysis.get('soft_pct', 0)
        if abs(hard_score - soft_score) < 20:
            confidence_score += 20
        else:
            confidence_score += 10
        
        if confidence_score >= 80:
            return 'High'
        elif confidence_score >= 60:
            return 'Medium'
        else:
            return 'Low'
            
    except Exception as e:
        logger.error(f"Error calculating confidence level: {e}")
        return 'Low'

def estimate_projects_score(resume_analysis: Dict) -> float:
    """Estimate projects/portfolio score from resume analysis."""
    try:


        final_score = resume_analysis.get('final_score', 0)
        
        if final_score >= 80:
            return 85
        elif final_score >= 60:
            return 70
        else:
            return 50
            
    except Exception as e:
        logger.error(f"Error estimating projects score: {e}")
        return 50

def estimate_education_score(resume_analysis: Dict) -> float:
    """Estimate education score from resume analysis."""
    try:

        final_score = resume_analysis.get('final_score', 0)
        
        if final_score >= 80:
            return 90
        elif final_score >= 60:
            return 75
        else:
            return 60
            
    except Exception as e:
        logger.error(f"Error estimating education score: {e}")
        return 60

def estimate_certifications_score(resume_analysis: Dict) -> float:
    """Estimate certifications score from resume analysis."""
    try:


        final_score = resume_analysis.get('final_score', 0)
        
        if final_score >= 80:
            return 80
        elif final_score >= 60:
            return 65
        else:
            return 50
            
    except Exception as e:
        logger.error(f"Error estimating certifications score: {e}")
        return 50

def get_industry_multiplier(jd_analysis: Dict) -> float:
    """Get industry-specific multiplier for hiring likelihood."""
    try:
        if not jd_analysis:
            return 1.0
        

        must_have = jd_analysis.get('must_have', [])
        

        tech_keywords = ['python', 'java', 'javascript', 'machine learning', 'data science']
        if any(keyword.lower() in ' '.join(must_have).lower() for keyword in tech_keywords):
            return 1.1
        

        finance_keywords = ['finance', 'accounting', 'cfa', 'cpa', 'financial modeling']
        if any(keyword.lower() in ' '.join(must_have).lower() for keyword in finance_keywords):
            return 1.05
        
        return 1.0
        
    except Exception as e:
        logger.error(f"Error getting industry multiplier: {e}")
        return 1.0

def get_performance_grade(score: float) -> str:
    """Get performance grade from score."""
    if score >= 85:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 75:
        return 'A-'
    elif score >= 70:
        return 'B+'
    elif score >= 65:
        return 'B'
    elif score >= 60:
        return 'B-'
    elif score >= 55:
        return 'C+'
    elif score >= 50:
        return 'C'
    else:
        return 'D'

def generate_performance_insights(resume_analysis: Dict, base_score: float, industry: str) -> List[str]:
    """Generate performance insights."""
    insights = []
    
    try:

        if base_score >= 80:
            insights.append("Excellent candidate with high potential for success")
        elif base_score >= 70:
            insights.append("Strong candidate with good potential")
        elif base_score >= 60:
            insights.append("Average candidate with room for improvement")
        else:
            insights.append("Candidate needs significant development")
        

        missing_skills = resume_analysis.get('missing_skills', [])
        if len(missing_skills) <= 2:
            insights.append("Well-rounded candidate with minimal skill gaps")
        elif len(missing_skills) <= 4:
            insights.append("Good candidate with some skill gaps to address")
        else:
            insights.append("Candidate has significant skill gaps")
        

        if industry == 'technology':
            insights.append("Consider technical interview to assess coding skills")
        elif industry == 'finance':
            insights.append("Consider case study or financial modeling assessment")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error generating performance insights: {e}")
        return ['Error generating insights']

def generate_performance_recommendations(resume_analysis: Dict, factors: Dict) -> List[str]:
    """Generate performance improvement recommendations."""
    recommendations = []
    
    try:

        final_score = resume_analysis.get('final_score', 0)
        
        if final_score < 70:
            recommendations.append("Focus on developing core skills mentioned in job description")
        

        missing_skills = resume_analysis.get('missing_skills', [])
        if missing_skills:
            recommendations.append(f"Prioritize learning: {', '.join(missing_skills[:3])}")
        

        if 'projects_weight' in factors:
            recommendations.append("Build and showcase relevant projects")
        
        if 'certifications_weight' in factors:
            recommendations.append("Consider obtaining industry certifications")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating performance recommendations: {e}")
        return ['Error generating recommendations']


def test_performance_predictor():
    """Test performance predictor with sample data."""
    sample_resume = {
        'final_score': 75,
        'hard_pct': 80,
        'soft_pct': 70,
        'verdict': 'High',
        'missing_skills': ['AWS', 'Docker']
    }
    
    sample_jd = {
        'must_have': ['Python', 'Machine Learning', 'SQL'],
        'good_to_have': ['AWS', 'Docker', 'Git']
    }
    
    prediction = predict_performance(sample_resume, sample_jd, 'technology')
    print("Performance Prediction:")
    print(f"Base Score: {prediction['base_performance_score']}")
    print(f"Interview Probability: {prediction['interview_probability']}%")
    print(f"Hiring Likelihood: {prediction['hiring_likelihood']}%")

if __name__ == "__main__":
    test_performance_predictor()