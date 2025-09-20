"""
Resume Comparison Dashboard
Provides side-by-side comparison of multiple resumes with advanced analytics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import json


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compare_resumes(resume_results: List[Dict], jd_text: str) -> Dict[str, any]:
    """
    Compare multiple resumes against a job description.
    
    Args:
        resume_results: List of resume analysis results
        jd_text: Job description text
    
    Returns:
        Comprehensive comparison analysis
    """
    try:
        if not resume_results:
            return {}
        

        comparison = {
            'total_resumes': len(resume_results),
            'comparison_date': datetime.now().isoformat(),
            'job_description': jd_text[:200] + "..." if len(jd_text) > 200 else jd_text
        }
        

        scores = [result.get('final_score', 0) for result in resume_results]
        comparison['score_analysis'] = {
            'average_score': round(np.mean(scores), 2),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'score_std': round(np.std(scores), 2),
            'score_range': max(scores) - min(scores)
        }
        

        ranked_resumes = sorted(resume_results, key=lambda x: x.get('final_score', 0), reverse=True)
        comparison['rankings'] = [
            {
                'rank': i + 1,
                'resume_file': result.get('resume_file', 'Unknown'),
                'final_score': result.get('final_score', 0),
                'verdict': result.get('verdict', 'Unknown'),
                'hard_pct': result.get('hard_pct', 0),
                'soft_pct': result.get('soft_pct', 0)
            }
            for i, result in enumerate(ranked_resumes)
        ]
        

        verdicts = [result.get('verdict', 'Unknown') for result in resume_results]
        comparison['verdict_distribution'] = {
            verdict: verdicts.count(verdict) for verdict in set(verdicts)
        }
        

        all_missing_skills = []
        for result in resume_results:
            missing_skills = result.get('missing_skills', [])
            all_missing_skills.extend(missing_skills)
        
        if all_missing_skills:
            skill_counts = {}
            for skill in all_missing_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            comparison['common_missing_skills'] = sorted(
                skill_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        

        comparison['insights'] = generate_comparison_insights(resume_results, scores)
        

        comparison['recommendations'] = generate_comparison_recommendations(resume_results)
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing resumes: {e}")
        return {}

def generate_comparison_insights(resume_results: List[Dict], scores: List[float]) -> List[str]:
    """Generate insights from resume comparison."""
    insights = []
    
    if not resume_results:
        return insights
    

    high_scores = [s for s in scores if s >= 75]
    medium_scores = [s for s in scores if 45 <= s < 75]
    low_scores = [s for s in scores if s < 45]
    
    if len(high_scores) > len(resume_results) * 0.3:
        insights.append(f"Strong candidate pool: {len(high_scores)} resumes scored 75+")
    elif len(high_scores) == 0:
        insights.append("No high-scoring candidates found - consider revising job requirements")
    
    if len(low_scores) > len(resume_results) * 0.5:
        insights.append(f"Many candidates need improvement: {len(low_scores)} scored below 45")
    

    score_std = np.std(scores)
    if score_std < 10:
        insights.append("Low score variance - candidates are similarly qualified")
    elif score_std > 25:
        insights.append("High score variance - significant differences in candidate quality")
    

    all_missing = []
    for result in resume_results:
        all_missing.extend(result.get('missing_skills', []))
    
    if all_missing:
        common_missing = max(set(all_missing), key=all_missing.count)
        insights.append(f"Most common missing skill: {common_missing}")
    
    return insights

def generate_comparison_recommendations(resume_results: List[Dict]) -> List[str]:
    """Generate recommendations based on comparison."""
    recommendations = []
    
    if not resume_results:
        return recommendations
    

    top_resume = max(resume_results, key=lambda x: x.get('final_score', 0))
    top_score = top_resume.get('final_score', 0)
    
    if top_score >= 80:
        recommendations.append("Consider the top candidate for immediate interview")
    elif top_score >= 60:
        recommendations.append("Top candidate shows promise - schedule interview")
    else:
        recommendations.append("Consider revising job requirements or candidate criteria")
    

    all_missing = []
    for result in resume_results:
        all_missing.extend(result.get('missing_skills', []))
    
    if all_missing:
        unique_missing = set(all_missing)
        if len(unique_missing) > 5:
            recommendations.append("Consider providing training for common missing skills")
    

    verdicts = [result.get('verdict', 'Unknown') for result in resume_results]
    if verdicts.count('High') < len(resume_results) * 0.2:
        recommendations.append("Consider expanding candidate search or adjusting requirements")
    
    return recommendations

def create_comparison_dataframe(resume_results: List[Dict]) -> pd.DataFrame:
    """Create a comparison DataFrame for visualization."""
    if not resume_results:
        return pd.DataFrame()
    
    data = []
    for result in resume_results:
        data.append({
            'Resume': result.get('resume_file', 'Unknown'),
            'Final Score': result.get('final_score', 0),
            'Hard Match %': result.get('hard_pct', 0),
            'Soft Match %': result.get('soft_pct', 0),
            'Verdict': result.get('verdict', 'Unknown'),
            'Missing Skills Count': len(result.get('missing_skills', [])),
            'Missing Skills': ', '.join(result.get('missing_skills', [])[:3])
        })
    
    return pd.DataFrame(data)

def calculate_resume_similarity(resume_texts: List[str]) -> Dict[str, any]:
    """Calculate similarity between resumes."""
    try:
        from .embeddings import get_embeddings, calculate_similarity
        
        if len(resume_texts) < 2:
            return {}
        

        embeddings = get_embeddings(resume_texts)
        

        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = calculate_similarity(embeddings[i], embeddings[j])
                similarities.append({
                    'resume_1': i,
                    'resume_2': j,
                    'similarity': similarity
                })
        
        return {
            'average_similarity': np.mean([s['similarity'] for s in similarities]),
            'max_similarity': max([s['similarity'] for s in similarities]),
            'min_similarity': min([s['similarity'] for s in similarities]),
            'pairwise_similarities': similarities
        }
        
    except Exception as e:
        logger.error(f"Error calculating resume similarity: {e}")
        return {}

def generate_comparison_report(resume_results: List[Dict], jd_text: str) -> str:
    """Generate a comprehensive comparison report."""
    try:
        comparison = compare_resumes(resume_results, jd_text)
        
        report = f"""

Generated: {comparison.get('comparison_date', 'Unknown')}


- Total Resumes Analyzed: {comparison.get('total_resumes', 0)}
- Average Score: {comparison.get('score_analysis', {}).get('average_score', 0):.1f}%
- Score Range: {comparison.get('score_analysis', {}).get('lowest_score', 0):.1f}% - {comparison.get('score_analysis', {}).get('highest_score', 0):.1f}%


"""
        
        rankings = comparison.get('rankings', [])
        for i, candidate in enumerate(rankings[:5]):
            report += f"""
{i+1}. {candidate.get('resume_file', 'Unknown')}
   - Score: {candidate.get('final_score', 0):.1f}%
   - Verdict: {candidate.get('verdict', 'Unknown')}
   - Hard Match: {candidate.get('hard_pct', 0):.1f}%
   - Soft Match: {candidate.get('soft_pct', 0):.1f}%
"""
        

        insights = comparison.get('insights', [])
        if insights:
            report += "\n## Key Insights\n"
            for insight in insights:
                report += f"- {insight}\n"
        

        recommendations = comparison.get('recommendations', [])
        if recommendations:
            report += "\n## Recommendations\n"
            for rec in recommendations:
                report += f"- {rec}\n"
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating comparison report: {e}")
        return "Error generating comparison report"


def test_resume_comparator():
    """Test resume comparator with sample data."""
    sample_results = [
        {
            'resume_file': 'resume1.pdf',
            'final_score': 85,
            'verdict': 'High',
            'hard_pct': 80,
            'soft_pct': 90,
            'missing_skills': ['AWS', 'Docker']
        },
        {
            'resume_file': 'resume2.pdf',
            'final_score': 65,
            'verdict': 'Medium',
            'hard_pct': 70,
            'soft_pct': 60,
            'missing_skills': ['Python', 'Machine Learning']
        }
    ]
    
    comparison = compare_resumes(sample_results, "Python developer with ML experience")
    print("Comparison Results:")
    print(f"Average Score: {comparison.get('score_analysis', {}).get('average_score', 0)}")
    print(f"Insights: {comparison.get('insights', [])}")

if __name__ == "__main__":
    test_resume_comparator()