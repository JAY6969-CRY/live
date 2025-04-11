# NewsSense - Financial News Analysis System

## Quick Start Guide

This is a simplified demo version of the NewsSense application for the demonstration. The application provides financial news analysis and helps answer questions about stock movements.

### How to Run the Application

There are two ways to run the application:

#### 1. Direct Offline Mode (Recommended for Demo)

For a quick demonstration with simulated data, run:

```bash
streamlit run direct_offline.py
```

This will start a Streamlit app with mock data that simulates the full functionality without requiring API keys or internet connections.

#### 2. Full Integration Mode (With Gemini API)

For the complete experience with real data scraping and Gemini AI integration:

1. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

2. Run the direct integration:
   ```bash
   python direct_start.py
   ```

Or manually start Streamlit with:
```bash
streamlit run run_direct.py
```

### Features

The application has two main tabs:

1. **Ask Question**: Enter any financial question and get an AI-generated response with relevant news sources.

2. **Stock Analysis**: Look up specific stocks and get analysis with relevant news articles.

### Demo Notes

- The offline mode uses simulated data for demonstration purposes
- The full integration mode requires internet connection for news scraping
- Using Gemini API provides more accurate and contextual responses

### Troubleshooting

If you encounter any issues:

1. Make sure you have all required dependencies installed (`pip install -r requirements.txt`)
2. Check your API key is correctly set in the `.env` file
3. If API services are not responsive, try the offline mode instead

---

## Technical Overview

NewsSense connects financial news to market performance to explain stock, mutual fund, or ETF movements.

The system architecture includes:
- News scraping from financial sources
- NLP processing to extract entities and insights
- Gemini AI integration for question answering
- Stock-specific analysis with relevance scoring
- User-friendly Streamlit interface

This project was built for the MyFi Hackathon Challenge. 