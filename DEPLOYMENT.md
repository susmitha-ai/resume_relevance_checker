# Streamlit Cloud Deployment Guide

## 🚀 Deploying Resume Relevance Checker to Streamlit Cloud

### Prerequisites
1. **GitHub Account** - Your code must be in a GitHub repository
2. **Streamlit Cloud Account** - Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Grok API Key** (optional) - For enhanced AI features

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Resume Relevance Checker"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/resume-relevance-checker.git
   git push -u origin main
   ```

2. **Ensure these files are in your repository:**
   - `streamlit_app.py` ✅
   - `requirements.txt` ✅
   - `packages.txt` ✅
   - `.streamlit/config.toml` ✅
   - All `scoring/` modules ✅
   - `README.md` ✅

### Step 2: Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Click "New app"**
3. **Fill in the details:**
   - **Repository**: `YOUR_USERNAME/resume-relevance-checker`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose a custom URL (optional)

4. **Click "Deploy!"**

### Step 3: Configure Secrets (Optional)

If you have a Grok API key:

1. **Go to your app's settings**
2. **Click "Secrets"**
3. **Add the following secrets:**
   ```toml
   [grok]
   api_url = "https://api.grok.example/v1"
   api_key = "sk-your-actual-api-key-here"
   ```

### Step 4: Monitor Deployment

- **Build logs**: Check the deployment logs for any issues
- **App URL**: Your app will be available at `https://YOUR_APP_NAME.streamlit.app`
- **Updates**: Push changes to GitHub to automatically redeploy

## 🔧 Configuration Files

### `.streamlit/config.toml`
```toml
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

### `packages.txt`
```
# Additional system packages (if needed)
```

### `requirements.txt`
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
PyMuPDF>=1.23.0
pdfplumber>=0.9.0
python-docx>=0.8.11
sentence-transformers>=2.2.2
scikit-learn>=1.3.0
requests>=2.31.0
python-dotenv>=1.0.0
nltk>=3.8.1
spacy>=3.6.0
jupyter>=1.0.0
ipykernel>=6.25.0
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0
altair>=4.0.0
```

## 🚨 Troubleshooting

### Common Issues:

1. **Import Errors:**
   - Ensure all modules are in the `scoring/` directory
   - Check that `__init__.py` files exist if needed

2. **Memory Issues:**
   - Streamlit Cloud has memory limits
   - Consider optimizing large models

3. **File Upload Limits:**
   - Streamlit Cloud has file size limits
   - Large PDFs might need optimization

4. **API Key Issues:**
   - Ensure secrets are properly configured
   - Check API key format and permissions

### Performance Optimization:

1. **Model Caching:**
   - Models are cached between sessions
   - First load might be slower

2. **File Processing:**
   - Large files are processed in memory
   - Consider file size limits

3. **Concurrent Users:**
   - Streamlit Cloud handles multiple users
   - Each user gets their own session

## 📊 Monitoring

- **Usage Statistics**: Available in Streamlit Cloud dashboard
- **Error Logs**: Check the logs for debugging
- **Performance**: Monitor app performance and memory usage

## 🔄 Updates

To update your deployed app:

1. **Make changes to your code**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Update: Add new features"
   git push origin main
   ```
3. **Streamlit Cloud will automatically redeploy**

## 🌐 Custom Domain (Optional)

1. **Go to app settings**
2. **Configure custom domain**
3. **Update DNS settings as instructed**

## 📱 Mobile Optimization

The app is mobile-responsive and works on:
- Desktop browsers
- Mobile devices
- Tablets

## 🔒 Security

- **File uploads**: Files are processed securely
- **API keys**: Stored as encrypted secrets
- **Data privacy**: No data is permanently stored

## 💰 Costs

- **Streamlit Cloud**: Free tier available
- **API costs**: Only if using external APIs
- **Storage**: Minimal storage usage

## 🆘 Support

- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **GitHub Issues**: Create issues in your repository
