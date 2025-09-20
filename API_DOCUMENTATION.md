# API Documentation - Resume Relevance Checker

## Overview

This document provides comprehensive API documentation for the Resume Relevance Checker application, detailing all available endpoints, request/response formats, and integration guidelines.

## Base URL

```
Local Development: http://localhost:8501
Production: https://your-app-name.streamlit.app
```

## Authentication

### User Registration
- **Endpoint**: `/register`
- **Method**: POST (via Streamlit form)
- **Description**: Register a new user account

**Request Parameters:**
```json
{
  "username": "string (required, unique)",
  "email": "string (required, unique, valid email)",
  "password": "string (required, min 6 characters)",
  "confirm_password": "string (required, must match password)",
  "full_name": "string (optional)",
  "company": "string (optional)",
  "role": "string (optional, from predefined list)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Account created successfully! Please sign in.",
  "user_id": "integer"
}
```

### User Login
- **Endpoint**: `/login`
- **Method**: POST (via Streamlit form)
- **Description**: Authenticate user and create session

**Request Parameters:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Welcome back! Redirecting to dashboard...",
  "session_id": "string",
  "user_info": {
    "id": "integer",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "company": "string",
    "role": "string"
  }
}
```

## Analysis Endpoints

### File Upload
- **Endpoint**: `/upload`
- **Method**: POST (via Streamlit file uploader)
- **Description**: Upload job descriptions and resumes

**Supported File Types:**
- PDF (.pdf)
- Microsoft Word (.docx)
- Plain Text (.txt)

**File Size Limits:**
- Maximum file size: 10MB per file
- Maximum files per upload: 10 files

### Skill Extraction
- **Endpoint**: `/extract_skills`
- **Method**: POST
- **Description**: Extract skills from job description

**Request Parameters:**
```json
{
  "job_description": "string (required)",
  "extraction_method": "ai|keyword (optional, default: ai)"
}
```

**Response:**
```json
{
  "success": true,
  "skills": {
    "must_have": ["string"],
    "good_to_have": ["string"]
  },
  "extraction_method": "ai|keyword"
}
```

### Resume Analysis
- **Endpoint**: `/analyze`
- **Method**: POST
- **Description**: Perform comprehensive resume analysis

**Request Parameters:**
```json
{
  "job_description": "string (required)",
  "resume_files": ["file objects"],
  "analysis_type": "standard|ats|performance|strength|comparison",
  "hard_weight": "float (0.0-1.0, default: 0.6)",
  "soft_weight": "float (0.0-1.0, default: 0.4)",
  "industry": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "resume_file": "string",
      "hard_pct": "float",
      "soft_pct": "float",
      "final_score": "float",
      "verdict": "string",
      "missing_skills": ["string"],
      "feedback": "string",
      "analysis_specific_data": "object"
    }
  ],
  "analysis_type": "string",
  "timestamp": "datetime"
}
```

## Analysis Types

### Standard Analysis
**Response Format:**
```json
{
  "resume_file": "string",
  "hard_pct": "float (0-100)",
  "soft_pct": "float (0-100)",
  "final_score": "float (0-100)",
  "verdict": "Excellent|Good|Fair|Poor",
  "missing_skills": ["string"],
  "feedback": "string"
}
```

### ATS Score Analysis
**Additional Fields:**
```json
{
  "ats_score": "float (0-100)",
  "ats_grade": "A|B|C|D|F",
  "ats_suggestions": ["string"]
}
```

### Performance Prediction
**Additional Fields:**
```json
{
  "performance_score": "float (0-100)",
  "interview_probability": "float (0-100)",
  "hiring_likelihood": "float (0-100)",
  "performance_grade": "A|B|C|D|F"
}
```

### Strength Analysis
**Additional Fields:**
```json
{
  "strength_score": "float (0-100)",
  "strength_categories": {
    "technical_skills": "float",
    "soft_skills": "float",
    "experience": "float",
    "education": "float"
  },
  "strength_insights": ["string"]
}
```

### Comparison Dashboard
**Additional Fields:**
```json
{
  "rankings": [
    {
      "rank": "integer",
      "resume_file": "string",
      "score": "float",
      "verdict": "string"
    }
  ],
  "insights": ["string"],
  "recommendations": ["string"]
}
```

## Data Export

### Export Results
- **Endpoint**: `/export`
- **Method**: GET
- **Description**: Export analysis results

**Query Parameters:**
- `format`: `csv|json` (required)
- `analysis_id`: `string` (optional, specific analysis)
- `user_id`: `integer` (optional, all user analyses)

**Response:**
- **CSV**: File download with analysis results
- **JSON**: JSON object with complete analysis data

### Analysis History
- **Endpoint**: `/history`
- **Method**: GET
- **Description**: Retrieve user's analysis history

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "id": "integer",
      "analysis_type": "string",
      "job_description": "string",
      "resume_count": "integer",
      "created_at": "datetime",
      "results_summary": "object"
    }
  ],
  "total_count": "integer"
}
```

## Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

### Common Error Codes
- `INVALID_CREDENTIALS`: Authentication failed
- `FILE_TOO_LARGE`: Uploaded file exceeds size limit
- `UNSUPPORTED_FORMAT`: File format not supported
- `ANALYSIS_FAILED`: Analysis processing error
- `INSUFFICIENT_DATA`: Missing required parameters
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error

## Rate Limiting

### Limits
- **File Uploads**: 10 files per request
- **Analysis Requests**: 5 per minute per user
- **API Calls**: 100 per hour per user

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Webhooks (Future Feature)

### Analysis Complete Webhook
```json
{
  "event": "analysis.complete",
  "data": {
    "analysis_id": "string",
    "user_id": "integer",
    "status": "success|failed",
    "results": "object",
    "timestamp": "datetime"
  }
}
```

## SDK Examples

### Python SDK
```python
from resume_checker import ResumeChecker

client = ResumeChecker(api_key="your_api_key")

# Upload and analyze
result = client.analyze(
    job_description="Software Engineer position...",
    resume_files=["resume1.pdf", "resume2.pdf"],
    analysis_type="standard"
)

print(f"Analysis complete: {result.final_score}% match")
```

### JavaScript SDK
```javascript
import { ResumeChecker } from 'resume-checker-sdk';

const client = new ResumeChecker('your_api_key');

const result = await client.analyze({
  jobDescription: 'Software Engineer position...',
  resumeFiles: ['resume1.pdf', 'resume2.pdf'],
  analysisType: 'standard'
});

console.log(`Analysis complete: ${result.finalScore}% match`);
```

## Integration Examples

### Webhook Integration
```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    
    if data['event'] == 'analysis.complete':
        # Process completed analysis
        analysis_id = data['data']['analysis_id']
        results = data['data']['results']
        
        # Send notification or update database
        send_notification(analysis_id, results)
    
    return {'status': 'success'}
```

### Batch Processing
```python
import asyncio
from resume_checker import ResumeChecker

async def batch_analyze():
    client = ResumeChecker(api_key="your_api_key")
    
    tasks = []
    for resume_batch in resume_batches:
        task = client.analyze_async(
            job_description=jd,
            resume_files=resume_batch,
            analysis_type="standard"
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## Security Considerations

### API Key Management
- Store API keys securely
- Rotate keys regularly
- Use environment variables
- Implement key scoping

### Data Privacy
- All data is encrypted in transit
- User data is isolated
- No data sharing with third parties
- GDPR compliance features

### Input Validation
- File type validation
- Size limit enforcement
- Content sanitization
- SQL injection prevention

## Monitoring and Analytics

### Metrics Available
- Request volume and latency
- Error rates by endpoint
- User engagement metrics
- Analysis success rates

### Logging
- Request/response logging
- Error tracking
- Performance monitoring
- Security event logging

## Support and Resources

### Documentation
- API reference guide
- Integration tutorials
- Code examples
- Best practices guide

### Support Channels
- GitHub Issues for bugs
- Email support for questions
- Community forums
- Video tutorials

### Status Page
- Service status updates
- Maintenance notifications
- Performance metrics
- Incident reports

---

*This API documentation is regularly updated. Please check for the latest version.*
