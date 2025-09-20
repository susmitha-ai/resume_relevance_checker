import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
import time
from datetime import datetime

try:
    from scoring.parser import extract_text_from_file
    from scoring.skill_extractor import extract_skills_from_jd
    from scoring.scoring import calculate_relevance_score
    from scoring.embeddings import get_embeddings
    from scoring.grok_client import grok_generate
    from scoring.feedback import generate_feedback
    from scoring.ats_analyzer import calculate_ats_score
    from scoring.resume_comparator import compare_resumes, create_comparison_dataframe
    from scoring.performance_predictor import predict_performance
    from scoring.strength_analyzer import analyze_resume_strengths
except ImportError as e:
    st.error(f"Missing modules: {e}")
    st.stop()

st.set_page_config(
    page_title="Resume Relevance Checker",
    page_icon="📄",
    layout="wide"
)

if 'results' not in st.session_state:
    st.session_state.results = []
if 'jd_text' not in st.session_state:
    st.session_state.jd_text = ""
if 'jd_skills' not in st.session_state:
    st.session_state.jd_skills = {"must_have": [], "good_to_have": []}

def update_task_status(task_id, status, outputs=None, notes=""):
    """Update task status in .cursor_tasks.json"""
    try:
        with open('.cursor_tasks.json', 'r') as f:
            data = json.load(f)
        
        for task in data['tasks']:
            if task['id'] == task_id:
                task['status'] = status
                if status == 'done':
                    task['finished_at'] = datetime.now().isoformat() + 'Z'
                    if outputs:
                        task['outputs'] = outputs
                if notes:
                    task['notes'] = notes
                break
        
        data['last_updated'] = datetime.now().isoformat() + 'Z'
        
        with open('.cursor_tasks.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error updating task status: {e}")

def main():
    st.title("📄 Resume Relevance Checker")
    st.markdown("Upload job descriptions and resumes to get AI-powered relevance scores and improvement suggestions.")
    
    with st.sidebar:
        st.header("📋 Configuration")
        
        st.subheader("🔧 Analysis Mode")
        analysis_mode = st.selectbox(
            "Choose Analysis Type:",
            ["Standard Analysis", "ATS Score Analysis", "Performance Prediction", "Strength Analysis", "Comparison Dashboard"]
        )
        

        st.subheader("1. Job Description")
        jd_option = st.radio("Choose JD input method:", ["Upload File", "Paste Text"])
        
        if jd_option == "Upload File":
            jd_file = st.file_uploader("Upload JD (PDF/DOCX)", type=['pdf', 'docx'], key="jd_upload")
            if jd_file:
                if st.button("Extract JD Text"):
                    with st.spinner("Extracting text from JD..."):
                        try:
                            jd_text = extract_text_from_file(jd_file)
                            st.session_state.jd_text = jd_text
                            st.success("JD text extracted successfully!")
                        except Exception as e:
                            st.error(f"Error extracting JD: {e}")
        else:
            jd_text = st.text_area("Paste Job Description", height=200, key="jd_paste")
            if jd_text:
                st.session_state.jd_text = jd_text
        

        if st.session_state.jd_text:
            if st.button("Extract Skills from JD"):
                with st.spinner("Extracting skills using AI..."):
                    try:
                        skills = extract_skills_from_jd(st.session_state.jd_text)
                        st.session_state.jd_skills = skills
                        st.success("Skills extracted successfully!")
                    except Exception as e:
                        st.error(f"Error extracting skills: {e}")
        

        if st.session_state.jd_skills.get("must_have"):
            st.subheader("Extracted Skills")
            st.write("**Must Have:**")
            for skill in st.session_state.jd_skills["must_have"]:
                st.write(f"• {skill}")
            
            st.write("**Good to Have:**")
            for skill in st.session_state.jd_skills["good_to_have"]:
                st.write(f"• {skill}")
        

        st.subheader("2. Resumes")
        resume_files = st.file_uploader(
            "Upload Resumes (PDF/DOCX)", 
            type=['pdf', 'docx'], 
            accept_multiple_files=True,
            key="resume_upload"
        )
        

        if analysis_mode in ["ATS Score Analysis", "Performance Prediction"]:
            st.subheader("3. Advanced Settings")
            industry = st.selectbox(
                "Industry:",
                ["technology", "finance", "healthcare", "education", "marketing", "default"]
            )
        else:
            industry = "default"
        

        st.subheader("4. Scoring Weights")
        hard_weight = st.slider("Hard Match Weight", 0.0, 1.0, 0.6, 0.1)
        soft_weight = 1.0 - hard_weight
        st.write(f"Soft Match Weight: {soft_weight:.1f}")
        

        if st.button("🚀 Analyze Resumes", type="primary"):
            if not st.session_state.jd_text:
                st.error("Please provide a job description first!")
                return
            if not resume_files:
                st.error("Please upload at least one resume!")
                return
            
            process_resumes_advanced(resume_files, hard_weight, soft_weight, analysis_mode, industry)
    

    if st.session_state.jd_text:
        st.subheader("📝 Job Description Preview")
        st.text_area("JD Text", st.session_state.jd_text, height=150, disabled=True)
    

    if st.session_state.results:
        display_results()
    


def process_resumes_advanced(resume_files, hard_weight, soft_weight, analysis_mode, industry):
    """Process uploaded resumes with advanced analysis modes"""
    st.session_state.results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, resume_file in enumerate(resume_files):
        status_text.text(f"Processing {resume_file.name}...")
        
        try:

            resume_text = extract_text_from_file(resume_file)
            

            score_result = calculate_relevance_score(
                jd_text=st.session_state.jd_text,
                resume_text=resume_text,
                jd_skills=st.session_state.jd_skills,
                hard_weight=hard_weight,
                soft_weight=soft_weight
            )
            

            feedback = generate_feedback(
                st.session_state.jd_text,
                resume_text,
                score_result.get('missing_skills', [])
            )
            

            result = {
                'resume_file': resume_file.name,
                'hard_pct': score_result.get('hard_pct', 0),
                'soft_pct': score_result.get('soft_pct', 0),
                'final_score': score_result.get('final_score', 0),
                'verdict': score_result.get('verdict', 'Low'),
                'missing_skills': score_result.get('missing_skills', []),
                'grok_feedback': feedback,
                'resume_text': resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
            }
            

            if analysis_mode == "ATS Score Analysis":
                ats_result = calculate_ats_score(resume_text, industry)
                result['ats_score'] = ats_result.get('ats_score', 0)
                result['ats_grade'] = ats_result.get('ats_grade', 'Unknown')
                result['ats_suggestions'] = ats_result.get('suggestions', [])
            
            elif analysis_mode == "Performance Prediction":
                performance_result = predict_performance(score_result, st.session_state.jd_skills, industry)
                result['performance_score'] = performance_result.get('base_performance_score', 0)
                result['interview_probability'] = performance_result.get('interview_probability', 0)
                result['hiring_likelihood'] = performance_result.get('hiring_likelihood', 0)
                result['performance_grade'] = performance_result.get('performance_grade', 'Unknown')
            
            elif analysis_mode == "Strength Analysis":
                strength_result = analyze_resume_strengths(resume_text, st.session_state.jd_skills)
                result['strength_score'] = strength_result.get('overall_strength', 0)
                result['strength_categories'] = strength_result.get('category_scores', {})
                result['strength_insights'] = strength_result.get('insights', [])
            
            st.session_state.results.append(result)
            
        except Exception as e:
            st.error(f"Error processing {resume_file.name}: {e}")
        
        progress_bar.progress((i + 1) / len(resume_files))
    
    status_text.text("Analysis complete!")
    

    save_results()
    

    display_advanced_results(analysis_mode)
    
    st.success(f"Processed {len(resume_files)} resumes successfully!")

def process_resumes(resume_files, hard_weight, soft_weight):
    """Process uploaded resumes and calculate scores (legacy function)"""
    process_resumes_advanced(resume_files, hard_weight, soft_weight, "Standard Analysis", "default")

def display_advanced_results(analysis_mode):
    """Display results based on analysis mode"""
    if analysis_mode == "Comparison Dashboard":
        display_comparison_dashboard()
    else:
        display_standard_results(analysis_mode)

def display_comparison_dashboard():
    """Display comparison dashboard for multiple resumes"""
    st.subheader("📊 Resume Comparison Dashboard")
    
    if len(st.session_state.results) < 2:
        st.warning("Comparison dashboard requires at least 2 resumes")
        return
    

    comparison = compare_resumes(st.session_state.results, st.session_state.jd_text)
    

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Resumes", comparison.get('total_resumes', 0))
    with col2:
        st.metric("Average Score", f"{comparison.get('score_analysis', {}).get('average_score', 0):.1f}%")
    with col3:
        st.metric("Highest Score", f"{comparison.get('score_analysis', {}).get('highest_score', 0):.1f}%")
    with col4:
        st.metric("Score Range", f"{comparison.get('score_analysis', {}).get('score_range', 0):.1f}")
    

    st.subheader("🏆 Candidate Rankings")
    rankings = comparison.get('rankings', [])
    for i, candidate in enumerate(rankings[:5]):
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            with col1:
                st.write(f"**#{candidate.get('rank', i+1)}**")
            with col2:
                st.write(candidate.get('resume_file', 'Unknown'))
            with col3:
                st.write(f"Score: {candidate.get('final_score', 0):.1f}%")
            with col4:
                verdict_color = {'High': '🟢', 'Medium': '🟡', 'Low': '🔴'}.get(candidate.get('verdict', 'Low'), '⚪')
                st.write(f"{verdict_color} {candidate.get('verdict', 'Unknown')}")
    

    insights = comparison.get('insights', [])
    if insights:
        st.subheader("💡 Key Insights")
        for insight in insights:
            st.info(insight)
    

    recommendations = comparison.get('recommendations', [])
    if recommendations:
        st.subheader("📋 Recommendations")
        for rec in recommendations:
            st.success(rec)

def display_standard_results(analysis_mode):
    """Display standard results with mode-specific enhancements"""
    st.subheader("📊 Analysis Results")
    

    df = pd.DataFrame(st.session_state.results)
    

    base_columns = ['resume_file', 'hard_pct', 'soft_pct', 'final_score', 'verdict']
    
    if analysis_mode == "ATS Score Analysis":
        display_columns = base_columns + ['ats_score', 'ats_grade']
        df_display = df[display_columns].copy()
    elif analysis_mode == "Performance Prediction":
        display_columns = base_columns + ['performance_score', 'interview_probability', 'hiring_likelihood']
        df_display = df[display_columns].copy()
    elif analysis_mode == "Strength Analysis":
        display_columns = base_columns + ['strength_score']
        df_display = df[display_columns].copy()
    else:
        display_columns = base_columns + ['missing_skills']
        df_display = df[display_columns].copy()
        df_display['missing_skills'] = df_display['missing_skills'].apply(lambda x: ', '.join(x[:3]) + ('...' if len(x) > 3 else ''))
    

    st.dataframe(df_display, use_container_width=True)
    

    st.subheader("🔍 Detailed Results")
    for i, result in enumerate(st.session_state.results):
        with st.expander(f"{result['resume_file']} - {result['verdict']} ({result['final_score']:.1f}%)"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Hard Match", f"{result['hard_pct']:.1f}%")
                st.metric("Soft Match", f"{result['soft_pct']:.1f}%")
                st.metric("Final Score", f"{result['final_score']:.1f}%")
                

                if analysis_mode == "ATS Score Analysis":
                    st.metric("ATS Score", f"{result.get('ats_score', 0):.1f}%")
                    st.metric("ATS Grade", result.get('ats_grade', 'Unknown'))
                elif analysis_mode == "Performance Prediction":
                    st.metric("Performance Score", f"{result.get('performance_score', 0):.1f}%")
                    st.metric("Interview Probability", f"{result.get('interview_probability', 0):.1f}%")
                    st.metric("Hiring Likelihood", f"{result.get('hiring_likelihood', 0):.1f}%")
                elif analysis_mode == "Strength Analysis":
                    st.metric("Strength Score", f"{result.get('strength_score', 0):.1f}%")
            
            with col2:
                st.write("**Missing Skills:**")
                for skill in result['missing_skills']:
                    st.write(f"• {skill}")
                

                if analysis_mode == "ATS Score Analysis" and result.get('ats_suggestions'):
                    st.write("**ATS Suggestions:**")
                    for suggestion in result['ats_suggestions']:
                        st.write(f"• {suggestion}")
                elif analysis_mode == "Strength Analysis" and result.get('strength_insights'):
                    st.write("**Strength Insights:**")
                    for insight in result['strength_insights']:
                        st.write(f"• {insight}")
            
            st.write("**AI Feedback:**")
            st.info(result['grok_feedback'])
            
            st.write("**Resume Preview:**")
            st.text(result['resume_text'])
    

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Export CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"resume_analysis_{analysis_mode.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📥 Export JSON"):
            json_data = json.dumps(st.session_state.results, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"resume_analysis_{analysis_mode.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def display_results():
    """Display results in a table and detailed view (legacy function)"""
    display_standard_results("Standard Analysis")

def save_results():
    """Save results to files"""
    try:

        with open('data/results/resume_scores.json', 'w') as f:
            json.dump(st.session_state.results, f, indent=2)
        

        df = pd.DataFrame(st.session_state.results)
        df.to_csv('data/results/resume_scores.csv', index=False)
        
        st.success("Results saved to data/results/")
    except Exception as e:
        st.error(f"Error saving results: {e}")


if __name__ == "__main__":
    main()