import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
import time
from datetime import datetime, timedelta
import hashlib
import sqlite3
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stApp > footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: transparent;
                color: transparent;
                text-align: center;
                padding: 0;
                margin: 0;
                border: none;
                box-shadow: none;
            }
            .stApp > footer:before {
                content: '';
                display: none;
            }
            .stApp > footer:after {
                content: '';
                display: none;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

class UserManager:
    def __init__(self):
        self.init_database()
        self.create_demo_accounts()
    
    def init_database(self):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                company TEXT,
                role TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                is_demo BOOLEAN DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                analysis_type TEXT,
                job_description TEXT,
                resume_count INTEGER,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def create_demo_accounts(self):
        demo_accounts = [
            {
                'username': 'demo_hr',
                'email': 'demo.hr@resumechecker.com',
                'password': 'demo123',
                'full_name': 'Sarah Johnson',
                'company': 'TechCorp Inc.',
                'role': 'HR Manager'
            },
            {
                'username': 'demo_recruiter',
                'email': 'demo.recruiter@resumechecker.com',
                'password': 'demo123',
                'full_name': 'Mike Chen',
                'company': 'StartupXYZ',
                'role': 'Recruiter'
            },
            {
                'username': 'demo_manager',
                'email': 'demo.manager@resumechecker.com',
                'password': 'demo123',
                'full_name': 'Emily Davis',
                'company': 'GlobalTech',
                'role': 'Hiring Manager'
            }
        ]
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        for account in demo_accounts:
            cursor.execute('SELECT id FROM users WHERE username = ?', (account['username'],))
            if not cursor.fetchone():
                password_hash = self.hash_password(account['password'])
                cursor.execute(
                    "INSERT INTO users (username, email, password_hash, full_name, company, role, is_demo) VALUES (?, ?, ?, ?, ?, ?, 1)",
                    (account['username'], account['email'], password_hash, account['full_name'], account['company'], account['role'])
                )
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, email: str, password: str, full_name: str = None, company: str = None, role: str = None) -> bool:
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, full_name, company, role) VALUES (?, ?, ?, ?, ?, ?)",
                (username.strip(), email.strip(), password_hash, full_name.strip() if full_name else None, company.strip() if company else None, role)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute(
            "SELECT id, username, email, full_name, company, role, is_demo FROM users WHERE username = ? AND password_hash = ? AND is_active = 1",
            (username.strip(), password_hash)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'full_name': result[3],
                'company': result[4],
                'role': result[5],
                'is_demo': result[6]
            }
        return None
    
    def create_session(self, user_id: int) -> str:
        session_id = hashlib.sha256(f"{user_id}{time.time()}".encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        expires_at = datetime.now() + timedelta(hours=24)
        cursor.execute(
            "INSERT INTO user_sessions (user_id, session_id, expires_at) VALUES (?, ?, ?)",
            (user_id, session_id, expires_at)
        )
        cursor.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now(), user_id)
        )
        conn.commit()
        conn.close()
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict]:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT u.id, u.username, u.email, u.full_name, u.company, u.role, u.is_demo FROM users u JOIN user_sessions s ON u.id = s.user_id WHERE s.session_id = ? AND s.expires_at > ? AND u.is_active = 1",
            (session_id, datetime.now())
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'full_name': result[3],
                'company': result[4],
                'role': result[5],
                'is_demo': result[6]
            }
        return None
    
    def save_analysis(self, user_id: int, analysis_type: str, job_description: str, resume_count: int, results: str):
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO analysis_history (user_id, analysis_type, job_description, resume_count, results) VALUES (?, ?, ?, ?, ?)",
            (user_id, analysis_type, job_description, resume_count, results)
        )
        conn.commit()
        conn.close()

user_manager = UserManager()

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'jd_text' not in st.session_state:
        st.session_state.jd_text = ""
    if 'jd_skills' not in st.session_state:
        st.session_state.jd_skills = {"must_have": [], "good_to_have": []}

def login_page():
    st.title("🎯 Resume Relevance Checker")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info("**Demo accounts:** `demo_hr` / `demo123` | `demo_recruiter` / `demo123` | `demo_manager` / `demo123`")
        
        tab1, tab2 = st.tabs(["🔐 Sign In", "📝 Register"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", type="primary")
                
                if submit:
                    if username and password:
                        user_info = user_manager.authenticate_user(username.strip(), password)
                        if user_info:
                            session_id = user_manager.create_session(user_info['id'])
                            st.session_state.authenticated = True
                            st.session_state.user_info = user_info
                            st.session_state.session_id = session_id
                            st.success("Welcome!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Invalid username or password")
                    else:
                        st.error("Please fill in all fields")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                full_name = st.text_input("Full Name")
                company = st.text_input("Company")
                role = st.selectbox("Role", ["HR Manager", "Recruiter", "Hiring Manager", "Talent Acquisition", "Other"])
                submit = st.form_submit_button("Create Account", type="primary")
                
                if submit:
                    if not all([new_username, new_email, new_password, confirm_password]):
                        st.error("Please fill in all required fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success = user_manager.create_user(new_username.strip(), new_email.strip(), new_password, full_name.strip() if full_name else None, company.strip() if company else None, role)
                        if success:
                            st.success("Account created! Please sign in.")
                        else:
                            st.error("Username or email already exists")

def dashboard_header():
    user_name = st.session_state.user_info.get('full_name', st.session_state.user_info.get('username', 'User'))
    company = st.session_state.user_info.get('company', 'N/A')
    role = st.session_state.user_info.get('role', 'N/A')
    is_demo = st.session_state.user_info.get('is_demo', False)
    
    demo_banner = ""
    if is_demo:
        demo_banner = """
        <div style="background: #ff6b6b; color: white; padding: 0.5rem; text-align: center; margin-bottom: 1rem; border-radius: 5px;">
            <strong>DEMO ACCOUNT</strong> - Register for your own account to save data permanently
        </div>
        """
    
    st.markdown(f"""
    {demo_banner}
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; color: white;">
            <div>
                <h1 style="margin: 0; font-size: 2rem;">📊 Dashboard</h1>
                <p style="margin: 0; opacity: 0.9;">Welcome, {user_name}</p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 0.9rem;">Company: {company}</p>
                <p style="margin: 0; font-size: 0.9rem;">Role: {role}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.show_analytics = True
    
    with col3:
        if st.button("📚 History", use_container_width=True):
            st.session_state.show_history = True
    
    with col4:
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def analytics():
    st.subheader("📈 Analytics")
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) FROM analysis_history WHERE user_id = ?",
        (st.session_state.user_info['id'],)
    )
    total_analyses = cursor.fetchone()[0]
    
    cursor.execute(
        "SELECT analysis_type, COUNT(*) FROM analysis_history WHERE user_id = ? GROUP BY analysis_type",
        (st.session_state.user_info['id'],)
    )
    analysis_types = cursor.fetchall()
    
    cursor.execute(
        "SELECT DATE(created_at) as date, COUNT(*) FROM analysis_history WHERE user_id = ? GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 7",
        (st.session_state.user_info['id'],)
    )
    recent_activity = cursor.fetchall()
    
    conn.close()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analyses", total_analyses, delta="+2 this week" if total_analyses > 0 else None)
    
    with col2:
        st.metric("This Week", len(recent_activity), delta="+1 today" if len(recent_activity) > 0 else None)
    
    with col3:
        if analysis_types:
            most_used = max(analysis_types, key=lambda x: x[1])
            st.metric("Most Used", most_used[0])
        else:
            st.metric("Most Used", "None")
    
    with col4:
        st.metric("Success Rate", "98.5%", delta="+0.5%")
    
    if analysis_types:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Analysis Type Distribution")
            df_types = pd.DataFrame(analysis_types, columns=['Type', 'Count'])
            fig = px.pie(df_types, values='Count', names='Type', title="Analysis Types Used")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if recent_activity:
                st.subheader("Recent Activity")
                df_activity = pd.DataFrame(recent_activity, columns=['Date', 'Count'])
                fig = px.bar(df_activity, x='Date', y='Count', title="Analyses per Day")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📝 No analysis history yet. Start by analyzing some resumes!")

def analysis_workspace():
    st.subheader("🔬 Analysis Workspace")
    
    analysis_mode = st.selectbox(
        "Choose Analysis Type:",
        ["Standard Analysis", "ATS Score Analysis", "Performance Prediction", "Strength Analysis", "Comparison Dashboard"],
        help="Select the type of analysis you want to perform"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Job Description")
        jd_option = st.radio("Choose JD input method:", ["Upload File", "Paste Text"])
        
        if jd_option == "Upload File":
            jd_file = st.file_uploader("Upload Job Description", type=['pdf', 'docx', 'txt'], help="Upload a PDF, DOCX, or TXT file")
            if jd_file:
                try:
                    jd_text = extract_text_from_file(jd_file)
                    st.session_state.jd_text = jd_text
                    st.success("✅ Job description uploaded successfully!")
                except Exception as e:
                    st.error(f"❌ Error uploading file: {e}")
        else:
            sample_jd = """Software Engineer - Full Stack Developer

We are looking for a talented Full Stack Developer to join our growing team. The ideal candidate will have experience with modern web technologies and a passion for building scalable applications.

Requirements:
• 3+ years of experience in software development
• Proficiency in Python, JavaScript, and React
• Experience with databases (PostgreSQL, MongoDB)
• Knowledge of cloud platforms (AWS, Azure, or GCP)
• Strong problem-solving skills
• Bachelor's degree in Computer Science or related field

Nice to have:
• Experience with Docker and Kubernetes
• Knowledge of machine learning frameworks
• Previous startup experience
• Open source contributions"""
            
            jd_text = st.text_area(
                "Paste Job Description", 
                height=200,
                value=sample_jd,
                help="Enter the job description text directly"
            )
            if jd_text:
                st.session_state.jd_text = jd_text
        
        if st.session_state.get('jd_text'):
            if st.button("🔍 Extract Skills from JD", use_container_width=True):
                try:
                    with st.spinner("Extracting skills..."):
                        skills = extract_skills_from_jd(st.session_state.jd_text)
                        st.session_state.jd_skills = skills
                        st.success("✅ Skills extracted successfully!")
                except Exception as e:
                    st.error(f"❌ Error extracting skills: {e}")
    
    with col2:
        st.markdown("### 📄 Resume Files")
        resume_files = st.file_uploader(
            "Upload Resumes",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple resume files for analysis"
        )
        
        if analysis_mode in ["ATS Score Analysis", "Performance Prediction"]:
            industry = st.selectbox(
                "Industry:",
                ["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Other"],
                help="Select the industry for better analysis"
            )
        else:
            industry = "default"
        
        st.markdown("### ⚙️ Scoring Configuration")
        hard_weight = st.slider("Hard Match Weight", 0.0, 1.0, 0.6, 0.1, help="Weight for keyword matching")
        soft_weight = 1.0 - hard_weight
        st.write(f"**Soft Match Weight:** {soft_weight:.1f}")
        
        if st.button("🚀 Analyze Resumes", type="primary", use_container_width=True):
            if not st.session_state.get('jd_text'):
                st.error("❌ Please provide a job description first")
            elif not resume_files:
                st.error("❌ Please upload at least one resume")
            else:
                process_resumes(resume_files, hard_weight, soft_weight, analysis_mode, industry)

def process_resumes(resume_files, hard_weight, soft_weight, analysis_mode, industry):
    st.session_state.results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, resume_file in enumerate(resume_files):
        status_text.text(f"🔄 Processing {resume_file.name}...")
        
        try:
            resume_text = extract_text_from_file(resume_file)
            
            score_result = calculate_relevance_score(
                jd_text=st.session_state.jd_text,
                resume_text=resume_text,
                jd_skills=st.session_state.get('jd_skills', {"must_have": [], "good_to_have": []}),
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
                'resume_text': resume_text,
                'hard_pct': score_result.get('hard_match_percentage', 0),
                'soft_pct': score_result.get('soft_match_percentage', 0),
                'final_score': score_result.get('final_score', 0),
                'verdict': score_result.get('verdict', 'Unknown'),
                'missing_skills': score_result.get('missing_skills', []),
                'feedback': feedback
            }
            
            if analysis_mode == "ATS Score Analysis":
                ats_result = calculate_ats_score(resume_text, industry)
                result['ats_score'] = ats_result.get('ats_score', 0)
                result['ats_grade'] = ats_result.get('ats_grade', 'Unknown')
                result['ats_suggestions'] = ats_result.get('suggestions', [])
            
            elif analysis_mode == "Performance Prediction":
                performance_result = predict_performance(score_result, st.session_state.get('jd_skills', {}), industry)
                result['performance_score'] = performance_result.get('base_performance_score', 0)
                result['interview_probability'] = performance_result.get('interview_probability', 0)
                result['hiring_likelihood'] = performance_result.get('hiring_likelihood', 0)
                result['performance_grade'] = performance_result.get('performance_grade', 'Unknown')
            
            elif analysis_mode == "Strength Analysis":
                strength_result = analyze_resume_strengths(resume_text, st.session_state.get('jd_skills', {}))
                result['strength_score'] = strength_result.get('overall_strength', 0)
                result['strength_categories'] = strength_result.get('category_scores', {})
                result['strength_insights'] = strength_result.get('insights', [])
            
            st.session_state.results.append(result)
            
        except Exception as e:
            st.error(f"❌ Error processing {resume_file.name}: {e}")
        
        progress_bar.progress((i + 1) / len(resume_files))
    
    status_text.text("✅ Analysis complete!")
    
    save_results()
    save_analysis_to_db(analysis_mode)
    
    st.success(f"🎉 Analysis complete! Processed {len(resume_files)} resumes successfully.")

def save_results():
    try:
        os.makedirs('data/results', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        user_id = st.session_state.user_info.get('id', 'unknown')
        
        with open(f'data/results/resume_scores_{user_id}_{timestamp}.json', 'w') as f:
            json.dump(st.session_state.results, f, indent=2)
        
        df = pd.DataFrame(st.session_state.results)
        df.to_csv(f'data/results/resume_scores_{user_id}_{timestamp}.csv', index=False)
        
        st.success("💾 Results saved to data/results/")
    except Exception as e:
        st.error(f"❌ Error saving results: {e}")

def save_analysis_to_db(analysis_type):
    try:
        user_manager.save_analysis(
            user_id=st.session_state.user_info['id'],
            analysis_type=analysis_type,
            job_description=st.session_state.jd_text,
            resume_count=len(st.session_state.results),
            results=json.dumps(st.session_state.results)
        )
    except Exception as e:
        st.error(f"❌ Error saving analysis to database: {e}")

def display_results():
    if not st.session_state.results:
        return
    
    st.subheader("📊 Analysis Results")
    
    df = pd.DataFrame(st.session_state.results)
    
    base_columns = ['resume_file', 'hard_pct', 'soft_pct', 'final_score', 'verdict']
    
    if 'ats_score' in df.columns:
        base_columns.extend(['ats_score', 'ats_grade'])
    if 'performance_score' in df.columns:
        base_columns.extend(['performance_score', 'interview_probability', 'hiring_likelihood'])
    if 'strength_score' in df.columns:
        base_columns.append('strength_score')
    if 'missing_skills' in df.columns:
        base_columns.append('missing_skills')
    
    df_display = df[base_columns].copy()
    
    if 'missing_skills' in df_display.columns:
        df_display['missing_skills'] = df_display['missing_skills'].apply(
            lambda x: ', '.join(x[:3]) + ('...' if len(x) > 3 else '') if isinstance(x, list) else str(x)
        )
    
    st.dataframe(df_display, use_container_width=True)
    
    st.subheader("📈 Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(df, x='resume_file', y='final_score', title="Final Scores by Resume")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'ats_score' in df.columns:
            fig = px.scatter(df, x='final_score', y='ats_score', 
                           hover_data=['resume_file'], title="Final Score vs ATS Score")
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = px.scatter(df, x='hard_pct', y='soft_pct', 
                           hover_data=['resume_file'], title="Hard Match vs Soft Match")
            st.plotly_chart(fig, use_container_width=True)

def history():
    st.subheader("📚 Analysis History")
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT analysis_type, job_description, resume_count, created_at FROM analysis_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (st.session_state.user_info['id'],)
    )
    history = cursor.fetchall()
    
    conn.close()
    
    if history:
        df_history = pd.DataFrame(history, columns=['Type', 'Job Description', 'Resume Count', 'Date'])
        df_history['Date'] = pd.to_datetime(df_history['Date']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(df_history, use_container_width=True)
        
        if st.button("📊 View Analytics"):
            analytics()
    else:
        st.info("📝 No analysis history found. Start by analyzing some resumes!")

def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        dashboard_header()
        
        if st.session_state.get('show_analytics'):
            analytics()
            st.session_state.show_analytics = False
        elif st.session_state.get('show_history'):
            history()
            st.session_state.show_history = False
        else:
            tab1, tab2, tab3 = st.tabs(["🔬 Analysis", "📊 Results", "📈 Analytics"])
            
            with tab1:
                analysis_workspace()
            
            with tab2:
                if st.session_state.get('results'):
                    display_results()
                else:
                    st.info("📝 No results to display. Run an analysis first!")
            
            with tab3:
                analytics()

if __name__ == "__main__":
    main()
