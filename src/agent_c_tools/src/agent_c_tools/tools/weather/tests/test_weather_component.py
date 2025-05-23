"""
Component tests for the weather client.
These tests call the Weather class directly to validate its functionality.
"""
import pytest
import json
import asyncio
from datetime import date
import sys
import os

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..util.client import Weather


class TestWeatherClientComponent:
    """Component tests for Weather client that test real functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.weather_client = Weather(locale='en', unit='imperial')
    
    @pytest.mark.component
    @pytest.mark.asyncio
    async def test_get_formatted_weather_data_real_location(self):
        """Test getting real weather data for a known location."""
        location = "New York"
        
        result = await self.weather_client.get_formatted_weather_data(location)
        
        # Should return a JSON string, not an error
        assert not result.startswith("Error getting weather:")
        
        # Parse the JSON and validate structure
        weather_data = json.loads(result)
        assert "currently" in weather_data
        
        currently = weather_data["currently"]
        
        # Validate required fields exist
        required_fields = [
            "current_temperature", "sky", "feels_like", "humidity",
            "wind_speed", "wind_direction", "visibility", "uv_index",
            "description", "forecasts"
        ]
        
        for field in required_fields:
            assert field in currently, f"Missing field: {field}"
        
        # Validate data types and ranges for temperature data
        assert isinstance(currently["current_temperature"], int)
        assert isinstance(currently["feels_like"], int)
        assert -50 <= currently["current_temperature"] <= 150  # Reasonable temp range in F
        
        # Validate humidity is a percentage
        assert isinstance(currently["humidity"], int)
        assert 0 <= currently["humidity"] <= 100
        
        # Validate forecasts is a list
        assert isinstance(currently["forecasts"], list)
        
        # If there are forecasts, validate their structure
        if currently["forecasts"]:
            forecast = currently["forecasts"][0]
            assert "date" in forecast
            assert "high_temperature" in forecast
            assert "low_temperature" in forecast
            
            # Validate date format (YYYY-MM-DD)
            date_str = forecast["date"]
            assert len(date_str) == 10
            assert date_str[4] == "-" and date_str[7] == "-"
            
            # Validate temperature values
            assert isinstance(forecast["high_temperature"], int)
            assert isinstance(forecast["low_temperature"], int)
            assert forecast["low_temperature"] <= forecast["high_temperature"]
    
    @pytest.mark.component
    @pytest.mark.asyncio
    async def test_get_formatted_weather_data_different_units(self):
        """Test weather data with metric units."""
        metric_client = Weather(locale='en', unit='metric')
        location = "London"
        
        result = await metric_client.get_formatted_weather_data(location)
        
        # Should return valid JSON
        assert not result.startswith("Error getting weather:")
        weather_data = json.loads(result)
        
        # Temperatures should be in Celsius range (roughly)
        temp = weather_data["currently"]["current_temperature"]
        assert isinstance(temp, int)
        assert -40 <= temp <= 50  # Reasonable temp range in C
    
    @pytest.mark.asyncio
    async def test_get_formatted_weather_data_invalid_location(self):
        """Test handling of invalid location."""
        location = "InvalidLocationThatDoesNotExist12345"
        
        result = await self.weather_client.get_formatted_weather_data(location)
        
        # Should return an error message
        assert result.startswith("Error getting weather:")
    
    @pytest.mark.asyncio
    async def test_get_formatted_weather_data_multiple_locations(self):
        """Test multiple different valid locations."""
        locations = ["Paris", "Tokyo", "Sydney"]
        
        for location in locations:
            result = await self.weather_client.get_formatted_weather_data(location)
            
            # Should get valid results for all major cities
            if not result.startswith("Error getting weather:"):
                weather_data = json.loads(result)
                assert "currently" in weather_data
                assert isinstance(weather_data["currently"]["current_temperature"], int)
    
    @pytest.mark.asyncio
    async def test_weather_data_consistency(self):
        """Test that the formatted data is consistent with raw forecast data."""
        location = "Chicago"
        
        # Get both raw and formatted data
        raw_forecast = await self.weather_client.get_forecast(location)
        formatted_result = await self.weather_client.get_formatted_weather_data(location)
        
        # Skip if we got an error
        if isinstance(raw_forecast, str) or formatted_result.startswith("Error"):
            pytest.skip("API returned error, skipping consistency test")
        
        formatted_data = json.loads(formatted_result)
        currently = formatted_data["currently"]
        
        # Compare key values between raw and formatted
        assert currently["current_temperature"] == raw_forecast.temperature
        assert currently["feels_like"] == raw_forecast.feels_like
        assert currently["humidity"] == raw_forecast.humidity
        assert currently["wind_speed"] == raw_forecast.wind_speed
        assert currently["visibility"] == raw_forecast.visibility
        assert currently["uv_index"] == raw_forecast.ultraviolet.index
        assert currently["description"] == raw_forecast.description
        
        # Check forecast count matches
        assert len(currently["forecasts"]) == len(raw_forecast.daily_forecasts)
    
    def test_weather_client_initialization(self):
        """Test Weather client can be initialized with different settings."""
        # Test various initialization combinations
        clients = [
            Weather(),  # defaults
            Weather(locale='en', unit='imperial'),
            Weather(locale='en', unit='metric'),
            Weather(locale='fr', unit='metric')
        ]
        
        for client in clients:
            assert hasattr(client, 'locale')
            assert hasattr(client, 'unit')
            assert hasattr(client, 'logger')
    
    @pytest.mark.asyncio
    async def test_json_output_format(self):
        """Test that the JSON output has the expected structure."""
        location = "Boston"
        
        result = await self.weather_client.get_formatted_weather_data(location)
        
        if result.startswith("Error getting weather:"):
            pytest.skip("API returned error, skipping JSON format test")
        
        # Should be valid JSON
        weather_data = json.loads(result)
        
        # Test the exact structure we expect
        assert isinstance(weather_data, dict)
        assert list(weather_data.keys()) == ["currently"]
        
        currently = weather_data["currently"]
        assert isinstance(currently, dict)
        
        # Test that forecasts have the right structure
        for forecast in currently["forecasts"]:
            assert isinstance(forecast, dict)
            expected_keys = {"date", "high_temperature", "low_temperature"}
            assert set(forecast.keys()) == expected_keys


# Optional: Test runner for just component tests
if __name__ == "__main__":
    print("Running Weather Client Component Tests...")
    pytest.main([__file__, "-v"])
