# Resume Relevance Checker

A comprehensive web application that analyzes resume-job description compatibility using advanced AI-powered scoring algorithms and provides actionable insights for career development.

## 🎯 Overview

The Resume Relevance Checker is a sophisticated platform designed to bridge the gap between job seekers and employers by providing intelligent analysis of resume-job description alignment. Built with modern web technologies and AI integration, it offers multiple analysis modes to evaluate resume compatibility from various perspectives.

## ✨ Key Features

### 🔍 Multi-Modal Analysis
- **Standard Analysis**: Comprehensive resume-job description matching
- **ATS Score Analysis**: Applicant Tracking System compatibility assessment
- **Performance Prediction**: Interview and hiring likelihood estimation
- **Strength Analysis**: Multi-dimensional resume strength evaluation
- **Comparison Dashboard**: Side-by-side resume comparison and ranking

### 🤖 AI-Powered Intelligence
- **Skill Extraction**: Automated identification of required and preferred skills
- **Semantic Matching**: Advanced text similarity analysis using embeddings
- **Feedback Generation**: Personalized improvement suggestions
- **Smart Scoring**: Hybrid hard-match and soft-match algorithms

### 👥 User Management
- **Secure Authentication**: User registration and login system
- **Demo Accounts**: Immediate access for testing and evaluation
- **Personal Dashboards**: Individual user workspaces
- **Analysis History**: Complete tracking of all analyses

### 📊 Advanced Analytics
- **Interactive Visualizations**: Dynamic charts and graphs
- **Data Export**: CSV and JSON result downloads
- **Usage Statistics**: Personal analytics and trends
- **Performance Metrics**: Success rates and analysis insights

## 🛠️ Technical Architecture

### Frontend
- **Streamlit**: Modern web application framework
- **Plotly**: Interactive data visualizations
- **Responsive Design**: Mobile and desktop compatibility

### Backend
- **Python 3.8+**: Core application logic
- **SQLite**: User data and analysis history storage
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

### AI & ML Components
- **Sentence Transformers**: Text embeddings for semantic analysis
- **Scikit-learn**: Machine learning algorithms
- **TF-IDF**: Keyword extraction and matching
- **Grok API Integration**: Advanced AI capabilities

### File Processing
- **PyMuPDF**: PDF text extraction
- **PDFPlumber**: Alternative PDF processing
- **Python-docx**: Microsoft Word document handling

## 📁 Project Structure

```
resume-relevance-checker/
├── final_dashboard.py          # Main application entry point
├── requirements.txt            # Python dependencies
├── README.md                  # Project documentation
├── .gitignore                 # Git ignore rules
├── .streamlit/                # Streamlit configuration
│   └── config.toml
├── scoring/                   # Core analysis modules
│   ├── __init__.py
│   ├── parser.py              # File text extraction
│   ├── skill_extractor.py     # Skill identification
│   ├── scoring.py             # Hybrid scoring algorithms
│   ├── embeddings.py          # Text embeddings
│   ├── grok_client.py         # AI API integration
│   ├── feedback.py            # Improvement suggestions
│   ├── ats_analyzer.py        # ATS compatibility
│   ├── resume_comparator.py   # Resume comparison
│   ├── performance_predictor.py # Performance prediction
│   └── strength_analyzer.py   # Strength analysis
├── data/                      # Data storage
│   ├── resumes/              # Uploaded resume files
│   ├── jds/                  # Job description files
│   ├── extracted_texts/      # Processed text files
│   └── results/              # Analysis results
└── notebooks/                # Development notebooks
    └── eval.ipynb            # Evaluation and testing
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (for version control)

### Local Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/resume-relevance-checker.git
   cd resume-relevance-checker
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   streamlit run final_dashboard.py
   ```

4. **Access the Application**
   - Open your browser and navigate to `http://localhost:8501`
   - Use demo accounts for immediate testing

### Demo Accounts
- **HR Manager**: `demo_hr` / `demo123`
- **Recruiter**: `demo_recruiter` / `demo123`
- **Hiring Manager**: `demo_manager` / `demo123`

## 📖 Usage Guide

### Getting Started

1. **Login or Register**
   - Use demo accounts for immediate access
   - Create personal account for data persistence

2. **Upload Job Description**
   - Upload PDF/DOCX files or paste text directly
   - Extract skills automatically using AI

3. **Upload Resumes**
   - Support for multiple file formats (PDF, DOCX, TXT)
   - Batch processing capabilities

4. **Configure Analysis**
   - Select analysis type based on your needs
   - Adjust scoring weights for customization
   - Choose industry context for better accuracy

5. **Review Results**
   - Interactive data tables and visualizations
   - Detailed feedback and improvement suggestions
   - Export results for further analysis

### Analysis Types

#### Standard Analysis
- Comprehensive resume-job description matching
- Hard-match and soft-match scoring
- Missing skills identification
- Overall compatibility assessment

#### ATS Score Analysis
- Applicant Tracking System compatibility
- Industry-specific ATS requirements
- Format and structure optimization
- Keyword density analysis

#### Performance Prediction
- Interview probability estimation
- Hiring likelihood assessment
- Performance grade assignment
- Risk factor identification

#### Strength Analysis
- Multi-dimensional strength evaluation
- Category-wise scoring (technical, soft skills, experience)
- Strength heatmap visualization
- Improvement area identification

#### Comparison Dashboard
- Side-by-side resume comparison
- Ranking and scoring metrics
- Competitive analysis insights
- Best candidate identification

## 🔧 Configuration

### Environment Variables
Create a `.env` file for API configuration:
```env
GROK_API_URL=your_grok_api_url
GROK_API_KEY=your_grok_api_key
```

### Streamlit Configuration
The application uses default Streamlit settings. Customize in `.streamlit/config.toml`:
```toml
[server]
port = 8501
headless = true

[browser]
gatherUsageStats = false
```

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Configure deployment settings
   - Deploy your application

3. **Configure Secrets**
   - Add API keys in Streamlit Cloud secrets
   - Set environment variables as needed

### Alternative Deployment Options

- **Heroku**: Container-based deployment
- **AWS/GCP/Azure**: Cloud platform deployment
- **Docker**: Containerized deployment

## 📊 API Integration

### Grok API Setup
1. Obtain API credentials from Grok
2. Configure environment variables
3. Test API connectivity
4. Monitor usage and costs

### Fallback Mechanisms
- Local embeddings for semantic analysis
- Template-based feedback generation
- Keyword matching for skill extraction
- Mock responses for testing

## 🔒 Security Features

### Data Protection
- Password hashing with SHA-256
- Session management with expiration
- User data isolation
- Secure file handling

### Privacy Compliance
- No data sharing with third parties
- Local data storage options
- User consent mechanisms
- Data deletion capabilities

## 🧪 Testing

### Test Suite
```bash
python test_installation.py
```

### Manual Testing
- Use demo accounts for functionality testing
- Upload sample resumes and job descriptions
- Verify all analysis modes work correctly
- Test export and visualization features

## 📈 Performance Optimization

### Caching Strategies
- Embedding caching for repeated analysis
- Session state management
- Database query optimization
- File processing optimization

### Scalability Considerations
- Database connection pooling
- Asynchronous processing
- Load balancing for multiple users
- Resource monitoring and alerting

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings for all functions
- Include type hints where appropriate
- Write comprehensive tests

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Streamlit team for the excellent web framework
- Hugging Face for sentence transformers
- Scikit-learn for machine learning tools
- The open-source community for various libraries

## 📞 Support

### Documentation
- Comprehensive inline documentation
- API reference guides
- Video tutorials and examples
- FAQ and troubleshooting guides

### Community
- GitHub Issues for bug reports
- Discussion forums for questions
- Regular updates and improvements
- Community contributions welcome

## 🔮 Future Enhancements

### Planned Features
- Multi-language support
- Advanced AI model integration
- Real-time collaboration features
- Mobile application development
- Enterprise dashboard features
- API endpoint development

### Research Areas
- Improved semantic matching algorithms
- Industry-specific analysis models
- Bias detection and mitigation
- Performance prediction accuracy
- User experience optimization

---

**Built with ❤️ for the global job market**

*Empowering job seekers and employers with intelligent resume analysis technology.*