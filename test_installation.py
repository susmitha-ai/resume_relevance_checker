

import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas")
    except ImportError as e:
        print(f"❌ Pandas: {e}")
        return False
    
    try:
        import numpy
        print("✅ NumPy")
    except ImportError as e:
        print(f"❌ NumPy: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests")
    except ImportError as e:
        print(f"❌ Requests: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv")
    except ImportError as e:
        print(f"❌ Python-dotenv: {e}")
        return False
    

    try:
        import fitz
        print("✅ PyMuPDF")
    except ImportError:
        print("⚠️  PyMuPDF (optional)")
    
    try:
        import pdfplumber
        print("✅ pdfplumber")
    except ImportError:
        print("⚠️  pdfplumber (optional)")
    
    try:
        from docx import Document
        print("✅ python-docx")
    except ImportError:
        print("⚠️  python-docx (optional)")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers")
    except ImportError:
        print("⚠️  sentence-transformers (optional)")
    
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        print("✅ scikit-learn")
    except ImportError:
        print("⚠️  scikit-learn (optional)")
    
    return True

def test_project_structure():
    """Test if project structure is correct."""
    print("\nTesting project structure...")
    
    required_files = [
        "streamlit_app.py",
        "requirements.txt", 
        "README.md",
        ".gitignore"
    ]
    
    required_dirs = [
        "scoring",
        "data",
        "data/resumes",
        "data/jds", 
        "data/extracted_texts",
        "data/results",
        "notebooks"
    ]
    
    required_modules = [
        "scoring/parser.py",
        "scoring/skill_extractor.py",
        "scoring/scoring.py",
        "scoring/embeddings.py",
        "scoring/grok_client.py",
        "scoring/feedback.py"
    ]
    
    all_good = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            all_good = False
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/")
            all_good = False
    
    for module_path in required_modules:
        if Path(module_path).exists():
            print(f"✅ {module_path}")
        else:
            print(f"❌ {module_path}")
            all_good = False
    
    return all_good

def test_module_imports():
    """Test if our custom modules can be imported."""
    print("\nTesting custom modules...")
    
    try:
        from scoring.parser import extract_text_from_file
        print("✅ scoring.parser")
    except ImportError as e:
        print(f"❌ scoring.parser: {e}")
        return False
    
    try:
        from scoring.skill_extractor import extract_skills_from_jd
        print("✅ scoring.skill_extractor")
    except ImportError as e:
        print(f"❌ scoring.skill_extractor: {e}")
        return False
    
    try:
        from scoring.scoring import calculate_relevance_score
        print("✅ scoring.scoring")
    except ImportError as e:
        print(f"❌ scoring.scoring: {e}")
        return False
    
    try:
        from scoring.embeddings import get_embeddings
        print("✅ scoring.embeddings")
    except ImportError as e:
        print(f"❌ scoring.embeddings: {e}")
        return False
    
    try:
        from scoring.grok_client import grok_generate
        print("✅ scoring.grok_client")
    except ImportError as e:
        print(f"❌ scoring.grok_client: {e}")
        return False
    
    try:
        from scoring.feedback import generate_feedback
        print("✅ scoring.feedback")
    except ImportError as e:
        print(f"❌ scoring.feedback: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of the modules."""
    print("\nTesting basic functionality...")
    
    try:
        from scoring.skill_extractor import extract_skills_from_jd
        

        sample_jd = "We need a Python developer with machine learning experience."
        skills = extract_skills_from_jd(sample_jd)
        
        if isinstance(skills, dict) and 'must_have' in skills and 'good_to_have' in skills:
            print("✅ Skill extraction works")
        else:
            print("❌ Skill extraction failed")
            return False
            
    except Exception as e:
        print(f"❌ Skill extraction test failed: {e}")
        return False
    
    try:
        from scoring.scoring import calculate_relevance_score
        

        result = calculate_relevance_score(
            jd_text="Python developer needed",
            resume_text="I am a Python developer",
            jd_skills={"must_have": ["Python"], "good_to_have": []}
        )
        
        if isinstance(result, dict) and 'final_score' in result:
            print("✅ Scoring works")
        else:
            print("❌ Scoring failed")
            return False
            
    except Exception as e:
        print(f"❌ Scoring test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("Resume Relevance Checker - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Import Dependencies", test_imports),
        ("Project Structure", test_project_structure),
        ("Module Imports", test_module_imports),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The installation is ready.")
        print("\nTo run the application:")
        print("  streamlit run streamlit_app.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)