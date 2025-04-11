
import streamlit as st
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# Page setup
st.set_page_config(
    page_title="NewsSense - Sources",
    page_icon="📰",
    layout="wide"
)

# Enhanced source links with detailed information
SOURCE_LINKS = {
    "Economic Times": {
        "url": "https://economictimes.indiatimes.com/",
        "logo": "https://img.etimg.com/photo/91627846.cms",
        "description": "Leading business and financial news source from India"
    },
    "Business Standard": {
        "url": "https://www.business-standard.com/",
        "logo": "https://bsmedia.business-standard.com/include/_mod/site/html5/images/business-standard-logo.png",
        "description": "Premium business news and analysis platform"
    },
    "Mint": {
        "url": "https://www.livemint.com/",
        "logo": "https://images.livemint.com/static/livemint-logo-v1.svg",
        "description": "Business and financial news from HT Media"
    },
    "Money Control": {
        "url": "https://www.moneycontrol.com/",
        "logo": "https://images.moneycontrol.com/images/common/logo-mkm.png",
        "description": "Comprehensive financial news and market data portal"
    },
    "Financial Express": {
        "url": "https://www.financialexpress.com/",
        "logo": "https://images.financialexpress.com/2021/08/fe-logo-new.png",
        "description": "Financial news and analysis from Indian Express Group"
    }
}

# Sample stock data
STOCK_DATA = {
    "TCS": {
        "name": "Tata Consultancy Services Ltd.",
        "ticker": "TCS.NS",
        "isin": "INE467B01029",
        "price": 3754.25,
        "change": 34.10
    },
    "RELIANCE": {
        "name": "Reliance Industries Ltd.",
        "ticker": "RELIANCE.NS",
        "isin": "INE002A01018",
        "price": 2865.75,
        "change": -14.20
    },
    "HDFC": {
        "name": "HDFC Bank Ltd.",
        "ticker": "HDFCBANK.NS",
        "isin": "INE040A01034",
        "price": 1643.50,
        "change": 13.70
    }
}

# Sample sources for demonstration
SAMPLE_SOURCES = [
    {
        "title": "TCS shares up 2% on market optimism",
        "source": "Economic Times",
        "date": "2023-04-11T09:30:00",
        "matches": ["tcs", "market"],
        "relevance_score": 15,
        "ticker": "TCS"
    },
    {
        "title": "Reliance Industries expands retail footprint with new acquisition",
        "source": "Business Standard",
        "date": "2023-04-11T10:45:00",
        "matches": ["reliance", "retail", "acquisition"],
        "relevance_score": 15,
        "ticker": "RELIANCE"
    },
    {
        "title": "HDFC Bank reports strong Q4 results, NPAs stable",
        "source": "Mint",
        "date": "2023-04-10T09:15:00",
        "matches": ["hdfc", "bank", "results", "npa"],
        "relevance_score": 16,
        "ticker": "HDFC"
    }
]

# CSS for enhanced source display
st.markdown("""
<style>
.source-card {
    border: 1px solid #e6e9ef;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    transition: all 0.3s ease;
    background-color: #f7f9fc;
}
.source-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    border-color: #c7d1e0;
}
.source-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}
.source-logo {
    max-height: 30px;
    max-width: 100px;
    margin-right: 15px;
}
.source-name {
    font-weight: bold;
    font-size: 16px;
    color: #1e3a8a;
}
.source-date {
    color: #64748b;
    font-size: 13px;
    margin-top: 2px;
}
.source-description {
    color: #64748b;
    font-size: 13px;
    margin-bottom: 10px;
}
.source-url {
    display: inline-block;
    background-color: #3a7de5;
    color: white;
    padding: 5px 12px;
    border-radius: 4px;
    text-decoration: none;
    font-size: 13px;
    margin-top: 5px;
}
.source-url:hover {
    background-color: #2563eb;
}
.relevance-info {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #e6e9ef;
}
.relevance-score {
    background-color: #f1f5f9;
    border-radius: 15px;
    padding: 3px 10px;
    font-size: 12px;
    color: #475569;
}
.relevance-stars {
    color: #f59e0b;
}
.matched-terms {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 8px;
}
.matched-term {
    background-color: #e0f2fe;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 12px;
    color: #0369a1;
}
.stock-up {
    color: #0ecb81;
    font-weight: bold;
}
.stock-down {
    color: #f6465d;
    font-weight: bold;
}
.stock-display {
    background-color: #f0f2f5;
    border-radius: 6px;
    padding: 10px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

def format_date(date_str):
    """Format date string for display."""
    try:
        dt = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d %b %Y, %H:%M")
    except:
        return date_str

def render_source_card(source):
    """Render an enhanced source card with direct link."""
    source_name = source.get('source', 'Unknown')
    title = source.get('title', 'Untitled')
    date = source.get('date', 'Unknown date')
    relevance = source.get('relevance_score', 0)
    matches = source.get('matches', [])
    ticker = source.get('ticker')
    
    # Get source information
    source_info = SOURCE_LINKS.get(source_name, {
        "url": "#",
        "logo": "",
        "description": "News source"
    })
    
    # Format date
    formatted_date = format_date(date)
    
    # Generate stars based on relevance
    stars = "★" * min(5, max(1, int(relevance / 5)))
    
    # Generate HTML for matched terms
    matched_terms_html = ""
    if matches:
        terms_html = "".join([f'<div class="matched-term">{term}</div>' for term in matches])
        matched_terms_html = f'<div class="matched-terms">{terms_html}</div>'
    
    # Add stock info if available
    stock_html = ""
    if ticker and ticker in STOCK_DATA:
        stock = STOCK_DATA[ticker]
        change_class = "stock-up" if stock["change"] > 0 else "stock-down"
        change_symbol = "▲" if stock["change"] > 0 else "▼"
        
        stock_html = f"""
        <div class="stock-display">
            <div><strong>{stock["name"]}</strong> ({stock["ticker"]})</div>
            <div>Price: ₹{stock["price"]:.2f} <span class="{change_class}">{change_symbol} {abs(stock["change"]):.2f}</span></div>
            <div style="font-size:12px;color:#666;">ISIN: {stock["isin"]}</div>
        </div>
        """
    
    # Build the complete source card
    html = f"""
    <div class="source-card">
        <div class="source-header">
            <img src="{source_info['logo']}" class="source-logo" onerror="this.style.display='none'" />
            <div>
                <div class="source-name">{title}</div>
                <div class="source-date">{formatted_date} • {source_name}</div>
            </div>
        </div>
        <div class="source-description">{source_info['description']}</div>
        <a href="{source_info['url']}" target="_blank" class="source-url">Visit Source</a>
        
        <div class="relevance-info">
            <div class="relevance-score">Relevance: <span class="relevance-stars">{stars}</span> ({relevance:.1f})</div>
            {matched_terms_html}
        </div>
        
        {stock_html}
    </div>
    """
    
    return html

# App header
st.title("📰 Enhanced News Sources with Stock Performance")
st.markdown("This demo showcases enhanced news source display with direct links and stock performance data.")

# Description
st.markdown("""
This feature provides a more comprehensive view of news sources with:
- Direct links to original news articles
- Source information and logos
- Relevance scores visualized with star ratings
- Highlighted matching terms for better context
- Stock performance data for mentioned companies
""")

# Create container for sources
st.subheader("News Sources with Stock Performance")

# Custom query input
query = st.text_input("Enter your question:", 
                      value="What's happening with TCS and Reliance?",
                      placeholder="e.g., Why is HDFC Bank up today?")

if st.button("Search", type="primary"):
    with st.spinner("Fetching relevant sources..."):
        # For demo, we'll display our mock sources
        # Normally this would call the API with the query
        
        # Filter sources based on query terms to simulate search
        query_terms = [term.lower() for term in query.replace("?", "").split() if len(term) > 2]
        
        if query_terms:
            filtered_sources = []
            for source in SAMPLE_SOURCES:
                source_text = source["title"].lower() + " " + source.get("source", "").lower()
                if any(term in source_text for term in query_terms):
                    filtered_sources.append(source)
                    
            display_sources = filtered_sources if filtered_sources else SAMPLE_SOURCES
        else:
            display_sources = SAMPLE_SOURCES
        
        # Always show stock performance data
        for source in display_sources:
            if "ticker" not in source and any(company.lower() in source["title"].lower() for company in ["TCS", "Reliance", "HDFC", "Infosys"]):
                if "TCS" in source["title"]:
                    source["ticker"] = "TCS"
                elif "Reliance" in source["title"]:
                    source["ticker"] = "RELIANCE"
                elif "HDFC" in source["title"]:
                    source["ticker"] = "HDFC"
                elif "Infosys" in source["title"]:
                    source["ticker"] = "INFY"
        
        # Display the sources
        for source in display_sources:
            st.markdown(render_source_card(source), unsafe_allow_html=True)
else:
    # Show sample sources initially
    st.markdown("### Sample News Sources")
    for source in SAMPLE_SOURCES:
        st.markdown(render_source_card(source), unsafe_allow_html=True)
        
# Add information about the demo
st.markdown("---")
st.markdown("""
### About This Demo
This demonstration shows how news sources are displayed with:
- Direct links to the original source websites
- Source logos and descriptions
- Relevance scores based on query matching
- Highlighted matched terms
- Integrated stock performance data
""")
