"""
Source links enhancement for the NewsSense app.
This file contains code to improve the visibility and functionality of source links.
"""

# Enhanced source links display
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
    },
    "Reuters": {
        "url": "https://www.reuters.com/",
        "logo": "https://www.reuters.com/pf/resources/images/reuters/logo-vertical-default.svg?d=154",
        "description": "Global news agency providing breaking news and analysis"
    },
    "Bloomberg": {
        "url": "https://www.bloomberg.com/",
        "logo": "https://www.bloomberg.com/graphics/assets/img/bloomberg-light.svg",
        "description": "Global business and financial information provider"
    }
}

# Source link CSS styles
SOURCE_LINK_CSS = """
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
</style>
"""

def render_enhanced_source_link(source):
    """
    Render an enhanced source link card with logo, description, and direct link.
    
    Args:
        source: Source dictionary with title, source, date, etc.
        
    Returns:
        HTML string for the enhanced source card
    """
    source_name = source.get('source', 'Unknown')
    title = source.get('title', 'Untitled')
    date = source.get('date', 'Unknown date')
    relevance = source.get('relevance_score', 0)
    matches = source.get('matches', [])
    
    # Get source information
    source_info = SOURCE_LINKS.get(source_name, {
        "url": "#",
        "logo": "",
        "description": "News source"
    })
    
    # Format date
    try:
        import datetime
        dt = datetime.datetime.fromisoformat(date.replace('Z', '+00:00'))
        formatted_date = dt.strftime("%d %b %Y, %H:%M")
    except:
        formatted_date = date
    
    # Generate stars based on relevance
    stars = "★" * min(5, max(1, int(relevance / 5)))
    
    # Generate HTML for matched terms
    matched_terms_html = ""
    if matches:
        terms_html = "".join([f'<div class="matched-term">{term}</div>' for term in matches])
        matched_terms_html = f'<div class="matched-terms">{terms_html}</div>'
    
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
    </div>
    """
    
    return html

def display_enhanced_sources(sources):
    """
    Display all sources with enhanced formatting.
    
    Args:
        sources: List of source dictionaries
    """
    import streamlit as st
    
    # Add the CSS
    st.markdown(SOURCE_LINK_CSS, unsafe_allow_html=True)
    
    # Display each source
    for source in sources:
        st.markdown(render_enhanced_source_link(source), unsafe_allow_html=True)

# Example usage in the app:
"""
# In the qa_section function:
if 'qa_results' in st.session_state and st.session_state.qa_results:
    result = st.session_state.qa_results
    
    # Display answer
    st.markdown("#### Answer:")
    st.markdown(f"{result.get('answer', 'No answer available')}")
    
    # Show relevant sources with enhanced links
    st.markdown("#### Sources:")
    sources = result.get('sources', [])
    if sources:
        # Add this import at the top
        from source_links_update import display_enhanced_sources
        
        # Display enhanced sources
        display_enhanced_sources(sources)
        
        # Continue with stock performance display
        for source in sources:
            with st.expander(f"Stock Data for {source.get('title', 'Untitled')}"):
                ticker = find_stock_ticker_in_source(source)
                if ticker:
                    stock_data = get_stock_data(ticker)
                    if stock_data:
                        render_stock_performance(stock_data)
                    else:
                        st.write("No stock data available for this source.")
""" 