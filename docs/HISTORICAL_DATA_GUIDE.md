# 📈 Historical Price Data Guide

This guide covers the new historical price data features added to the Luno MCP server.

## Overview

The Luno MCP server now supports comprehensive historical price data through two main tools:
- **`get_historical_prices`** - Raw OHLC candlestick data
- **`get_price_range`** - Statistical analysis over time periods

## Features

### 🕯️ Candlestick Data (`get_historical_prices`)

Get detailed OHLC (Open, High, Low, Close) candlestick data for any trading pair.

**Parameters:**
- `pair` (required): Trading pair (e.g., 'XBTZAR', 'ETHZAR')
- `since` (required): Start timestamp in Unix milliseconds
- `duration` (optional): Candle duration in seconds (default: 86400 = 24h)

**Supported Timeframes:**
- `60` - 1 minute
- `300` - 5 minutes  
- `900` - 15 minutes
- `1800` - 30 minutes
- `3600` - 1 hour
- `10800` - 3 hours
- `14400` - 4 hours
- `28800` - 8 hours
- `86400` - 24 hours (default)
- `259200` - 3 days
- `604800` - 7 days

**Example Response:**
```json
{
  "pair": "XBTZAR",
  "since": 1640995200000,
  "duration": 86400,
  "duration_name": "24h",
  "candles": [
    {
      "timestamp": 1640995200000,
      "open": "850000.00",
      "high": "870000.00", 
      "low": "845000.00",
      "close": "865000.00",
      "volume": "15.25"
    }
  ],
  "candle_count": 7,
  "status": "success"
}
```

### 📊 Price Analysis (`get_price_range`)

Get statistical analysis of price movements over a specified time period.

**Parameters:**
- `pair` (required): Trading pair (e.g., 'XBTZAR', 'ETHZAR')
- `days` (optional): Number of days to analyze (1-30, default: 7)

**Example Response:**
```json
{
  "pair": "XBTZAR",
  "days": 7,
  "period_start": 1640995200000,
  "period_end": 1641600000000,
  "open_price": "850000.00",
  "close_price": "865000.00",
  "highest_price": "890000.00",
  "lowest_price": "845000.00",
  "price_change": "15000.00",
  "price_change_percent": "1.76%",
  "average_price": "867500.00",
  "total_volume": "125.75",
  "candle_count": 7,
  "status": "success"
}
```

## Usage Examples

### Basic Historical Data

**Ask Claude:**
> "Get historical prices for XBTZAR over the last 7 days"

**Or more specific:**
> "Show me 1-hour candlestick data for ETHZAR since yesterday"

### Price Analysis

**Ask Claude:**
> "What's the price range for Bitcoin in ZAR over the past 30 days?"

**Or:**
> "Analyze ETHZAR price movements for the last week"

### Advanced Queries

**Ask Claude:**
> "Compare the 24-hour and 1-hour price movements for XBTEUR"

**Or:**
> "Show me the highest and lowest Bitcoin prices in the past month"

## Technical Details

### Authentication
- **Required**: Both historical data tools require API credentials
- **Endpoint**: Uses Luno's `/api/exchange/1/candles` endpoint
- **Rate Limits**: Subject to Luno's standard rate limiting (300 calls/minute)

### Data Limits
- **Maximum candles**: 1000 per request
- **Time range**: Depends on candle duration and start time
- **Currency pairs**: All Luno-supported trading pairs

### Error Handling
- **Invalid pairs**: Returns error with supported pairs suggestion
- **Invalid timeframes**: Returns error with supported durations
- **No data**: Returns error when no historical data is available
- **API errors**: Proper error propagation from Luno API

## Integration Examples

### Python Script Usage
```python
import asyncio
from datetime import datetime, timezone, timedelta
from luno_mcp_server.luno_client import LunoClient

async def get_bitcoin_week():
    client = LunoClient()
    
    # Get data from 7 days ago
    since_dt = datetime.now(timezone.utc) - timedelta(days=7)
    since = int(since_dt.timestamp() * 1000)
    
    # Get daily candles
    data = await client.get_candles("XBTZAR", since, 86400)
    return data

# Run it
result = asyncio.run(get_bitcoin_week())
```

### MCP Tool Testing
```bash
# Test the historical data functionality
python test_historical_data.py
```

## Troubleshooting

### Common Issues

1. **"Authentication required" error**
   - Ensure API credentials are set in environment variables
   - Check that credentials have the required permissions

2. **"No data available" error**
   - Try a different time range
   - Verify the trading pair is correct and active
   - Check if the start time is too far in the past

3. **"Invalid duration" error**
   - Use one of the supported duration values
   - Refer to the supported timeframes list above

4. **Rate limit errors**
   - Reduce request frequency
   - Implement proper rate limiting in your application

### Debug Mode
Enable debug logging by setting the environment variable:
```bash
export LUNO_MCP_LOG_LEVEL=DEBUG
```

## Best Practices

1. **Choose appropriate timeframes**
   - Use longer candles (24h, 7d) for trend analysis
   - Use shorter candles (1m, 5m) for detailed trading analysis

2. **Optimize requests**
   - Request only the data you need
   - Cache results when possible
   - Respect rate limits

3. **Handle errors gracefully**
   - Always check the `status` field in responses
   - Implement retry logic for transient errors
   - Provide fallback options for users

4. **Data validation**
   - Validate timestamp ranges before requests
   - Check for reasonable date ranges
   - Verify trading pair formats

## Future Enhancements

Potential future additions:
- Volume analysis tools
- Technical indicators (RSI, MACD, etc.)
- Price alerts and notifications
- Export functionality (CSV, JSON)
- Real-time streaming integration

## Support

For issues or feature requests related to historical data:
1. Check the troubleshooting section above
2. Review the Luno API documentation
3. Test with the provided test script
4. Check the main project documentation

---

**Note**: Historical data requires API authentication and is subject to Luno's terms of service and rate limits.