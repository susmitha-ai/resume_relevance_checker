"""
ATS (Applicant Tracking System) Score Calculator
Analyzes resume compatibility with ATS systems and provides industry benchmarks.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ATS_RULES = {
    'contact_info': {
        'phone_pattern': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        'email_pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'linkedin_pattern': r'linkedin\.com/in/[\w-]+',
        'github_pattern': r'github\.com/[\w-]+'
    },
    'sections': {
        'required': ['experience', 'education', 'skills'],
        'preferred': ['summary', 'projects', 'certifications', 'achievements']
    },
    'keywords': {
        'action_verbs': [
            'achieved', 'developed', 'implemented', 'managed', 'led', 'created',
            'designed', 'built', 'improved', 'increased', 'reduced', 'optimized',
            'collaborated', 'coordinated', 'delivered', 'executed', 'facilitated'
        ],
        'quantifiers': [
            'increased', 'decreased', 'improved', 'reduced', 'saved', 'generated',
            'managed', 'led', 'supervised', 'trained', 'mentored'
        ]
    }
}


INDUSTRY_BENCHMARKS = {
    'technology': {'excellent': 85, 'good': 70, 'average': 55},
    'finance': {'excellent': 80, 'good': 65, 'average': 50},
    'healthcare': {'excellent': 82, 'good': 67, 'average': 52},
    'education': {'excellent': 78, 'good': 63, 'average': 48},
    'marketing': {'excellent': 80, 'good': 65, 'average': 50},
    'default': {'excellent': 80, 'good': 65, 'average': 50}
}

def calculate_ats_score(resume_text: str, industry: str = 'default') -> Dict[str, any]:
    """
    Calculate comprehensive ATS score for a resume.
    
    Args:
        resume_text: Extracted resume text
        industry: Industry type for benchmarking
    
    Returns:
        Dictionary with ATS score and detailed analysis
    """
    try:

        formatting_score = calculate_formatting_score(resume_text)
        

        content_score = calculate_content_score(resume_text)
        

        keyword_score = calculate_keyword_score(resume_text)
        

        contact_score = calculate_contact_score(resume_text)
        

        section_score = calculate_section_score(resume_text)
        

        ats_score = (
            formatting_score * 0.25 +
            content_score * 0.30 +
            keyword_score * 0.20 +
            contact_score * 0.15 +
            section_score * 0.10
        )
        

        benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS['default'])
        

        if ats_score >= benchmarks['excellent']:
            ats_grade = 'Excellent'
        elif ats_score >= benchmarks['good']:
            ats_grade = 'Good'
        elif ats_score >= benchmarks['average']:
            ats_grade = 'Average'
        else:
            ats_grade = 'Needs Improvement'
        

        suggestions = generate_ats_suggestions(
            formatting_score, content_score, keyword_score, 
            contact_score, section_score
        )
        
        return {
            'ats_score': round(ats_score, 1),
            'ats_grade': ats_grade,
            'industry_benchmark': benchmarks,
            'detailed_scores': {
                'formatting': formatting_score,
                'content': content_score,
                'keywords': keyword_score,
                'contact': contact_score,
                'sections': section_score
            },
            'suggestions': suggestions,
            'industry': industry
        }
        
    except Exception as e:
        logger.error(f"Error calculating ATS score: {e}")
        return {
            'ats_score': 0,
            'ats_grade': 'Error',
            'industry_benchmark': INDUSTRY_BENCHMARKS['default'],
            'detailed_scores': {},
            'suggestions': ['Error in ATS analysis'],
            'industry': industry
        }

def calculate_formatting_score(resume_text: str) -> float:
    """Calculate formatting compatibility score."""
    score = 0
    max_score = 100
    

    lines = resume_text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    if len(non_empty_lines) > 10:
        score += 20
    

    bullet_count = sum(1 for line in non_empty_lines if line.startswith(('•', '-', '*', '◦')))
    if bullet_count > 5:
        score += 20
    

    section_headers = sum(1 for line in non_empty_lines if line.isupper() and len(line) > 3)
    if section_headers >= 3:
        score += 20
    

    date_pattern = r'\b(19|20)\d{2}\b'
    dates = re.findall(date_pattern, resume_text)
    if len(dates) >= 2:
        score += 20
    

    number_pattern = r'\b\d+%|\$\d+|\d+\+|\d+x\b'
    numbers = re.findall(number_pattern, resume_text)
    if len(numbers) >= 3:
        score += 20
    
    return min(score, max_score)

def calculate_content_score(resume_text: str) -> float:
    """Calculate content completeness score."""
    score = 0
    max_score = 100
    

    required_sections = ATS_RULES['sections']['required']
    found_sections = 0
    
    for section in required_sections:
        if section.lower() in resume_text.lower():
            found_sections += 1
    
    score += (found_sections / len(required_sections)) * 40
    

    preferred_sections = ATS_RULES['sections']['preferred']
    found_preferred = 0
    
    for section in preferred_sections:
        if section.lower() in resume_text.lower():
            found_preferred += 1
    
    score += (found_preferred / len(preferred_sections)) * 30
    

    experience_indicators = ['experience', 'work', 'employment', 'career']
    has_experience = any(indicator in resume_text.lower() for indicator in experience_indicators)
    if has_experience:
        score += 30
    
    return min(score, max_score)

def calculate_keyword_score(resume_text: str) -> float:
    """Calculate keyword optimization score."""
    score = 0
    max_score = 100
    

    action_verbs = ATS_RULES['keywords']['action_verbs']
    found_verbs = sum(1 for verb in action_verbs if verb.lower() in resume_text.lower())
    score += min(found_verbs * 5, 40)
    

    quantifiers = ATS_RULES['keywords']['quantifiers']
    found_quantifiers = sum(1 for q in quantifiers if q.lower() in resume_text.lower())
    score += min(found_quantifiers * 5, 30)
    

    tech_keywords = ['python', 'java', 'sql', 'machine learning', 'data analysis', 'project management']
    found_tech = sum(1 for tech in tech_keywords if tech.lower() in resume_text.lower())
    score += min(found_tech * 3, 30)
    
    return min(score, max_score)

def calculate_contact_score(resume_text: str) -> float:
    """Calculate contact information completeness score."""
    score = 0
    max_score = 100
    

    phone_pattern = ATS_RULES['contact_info']['phone_pattern']
    if re.search(phone_pattern, resume_text):
        score += 25
    

    email_pattern = ATS_RULES['contact_info']['email_pattern']
    if re.search(email_pattern, resume_text):
        score += 25
    

    linkedin_pattern = ATS_RULES['contact_info']['linkedin_pattern']
    if re.search(linkedin_pattern, resume_text):
        score += 25
    

    github_pattern = ATS_RULES['contact_info']['github_pattern']
    if re.search(github_pattern, resume_text):
        score += 25
    
    return min(score, max_score)

def calculate_section_score(resume_text: str) -> float:
    """Calculate section organization score."""
    score = 0
    max_score = 100
    

    section_headers = ['experience', 'education', 'skills', 'summary', 'objective']
    found_headers = sum(1 for header in section_headers if header.lower() in resume_text.lower())
    score += min(found_headers * 15, 60)
    

    date_pattern = r'\b(19|20)\d{2}\b'
    dates = re.findall(date_pattern, resume_text)
    if len(dates) >= 2:

        try:
            date_values = [int(date) for date in dates]
            if max(date_values) - min(date_values) > 0:
                score += 20
        except:
            pass
    

    lines = resume_text.split('\n')
    formatted_lines = [line.strip() for line in lines if line.strip()]
    if len(formatted_lines) > 10:
        score += 20
    
    return min(score, max_score)

def generate_ats_suggestions(formatting_score: float, content_score: float, 
                           keyword_score: float, contact_score: float, 
                           section_score: float) -> List[str]:
    """Generate specific ATS improvement suggestions."""
    suggestions = []
    
    if formatting_score < 70:
        suggestions.append("Improve resume formatting with consistent bullet points and clear section headers")
    
    if content_score < 70:
        suggestions.append("Add missing sections like Experience, Education, and Skills")
    
    if keyword_score < 70:
        suggestions.append("Include more action verbs and quantified achievements")
    
    if contact_score < 70:
        suggestions.append("Add complete contact information including phone, email, and LinkedIn")
    
    if section_score < 70:
        suggestions.append("Organize content into clear sections with proper headers")
    
    if not suggestions:
        suggestions.append("Your resume has excellent ATS compatibility!")
    
    return suggestions

def compare_ats_scores(resume_scores: List[Dict]) -> Dict[str, any]:
    """Compare ATS scores across multiple resumes."""
    if not resume_scores:
        return {}
    
    scores = [score.get('ats_score', 0) for score in resume_scores]
    
    return {
        'average_score': sum(scores) / len(scores),
        'highest_score': max(scores),
        'lowest_score': min(scores),
        'score_distribution': {
            'excellent': sum(1 for s in scores if s >= 85),
            'good': sum(1 for s in scores if 70 <= s < 85),
            'average': sum(1 for s in scores if 55 <= s < 70),
            'needs_improvement': sum(1 for s in scores if s < 55)
        }
    }


def test_ats_analyzer():
    """Test ATS analyzer with sample resume."""
    sample_resume = """
    John Doe
    Software Engineer
    Phone: (555) 123-4567
    Email: john.doe@email.com
    LinkedIn: linkedin.com/in/johndoe
    
    EXPERIENCE
    • Developed web applications using Python and Django
    • Increased system performance by 30%
    • Led a team of 5 developers
    • Managed database optimization projects
    
    EDUCATION
    • Bachelor of Computer Science, University XYZ (2018-2022)
    
    SKILLS
    • Python, Java, SQL, Machine Learning
    • Project Management, Team Leadership
    """
    
    result = calculate_ats_score(sample_resume, 'technology')
    print("ATS Analysis Results:")
    print(f"Score: {result['ats_score']}")
    print(f"Grade: {result['ats_grade']}")
    print(f"Suggestions: {result['suggestions']}")

if __name__ == "__main__":
    test_ats_analyzer()