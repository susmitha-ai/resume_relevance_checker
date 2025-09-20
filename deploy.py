

import os
import sys
from pathlib import Path

def check_deployment_readiness():
    """Check if the project is ready for deployment."""
    print("🔍 Checking deployment readiness...")
    
    required_files = [
        "streamlit_app.py",
        "requirements.txt",
        ".streamlit/config.toml",
        "scoring/parser.py",
        "scoring/skill_extractor.py",
        "scoring/scoring.py",
        "scoring/embeddings.py",
        "scoring/grok_client.py",
        "scoring/feedback.py",
        "scoring/ats_analyzer.py",
        "scoring/resume_comparator.py",
        "scoring/performance_predictor.py",
        "scoring/strength_analyzer.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present!")
    return True

def check_requirements():
    """Check requirements.txt content."""
    print("\n📋 Checking requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        required_packages = [
            "streamlit",
            "pandas",
            "numpy",
            "PyMuPDF",
            "pdfplumber",
            "python-docx",
            "sentence-transformers",
            "scikit-learn",
            "requests",
            "python-dotenv"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print("❌ Missing packages in requirements.txt:")
            for package in missing_packages:
                print(f"   - {package}")
            return False
        
        print("✅ All required packages present!")
        return True
        
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False

def generate_deployment_instructions():
    """Generate deployment instructions."""
    print("\n🚀 Deployment Instructions:")
    print("=" * 50)
    
    print("\n1. 📁 Prepare GitHub Repository:")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Initial commit - Resume Relevance Checker'")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/YOUR_USERNAME/resume-relevance-checker.git")
    print("   git push -u origin main")
    
    print("\n2. 🌐 Deploy to Streamlit Cloud:")
    print("   - Go to https://share.streamlit.io")
    print("   - Click 'New app'")
    print("   - Repository: YOUR_USERNAME/resume-relevance-checker")
    print("   - Branch: main")
    print("   - Main file: streamlit_app.py")
    print("   - Click 'Deploy!'")
    
    print("\n3. 🔑 Configure Secrets (Optional):")
    print("   - Go to app settings")
    print("   - Add secrets:")
    print("     [grok]")
    print("     api_url = 'https://api.grok.example/v1'")
    print("     api_key = 'sk-your-actual-api-key-here'")
    
    print("\n4. ✅ Your app will be available at:")
    print("   https://YOUR_APP_NAME.streamlit.app")

def main():
    """Main deployment check function."""
    print("🎯 Resume Relevance Checker - Deployment Checker")
    print("=" * 60)
    

    files_ok = check_deployment_readiness()
    

    requirements_ok = check_requirements()
    

    if files_ok and requirements_ok:
        print("\n🎉 Project is ready for deployment!")
        generate_deployment_instructions()
    else:
        print("\n❌ Project needs fixes before deployment.")
        print("Please address the issues above and run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()