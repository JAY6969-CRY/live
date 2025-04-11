# NewsSense: Financial News Analysis System

NewsSense is a comprehensive financial news analysis system that helps investors understand why their stocks, mutual funds, or ETFs are up or down by connecting financial news to market performance.

## Features

- **News Scraping**: Scrape financial news from multiple sources without relying on third-party APIs
- **Financial Data Retrieval**: Get data for stocks, mutual funds, and ETFs for both Indian and US markets
- **Natural Language Processing**: Analyze news for sentiment, entity extraction, and keyword identification
- **Question Answering**: Answer natural language questions about market movements using an LLM-powered QA system
- **Stock-Specific Analysis**: Look up any stock symbol and get targeted news and analysis
- **Multiple Interfaces**: Access via web UI, API, or command-line

## Setup and Installation

### Prerequisites

- Python 3.8+
- OpenAI API key (for QA functionality)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/newssense.git
   cd newssense
   ```

2. Install requirements:
   ```
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   For Windows:
   ```
   set OPENAI_API_KEY=your_api_key_here
   ```

## Running NewsSense

### Quick Start (Recommended)

The easiest way to run all components of NewsSense is using the start script:

```
python start.py
```

This will start:
- The FastAPI backend at http://localhost:8000
- The Flask stock analysis API at http://localhost:5000
- The Streamlit web interface at http://localhost:8501

The script will automatically open your browser to the web interface.

### Manual Component Startup

Alternatively, you can start each component individually:

#### Starting the Backend API

1. Start the FastAPI backend:
   ```
   cd src/api
   uvicorn app:app --reload
   ```
   
   The API will be available at http://localhost:8000

2. Start the Flask stock analysis API:
   ```
   cd src/api
   python flask_app.py
   ```
   
   The Stock API will be available at http://localhost:5000

### Starting the Web Interface

```
cd web
streamlit run app.py
```

The web interface will be available at http://localhost:8501

### Using the Command-Line Interface

Basic usage:
```
python -m cli.main ask "Why is Nifty down today?"
```

Interactive mode:
```
python -m cli.main interactive
```

## Usage

### Web Interface

1. **Ask Questions**: Use the "Ask" tab to ask natural language questions about the market
2. **Stock Lookup**: Enter a stock symbol in the "Stock Lookup" tab to get targeted news and analysis
3. **Browse News**: Find latest financial news articles in the "News" tab
4. **Search Stocks/Funds**: Look up specific securities in their respective tabs

### API Endpoints

#### Main API (FastAPI)

- `GET /news/headlines`: Get latest news headlines
- `GET /news/article`: Get full article by URL
- `GET /stocks/search`: Search for stocks
- `GET /mutualfunds/search`: Search for mutual funds
- `POST /qa/question`: Answer a financial question

#### Stock Analysis API (Flask)

- `GET /api/stock/news`: Get news related to a specific stock symbol
- `POST /api/stock/analysis`: Generate analysis for a stock based on recent news

## Project Structure

```
newssense/
├── cli/              # Command-line interface
├── src/              # Core source code
│   ├── api/          # API endpoints
│   ├── data/         # Data retrieval and processing
│   │   ├── financial/# Financial data retrieval
│   │   └── scrapers/ # News scraping modules
│   └── models/       # ML/NLP models and processors
├── web/              # Web interface
└── README.md         # This file
```

## Customization

- Add new news sources in `src/data/scrapers/`
- Extend financial data sources in `src/data/financial/`
- Customize NLP processing in `src/models/news_processor.py`

## Limitations

- Relies on Google's Gemini API for enhanced QA functionality (falls back to simulated responses if API key is not provided)
- Uses simulated/placeholder data for some financial instruments
- Limited to predefined list of entities for matching news to securities

## License

[Your license information here]

## Acknowledgements

Built for the MyFi Hackathon Challenge. 