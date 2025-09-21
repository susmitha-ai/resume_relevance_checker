"""
Skill extraction module for job descriptions.
Extracts must-have and good-to-have skills using AI and keyword matching.
"""

import json
import re
from typing import Dict, List, Optional
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TECH_SKILLS_DB = {
    'programming': [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby',
        'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css', 'react', 'angular',
        'vue', 'node.js', 'django', 'flask', 'spring', 'express', 'laravel', 'rails'
    ],
    'databases': [
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 'dynamodb',
        'sqlite', 'oracle', 'sql server', 'neo4j', 'influxdb'
    ],
    'cloud': [
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
        'gitlab ci', 'github actions', 'cloudformation', 'serverless', 'lambda'
    ],
    'data_science': [
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'pandas', 'numpy',
        'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'spark', 'hadoop', 'kafka',
        'airflow', 'jupyter', 'matplotlib', 'seaborn', 'plotly'
    ],
    'tools': [
        'git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'teams', 'figma', 'sketch',
        'postman', 'swagger', 'docker', 'kubernetes', 'vagrant', 'virtualbox'
    ],
    'methodologies': [
        'agile', 'scrum', 'kanban', 'devops', 'ci/cd', 'tdd', 'bdd', 'microservices',
        'rest api', 'graphql', 'soa', 'mvc', 'mvp', 'mvvm'
    ]
}

def extract_skills_from_jd(jd_text: str, use_ai: bool = True) -> Dict[str, List[str]]:
    """
    Extract must-have and good-to-have skills from job description.
    
    Args:
        jd_text: Job description text
        use_ai: Whether to use AI for extraction (requires Grok API)
    
    Returns:
        Dictionary with 'must_have' and 'good_to_have' skill lists
    """
    if not jd_text or not jd_text.strip():
        return {"must_have": [], "good_to_have": []}
    
    try:
        if use_ai:

            ai_skills = extract_skills_with_ai(jd_text)
            if ai_skills and ai_skills.get('must_have'):
                return ai_skills
            else:
                logger.warning("AI extraction failed, falling back to keyword matching")
        

        return extract_skills_with_keywords(jd_text)
        
    except Exception as e:
        logger.error(f"Error extracting skills: {e}")

        return extract_skills_with_keywords(jd_text)

def extract_skills_with_ai(jd_text: str) -> Dict[str, List[str]]:
    """
    Extract skills using AI (Grok API).
    
    Args:
        jd_text: Job description text
    
    Returns:
        Dictionary with extracted skills
    """
    try:
        from .grok_client import grok_generate
        
        prompt = f"""You are a hiring-assistant that extracts concise skill lists for resumes. Output JSON with two arrays: "must_have" and "good_to_have".

Given this job description, extract:
- 5 must-have skills (technical skills or qualifications that are required)
- 8 good-to-have skills (beneficial but not required)
Return output as strict JSON only.

Job Description:
{jd_text}

Expected output format:
{{"must_have": ["Python", "SQL", "Machine Learning", "Pandas", "Data Modeling"],
 "good_to_have": ["TensorFlow", "AWS", "Spark", "Tableau", "Git", "Docker", "NLP", "communication"]}}"""

        response = grok_generate(prompt, max_tokens=300, temperature=0.2)
        
        if response.get('ok') and response.get('text'):

            try:
                skills_data = json.loads(response['text'])
                if isinstance(skills_data, dict) and 'must_have' in skills_data:
                    return {
                        'must_have': skills_data.get('must_have', [])[:5],
                        'good_to_have': skills_data.get('good_to_have', [])[:8]
                    }
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON")
        
        return {"must_have": [], "good_to_have": []}
        
    except Exception as e:
        logger.error(f"AI skill extraction failed: {e}")
        return {"must_have": [], "good_to_have": []}

def extract_skills_with_keywords(jd_text: str) -> Dict[str, List[str]]:
    """
    Extract skills using enhanced keyword matching and heuristics.
    
    Args:
        jd_text: Job description text
    
    Returns:
        Dictionary with extracted skills
    """

    text_lower = jd_text.lower()
    

    mentioned_skills = []
    for category, skills in TECH_SKILLS_DB.items():
        for skill in skills:
            if skill.lower() in text_lower:
                mentioned_skills.append(skill.title())
    
    # Enhanced keyword extraction
    additional_keywords = extract_additional_keywords(jd_text)
    mentioned_skills.extend(additional_keywords)
    

    mentioned_skills = list(set(mentioned_skills))
    

    must_have_keywords = [
        'required', 'must have', 'essential', 'mandatory', 'necessary',
        'prerequisite', 'minimum', 'at least', 'should have', 'need',
        'critical', 'important', 'key', 'core', 'fundamental'
    ]
    
    good_to_have_keywords = [
        'preferred', 'nice to have', 'bonus', 'advantage', 'plus',
        'desirable', 'beneficial', 'helpful', 'would be great',
        'optional', 'additional', 'extra', 'welcome'
    ]
    
    must_have = []
    good_to_have = []
    

    sentences = re.split(r'[.!?]+', jd_text)
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        

        is_must_have = any(keyword in sentence_lower for keyword in must_have_keywords)
        is_good_to_have = any(keyword in sentence_lower for keyword in good_to_have_keywords)
        

        for skill in mentioned_skills:
            if skill.lower() in sentence_lower:
                if is_must_have and not is_good_to_have:
                    if skill not in must_have:
                        must_have.append(skill)
                elif is_good_to_have:
                    if skill not in good_to_have:
                        good_to_have.append(skill)
    

    if not must_have and not good_to_have:

        must_have = mentioned_skills[:5]
        good_to_have = mentioned_skills[5:13]
    

    if len(must_have) < 3:

        common_skills = ['Communication', 'Problem Solving', 'Teamwork']
        for skill in common_skills:
            if skill not in must_have and len(must_have) < 5:
                must_have.append(skill)
    
    return {
        'must_have': must_have[:5],
        'good_to_have': good_to_have[:8]
    }

def extract_skills_from_resume(resume_text: str) -> List[str]:
    """
    Extract skills mentioned in resume text.
    
    Args:
        resume_text: Resume text
    
    Returns:
        List of mentioned skills
    """
    if not resume_text:
        return []
    
    text_lower = resume_text.lower()
    mentioned_skills = []
    

    for category, skills in TECH_SKILLS_DB.items():
        for skill in skills:
            if skill.lower() in text_lower:
                mentioned_skills.append(skill.title())
    

    return list(set(mentioned_skills))

def calculate_skill_match(resume_skills: List[str], jd_skills: Dict[str, List[str]]) -> Dict[str, any]:
    """
    Calculate skill matching statistics.
    
    Args:
        resume_skills: Skills found in resume
        jd_skills: Required skills from JD
    
    Returns:
        Dictionary with match statistics
    """
    must_have = [skill.lower() for skill in jd_skills.get('must_have', [])]
    good_to_have = [skill.lower() for skill in jd_skills.get('good_to_have', [])]
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    

    must_have_matches = [skill for skill in must_have if skill in resume_skills_lower]
    good_to_have_matches = [skill for skill in good_to_have if skill in resume_skills_lower]
    

    missing_must_have = [skill for skill in must_have if skill not in resume_skills_lower]
    missing_good_to_have = [skill for skill in good_to_have if skill not in resume_skills_lower]
    
    return {
        'must_have_matches': must_have_matches,
        'good_to_have_matches': good_to_have_matches,
        'missing_must_have': missing_must_have,
        'missing_good_to_have': missing_good_to_have,
        'must_have_score': len(must_have_matches) / len(must_have) if must_have else 0,
        'good_to_have_score': len(good_to_have_matches) / len(good_to_have) if good_to_have else 0
    }


def test_skill_extraction():
    """Test skill extraction with sample JD."""
    sample_jd = """
    We are looking for a Senior Data Scientist with the following requirements:
    
    Required Skills:
    - Python programming (3+ years)
    - Machine Learning and Deep Learning
    - SQL and database management
    - Statistical analysis
    - Must have experience with pandas and numpy
    
    Preferred Skills:
    - TensorFlow or PyTorch
    - AWS or cloud platforms
    - Docker and Kubernetes
    - Git version control
    - Strong communication skills
    """
    
    skills = extract_skills_from_jd(sample_jd)
    print("Extracted Skills:")
    print(f"Must Have: {skills['must_have']}")
    print(f"Good to Have: {skills['good_to_have']}")

def extract_additional_keywords(jd_text: str) -> List[str]:
    """
    Extract additional keywords and skills from job description.
    
    Args:
        jd_text: Job description text
    
    Returns:
        List of additional keywords found
    """
    keywords = []
    text_lower = jd_text.lower()
    
    # Common technical terms and frameworks
    tech_patterns = [
        r'\b(?:react|angular|vue|node\.?js|express|django|flask|spring|laravel)\b',
        r'\b(?:aws|azure|gcp|docker|kubernetes|jenkins|git|github|gitlab)\b',
        r'\b(?:sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
        r'\b(?:python|java|javascript|typescript|c\+\+|c#|go|rust|php|ruby)\b',
        r'\b(?:machine learning|ml|ai|artificial intelligence|deep learning|nlp)\b',
        r'\b(?:agile|scrum|kanban|devops|ci/cd|microservices|api|rest|graphql)\b',
        r'\b(?:tableau|power bi|excel|sql server|oracle|sap|salesforce)\b',
        r'\b(?:linux|unix|windows|macos|bash|powershell|shell scripting)\b'
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        keywords.extend([match.title() for match in matches])
    
    # Extract capitalized words (likely proper nouns/skills)
    capitalized_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', jd_text)
    keywords.extend(capitalized_words)
    
    # Extract words with numbers (versions, years)
    version_patterns = re.findall(r'\b\w+\s*\d+(?:\.\d+)*\b', jd_text, re.IGNORECASE)
    keywords.extend(version_patterns)
    
    # Remove common words and duplicates
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'a', 'an'}
    keywords = [kw for kw in keywords if kw.lower() not in common_words and len(kw) > 2]
    
    return list(set(keywords))

if __name__ == "__main__":
    test_skill_extraction()