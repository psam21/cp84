"""
Fear & Greed Index Utilities
============================

Utilities for processing and displaying Fear & Greed Index data
Includes sentiment classification, color coding, and formatting
"""

from typing import Dict, Optional, Any
from datetime import datetime

def get_sentiment_details(value: int) -> Dict[str, str]:
    """
    Get detailed sentiment information based on Fear & Greed Index value
    
    Args:
        value: Fear & Greed Index value (0-100)
        
    Returns:
        Dict with emoji, color, description, and CSS class
    """
    if value <= 24:
        return {
            'emoji': '😰',
            'color': '#FF4444',  # Red
            'description': 'Extreme Fear',
            'css_class': 'extreme-fear',
            'bar_color': 'red'
        }
    elif value <= 49:
        return {
            'emoji': '😨',
            'color': '#FF8800',  # Orange
            'description': 'Fear',
            'css_class': 'fear',
            'bar_color': 'orange'
        }
    elif value <= 74:
        return {
            'emoji': '😐',
            'color': '#FFDD00',  # Yellow
            'description': 'Neutral',
            'css_class': 'neutral',
            'bar_color': 'yellow'
        }
    elif value <= 89:
        return {
            'emoji': '😊',
            'color': '#88DD44',  # Light Green
            'description': 'Greed',
            'css_class': 'greed',
            'bar_color': 'lightgreen'
        }
    else:  # 90-100
        return {
            'emoji': '🤑',
            'color': '#44AA44',  # Dark Green
            'description': 'Extreme Greed',
            'css_class': 'extreme-greed',
            'bar_color': 'green'
        }

def format_fear_greed_display(fear_greed_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Format Fear & Greed data for display in the UI
    
    Args:
        fear_greed_data: Raw data from API or None if failed
        
    Returns:
        Dict with formatted display values
    """
    if not fear_greed_data:
        return {
            'title': '😰 Fear & Greed',
            'value': 'API Failed',
            'subtitle': 'Check Connection',
            'color': '#888888',
            'emoji': '❌',
            'progress_value': 0,
            'progress_color': 'gray'
        }
    
    try:
        value = fear_greed_data['value']
        sentiment = get_sentiment_details(value)
        
        # Format timestamp if available
        last_updated = 'Unknown'
        if 'timestamp' in fear_greed_data:
            try:
                timestamp = int(fear_greed_data['timestamp'])
                dt = datetime.fromtimestamp(timestamp)
                last_updated = dt.strftime('%H:%M')
            except (ValueError, OSError):
                last_updated = 'Unknown'
        
        return {
            'title': f"{sentiment['emoji']} Fear & Greed",
            'value': f"{value}",
            'subtitle': f"{sentiment['description']} (Updated: {last_updated})",
            'color': sentiment['color'],
            'emoji': sentiment['emoji'],
            'progress_value': value,
            'progress_color': sentiment['bar_color']
        }
        
    except (KeyError, ValueError, TypeError) as e:
        return {
            'title': '😰 Fear & Greed',
            'value': 'Parse Error',
            'subtitle': 'Data Invalid',
            'color': '#888888',
            'emoji': '⚠️',
            'progress_value': 0,
            'progress_color': 'gray'
        }

def get_sentiment_interpretation(value: int) -> str:
    """
    Get a human-readable interpretation of the Fear & Greed Index
    
    Args:
        value: Fear & Greed Index value (0-100)
        
    Returns:
        Interpretation string
    """
    sentiment = get_sentiment_details(value)
    
    interpretations = {
        'Extreme Fear': "Market participants are extremely fearful. This could indicate a buying opportunity as assets may be oversold.",
        'Fear': "Market sentiment is fearful. Investors are nervous, which might present good entry points.",
        'Neutral': "Market sentiment is balanced. Neither fear nor greed is dominating investor behavior.",
        'Greed': "Market participants are getting greedy. Be cautious as assets might be getting overvalued.",
        'Extreme Greed': "Extreme greed in the market. Consider taking profits as a correction might be due."
    }
    
    return interpretations.get(sentiment['description'], "Market sentiment data available.")

def create_progress_bar_html(value: int, color: str, width: str = "100%") -> str:
    """
    Create HTML for a progress bar representation of the Fear & Greed Index
    
    Args:
        value: Index value (0-100)
        color: Color for the progress bar
        width: CSS width for the container
        
    Returns:
        HTML string for the progress bar
    """
    progress_width = f"{value}%"
    
    return f"""
    <div style="width: {width}; background-color: #e0e0e0; border-radius: 10px; height: 8px; overflow: hidden;">
        <div style="width: {progress_width}; background-color: {color}; height: 100%; transition: width 0.3s ease;"></div>
    </div>
    """

def get_market_context(value: int) -> Dict[str, str]:
    """
    Get market context and trading advice based on Fear & Greed Index
    
    Args:
        value: Fear & Greed Index value (0-100)
        
    Returns:
        Dict with context and advice
    """
    if value <= 24:
        return {
            'context': 'Extreme Fear Zone',
            'advice': 'Consider buying opportunities - market may be oversold',
            'risk_level': 'High Opportunity',
            'action': 'Accumulate'
        }
    elif value <= 49:
        return {
            'context': 'Fear Zone', 
            'advice': 'Good time for gradual accumulation',
            'risk_level': 'Moderate Opportunity',
            'action': 'Buy Dips'
        }
    elif value <= 74:
        return {
            'context': 'Neutral Zone',
            'advice': 'Market is balanced - monitor for direction',
            'risk_level': 'Balanced',
            'action': 'Hold/Monitor'
        }
    elif value <= 89:
        return {
            'context': 'Greed Zone',
            'advice': 'Exercise caution - consider taking some profits',
            'risk_level': 'Moderate Risk',
            'action': 'Reduce Position'
        }
    else:
        return {
            'context': 'Extreme Greed Zone',
            'advice': 'High risk of correction - consider selling',
            'risk_level': 'High Risk',
            'action': 'Take Profits'
        }
