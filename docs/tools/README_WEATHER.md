# Weather Tool

## What This Tool Does

The Weather Tool enables agents to provide current weather conditions and forecasts for any location worldwide. This capability gives you instant access to up-to-date weather information during your conversation without needing to switch to a separate weather app or website.

## Key Capabilities

Agents equipped with this tool can provide comprehensive weather information including:

- **Current Conditions**: Get real-time temperature, sky conditions, and "feels like" temperature
- **Weather Details**: Access humidity levels, wind speed and direction, and visibility
- **Health Indicators**: Check UV index for sun protection planning
- **Visual Context**: Weather descriptions include helpful emoji for quick visual reference
- **Forward Planning**: View forecasts for upcoming days with high and low temperatures

## Practical Use Cases

- **Travel Planning**: Check weather conditions for destinations before or during trips
- **Daily Preparation**: Get informed about the day's weather to dress appropriately
- **Event Planning**: Check forecasts for upcoming outdoor activities or events
- **Weather-dependent Decisions**: Make informed choices about outdoor work, exercise, or leisure activities
- **Safety Awareness**: Stay informed about potential weather-related hazards

## Example Interactions

### Basic Weather Check

**User**: "What's the weather like in Chicago today?"

**Agent**: *Provides current temperature, conditions, and feels-like temperature for Chicago, along with today's forecast for high and low temperatures and any notable conditions.*

### Travel Planning

**User**: "I'm traveling to Barcelona next week. What's the weather forecast looking like?"

**Agent**: *Retrieves and shares the multi-day forecast for Barcelona, highlighting temperature trends and any significant weather patterns expected during the coming week.*

### Detailed Weather Information

**User**: "I'm planning to go hiking near Seattle tomorrow. Can you give me detailed weather information including wind and UV index?"

**Agent**: *Provides comprehensive weather data for the Seattle area, with emphasis on hiking-relevant factors like wind conditions, UV index, and any precipitation forecasts.*

## Configuration Requirements

No special configuration is required to use this tool. Weather information is available for locations worldwide without needing any accounts or API keys.

## Important Considerations

### Location Specificity

For best results:
- Provide specific city names when possible
- For common city names (like Springfield), include state/province or country
- You can ask for weather by neighborhood, landmark, or airport code

### Available Weather Information

The tool provides these key weather elements:
- Current temperature (Fahrenheit or Celsius)
- Weather condition with descriptive emoji
- "Feels like" temperature accounting for humidity and wind
- Humidity percentage
- Wind speed and direction
- Visibility distance
- UV index for sun exposure planning
- Daily forecasts with high and low temperatures

### International Support

- Weather information is available globally for virtually any location
- You can specify temperature units (Fahrenheit or Celsius) if you have a preference
- Times and dates reflect the local time zone of the requested location

### Data Source

Weather information comes from wttr.in, a reliable public weather service. As with any forecast, accuracy may vary, particularly for predictions several days in advance.