"""
Feedback generation module using Grok API.
Generates personalized improvement suggestions for resumes.
"""

import json
from typing import Dict, List, Optional
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_feedback(jd_text: str, resume_text: str, missing_skills: List[str]) -> str:
    """
    Generate one-line improvement feedback for a resume.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
        missing_skills: List of missing skills
    
    Returns:
        Feedback string
    """
    try:

        ai_feedback = generate_ai_feedback(jd_text, resume_text, missing_skills)
        if ai_feedback and ai_feedback != "Mock response: Please configure GROK_API_KEY in .env file":
            return ai_feedback
        

        return generate_template_feedback(missing_skills)
        
    except Exception as e:
        logger.error(f"Error generating feedback: {e}")
        return generate_template_feedback(missing_skills)

def generate_ai_feedback(jd_text: str, resume_text: str, missing_skills: List[str]) -> str:
    """
    Generate feedback using AI (Grok API).
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
        missing_skills: List of missing skills
    
    Returns:
        AI-generated feedback
    """
    try:
        from .grok_client import grok_generate
        
        prompt = f"""You are an admissions coach. Provide a one-line suggestion to improve a resume given a JD and detected missing skills.

JD: {jd_text[:500]}

Resume text: {resume_text[:500]}

Missing skills: {', '.join(missing_skills[:5])}

Produce a single, action-oriented line (imperative) that a candidate can do in 1–4 weeks to improve their fit. Example: "Add a 2-week Kaggle project demonstrating X and host code on GitHub."

Focus on practical, achievable improvements that directly address the missing skills."""

        response = grok_generate(prompt, max_tokens=100, temperature=0.3)
        
        if response.get('ok') and response.get('text'):
            feedback = response['text'].strip()

            feedback = feedback.replace('"', '').replace("'", '')
            if feedback.startswith('"') and feedback.endswith('"'):
                feedback = feedback[1:-1]
            return feedback
        
        return "Unable to generate AI feedback"
        
    except Exception as e:
        logger.error(f"Error with AI feedback generation: {e}")
        return "AI feedback unavailable"

def generate_template_feedback(missing_skills: List[str]) -> str:
    """
    Generate feedback using predefined templates.
    
    Args:
        missing_skills: List of missing skills
    
    Returns:
        Template-based feedback
    """
    if not missing_skills:
        return "Your resume looks strong! Consider adding more specific achievements and metrics."
    

    technical_skills = []
    soft_skills = []
    tools = []
    
    for skill in missing_skills[:3]:
        skill_lower = skill.lower()
        if any(tech in skill_lower for tech in ['python', 'java', 'javascript', 'sql', 'machine learning', 'data']):
            technical_skills.append(skill)
        elif any(tool in skill_lower for tool in ['git', 'docker', 'aws', 'kubernetes', 'jenkins']):
            tools.append(skill)
        else:
            soft_skills.append(skill)
    

    if technical_skills:
        skill = technical_skills[0]
        return f"Complete a 2-week project demonstrating {skill} and showcase it on GitHub with detailed documentation."
    
    elif tools:
        tool = tools[0]
        return f"Set up a personal project using {tool} and document the process to demonstrate hands-on experience."
    
    elif soft_skills:
        skill = soft_skills[0]
        return f"Add a section highlighting {skill} with specific examples from your experience and quantify your impact."
    
    else:
        return f"Focus on developing skills in {', '.join(missing_skills[:2])} through online courses and practical projects."

def generate_detailed_feedback(jd_text: str, resume_text: str, score_result: Dict) -> Dict[str, str]:
    """
    Generate detailed feedback including summary and suggestions.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
        score_result: Scoring results
    
    Returns:
        Dictionary with different types of feedback
    """
    try:
        from .grok_client import grok_generate
        
        missing_skills = score_result.get('missing_skills', [])
        final_score = score_result.get('final_score', 0)
        

        summary_prompt = f"""Summarize the candidate in 2-3 short bullets focusing on relevant experience/skills for the JD.

JD: {jd_text[:300]}

Resume: {resume_text[:500]}

Return a JSON object: {{"summary": ["...","..."], "strengths": ["..."], "weaknesses": ["..."]}}"""

        summary_response = grok_generate(summary_prompt, max_tokens=200, temperature=0.2)
        
        summary_data = {"summary": [], "strengths": [], "weaknesses": []}
        if summary_response.get('ok') and summary_response.get('text'):
            try:
                summary_data = json.loads(summary_response['text'])
            except json.JSONDecodeError:
                logger.warning("Failed to parse summary JSON")
        

        suggestions = generate_improvement_suggestions(missing_skills, final_score)
        
        return {
            "one_line": generate_feedback(jd_text, resume_text, missing_skills),
            "summary": summary_data.get("summary", []),
            "strengths": summary_data.get("strengths", []),
            "weaknesses": summary_data.get("weaknesses", []),
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Error generating detailed feedback: {e}")
        return {
            "one_line": generate_template_feedback(missing_skills),
            "summary": ["Unable to generate summary"],
            "strengths": [],
            "weaknesses": missing_skills,
            "suggestions": []
        }

def generate_improvement_suggestions(missing_skills: List[str], final_score: float) -> List[str]:
    """
    Generate specific improvement suggestions.
    
    Args:
        missing_skills: List of missing skills
        final_score: Final relevance score
    
    Returns:
        List of improvement suggestions
    """
    suggestions = []
    
    if final_score < 30:
        suggestions.append("Consider a complete resume overhaul focusing on relevant skills and experience")
    elif final_score < 60:
        suggestions.append("Add more relevant projects and quantify your achievements")
    
    if missing_skills:

        tech_skills = [s for s in missing_skills if any(tech in s.lower() for tech in ['python', 'java', 'sql', 'machine learning'])]
        if tech_skills:
            suggestions.append(f"Complete online courses in {', '.join(tech_skills[:2])} and build projects")
        

        tools = [s for s in missing_skills if any(tool in s.lower() for tool in ['git', 'docker', 'aws', 'kubernetes'])]
        if tools:
            suggestions.append(f"Get hands-on experience with {', '.join(tools[:2])} through personal projects")
        

        soft_skills = [s for s in missing_skills if s not in tech_skills and s not in tools]
        if soft_skills:
            suggestions.append(f"Highlight {', '.join(soft_skills[:2])} with specific examples and metrics")
    
    if not suggestions:
        suggestions.append("Add more specific achievements and quantify your impact")
    
    return suggestions[:3]

def generate_resume_summary(jd_text: str, resume_text: str) -> Dict[str, List[str]]:
    """
    Generate resume summary for the JD.
    
    Args:
        jd_text: Job description text
        resume_text: Resume text
    
    Returns:
        Dictionary with summary, strengths, and weaknesses
    """
    try:
        from .grok_client import grok_generate
        
        prompt = f"""Summarize the candidate in 2-3 short bullets focusing on relevant experience/skills for the JD.

JD: {jd_text[:300]}

Resume: {resume_text[:500]}

Return a JSON object: {{"summary": ["...","..."], "strengths": ["..."], "weaknesses": ["..."]}}"""

        response = grok_generate(prompt, max_tokens=200, temperature=0.2)
        
        if response.get('ok') and response.get('text'):
            try:
                return json.loads(response['text'])
            except json.JSONDecodeError:
                logger.warning("Failed to parse summary JSON")
        
        return {"summary": [], "strengths": [], "weaknesses": []}
        
    except Exception as e:
        logger.error(f"Error generating resume summary: {e}")
        return {"summary": [], "strengths": [], "weaknesses": []}


def test_feedback():
    """Test feedback generation."""
    sample_jd = "We need a Python developer with machine learning experience."
    sample_resume = "I am a software developer with 2 years of experience."
    missing_skills = ["Python", "Machine Learning", "Pandas"]
    
    feedback = generate_feedback(sample_jd, sample_resume, missing_skills)
    print(f"Generated feedback: {feedback}")
    
    detailed = generate_detailed_feedback(sample_jd, sample_resume, {
        "missing_skills": missing_skills,
        "final_score": 45
    })
    print(f"Detailed feedback: {detailed}")

if __name__ == "__main__":
    test_feedback()