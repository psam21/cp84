# Fear & Greed Index Feature

## Overview

The Fear & Greed Index is a market sentiment indicator that measures the emotions and sentiments driving the crypto market. The index ranges from 0 (Extreme Fear) to 100 (Extreme Greed) and helps provide context for market conditions.

## Implementation

### API Integration
- **Source**: Alternative.me API (`https://api.alternative.me/fng/`)
- **Data Type**: Market sentiment index (0-100)
- **Update Frequency**: Daily
- **Cache Duration**: 5 minutes
- **Rate Limiting**: 10 requests per minute

### UI Components

#### Visual Display
- **Location**: Blue metrics container (10th box)
- **Layout**: Emoji + Title + Value + Progress Bar
- **Design**: Matches existing portfolio box styling

#### Color Coding
| Range | Classification | Color | Emoji | Advice |
|-------|---------------|-------|-------|---------|
| 0-24  | Extreme Fear  | 🔴 Red | 😰 | Accumulate |
| 25-49 | Fear          | 🟠 Orange | 😨 | Buy Dips |
| 50-74 | Neutral       | 🟡 Yellow | 😐 | Hold/Monitor |
| 75-89 | Greed         | 🟢 Light Green | 😊 | Reduce Position |
| 90-100| Extreme Greed | 🟢 Dark Green | 🤑 | Take Profits |

### Technical Features

#### Error Handling
- **API Failure**: Shows "API Failed" with ❌ emoji
- **Network Issues**: Graceful degradation to cached data
- **Invalid Data**: Parse error handling with warning display

#### Performance
- **Caching**: Smart 5-minute cache (daily updates)
- **Rate Limiting**: Conservative API usage
- **Parallel Loading**: Non-blocking integration with main portfolio

#### Progress Bar
- **Visual**: Horizontal progress bar showing index position
- **Animation**: Smooth CSS transitions
- **Responsive**: Adapts to container width
- **Accessibility**: Clear visual representation of sentiment

## Usage

### For Users
1. **Monitor Sentiment**: Quick visual indicator of market psychology
2. **Trading Context**: Understand if market is fearful or greedy
3. **Decision Support**: Use sentiment data for portfolio decisions
4. **Market Timing**: Historical context for entry/exit points

### For Developers
```python
# Get current Fear & Greed data
from apis.fear_greed_api import get_fear_greed_index
data = get_fear_greed_index()

# Format for display
from utils.fear_greed_utils import format_fear_greed_display
display = format_fear_greed_display(data)

# Get market context and advice
from utils.fear_greed_utils import get_market_context
context = get_market_context(data['value'])
```

## Integration Points

### Files Modified
- `pages/portfolio_ui.py` - Added Fear & Greed box to blue container
- `utils/diagnostics.py` - Added connectivity testing
- `utils/__init__.py` - Exported Fear & Greed utilities

### Files Added
- `apis/fear_greed_api.py` - Alternative.me API integration
- `utils/fear_greed_utils.py` - Sentiment processing utilities
- `tests/test_apis.py` - Fear & Greed API tests (updated)
- `tests/test_utils.py` - Fear & Greed utils tests (updated)

### Dependencies
- No new external dependencies required
- Uses existing `requests` and caching infrastructure
- Leverages existing rate limiting system

## Testing

### Unit Tests
```bash
# Test API connectivity
python -c "from apis.fear_greed_api import test_fear_greed_connectivity; print(test_fear_greed_connectivity())"

# Test sentiment classification
python -c "from utils.fear_greed_utils import get_sentiment_details; print(get_sentiment_details(72))"
```

### Integration Tests
- API connectivity and response validation
- Sentiment classification accuracy
- Display formatting correctness
- Error handling scenarios
- Cache behavior verification

## Monitoring

### Success Metrics
- API response time < 2 seconds
- Cache hit rate > 80%
- Error rate < 5%
- UI render time < 100ms

### Error Scenarios
- Alternative.me API downtime
- Network connectivity issues
- Invalid response format
- Rate limiting exceeded

## Future Enhancements

### Potential Features
- Historical Fear & Greed trends
- Sentiment-based alerts
- Advanced sentiment analysis
- Multiple sentiment sources
- Custom thresholds and notifications

### Technical Improvements
- WebSocket real-time updates
- Additional sentiment providers
- Machine learning sentiment analysis
- Predictive sentiment modeling

## Support

### Troubleshooting
1. **No Data**: Check internet connectivity and API status
2. **Stale Data**: Clear cache or wait for refresh
3. **UI Issues**: Check browser console for errors
4. **API Errors**: Monitor rate limiting and retry logic

### Configuration
- Cache duration configurable in `fear_greed_api.py`
- Rate limits adjustable in rate limiter
- Display format customizable in `fear_greed_utils.py`
- Color scheme modifiable in sentiment classification
