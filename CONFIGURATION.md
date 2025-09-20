# Configuration Guide

## Environment Variables

To use the full AI-powered features, you need to configure the Grok API. Create a `.env` file in the project root with the following content:

```env
# Grok API Configuration
GROK_API_URL=https://api.grok.example/v1
GROK_API_KEY=sk-your-api-key-here
```

## Getting Grok API Access

1. **Sign up for Grok API access** at the official Grok website
2. **Get your API key** from the dashboard
3. **Update the .env file** with your actual credentials

## Fallback Mode

The application works without Grok API using:
- Local TF-IDF embeddings for semantic similarity
- Template-based feedback generation
- Keyword-based skill extraction

## Testing Configuration

Run the test script to verify your setup:

```bash
python test_installation.py
```

## Running the Application

1. **Start the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Open your browser** and go to `http://localhost:8501`

## Features Available

### With Grok API:
- AI-powered skill extraction from job descriptions
- Personalized feedback generation
- Advanced semantic analysis

### Without Grok API (Fallback):
- Keyword-based skill extraction
- Template-based feedback
- TF-IDF semantic similarity
- All core functionality works

## Troubleshooting

If you encounter issues:

1. **Check API credentials** in `.env` file
2. **Verify internet connection** for API calls
3. **Check API rate limits** and quotas
4. **Review error messages** in the console

The application is designed to gracefully handle API failures and provide useful fallback functionality.
