"""
Integration tests for the weather tool using debug_tool.
These tests call the actual WeatherTools interface that users interact with.
"""
import pytest
import json
import asyncio
import sys
import os

# from agent_c_tools.tools.tool_debugger.debug_tool import ToolDebugger

# Add the tool_debugger directory to the path to import debug_tool
tool_debugger_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
    'tool_debugger'
)
sys.path.insert(0, tool_debugger_path)

# from debug_tool import ToolDebugger
from ...tool_debugger.debug_tool import ToolDebugger


class TestWeatherToolsIntegration:
    """Integration tests for WeatherTools that test the complete user interface."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.debugger = None
    
    def teardown_method(self):
        """Clean up after each test method."""
        if self.debugger:
            # Clean up any resources if needed
            pass
    
    async def setup_weather_tool(self):
        """Helper method to set up the weather tool for testing."""
        # The ToolDebugger will automatically load .env and .local_workspaces.json 
        # from C:\Users\justj\PycharmProjects\agent_c\
        self.debugger = ToolDebugger(init_local_workspaces=False)
        await self.debugger.setup_tool(
            tool_import_path='agent_c_tools.WeatherTools',
            tool_opts={}  # API keys and config loaded automatically from .env
        )
        return self.debugger
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_weather_tool_real_location(self):
        """Test getting weather through the actual tool interface."""
        debugger = await self.setup_weather_tool()
        
        # Call the tool through its actual interface
        results = await debugger.run_tool_test(
            tool_name='get_current_weather',
            tool_params={'location_name': 'New York'}
        )
        
        # Extract and validate the content
        content = debugger.extract_content_from_results(results)
        assert content is not None
        assert not content.startswith("Error getting weather:")
        
        # Parse and validate JSON structure
        structured_content = debugger.extract_structured_content(results)
        assert structured_content is not None
        assert "currently" in structured_content
        
        currently = structured_content["currently"]
        
        # Validate required fields exist
        required_fields = [
            "current_temperature", "sky", "feels_like", "humidity",
            "wind_speed", "wind_direction", "visibility", "uv_index",
            "description", "forecasts"
        ]
        
        for field in required_fields:
            assert field in currently, f"Missing field: {field}"
        
        # Validate data types and ranges
        assert isinstance(currently["current_temperature"], int)
        assert isinstance(currently["feels_like"], int)
        assert isinstance(currently["humidity"], int)
        assert 0 <= currently["humidity"] <= 100
        assert isinstance(currently["forecasts"], list)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_weather_tool_invalid_location(self):
        """Test error handling through the tool interface."""
        debugger = await self.setup_weather_tool()
        
        # Call with invalid location
        results = await debugger.run_tool_test(
            tool_name='get_current_weather',
            tool_params={'location_name': 'InvalidLocationThatDoesNotExist12345'}
        )
        
        # Should get an error message
        content = debugger.extract_content_from_results(results)
        assert content is not None
        assert content.startswith("Error getting weather:")
    
    @pytest.mark.asyncio
    async def test_weather_tool_missing_parameter(self):
        """Test handling of missing location parameter through tool interface."""
        debugger = await self.setup_weather_tool()
        
        # Call without location_name parameter
        results = await debugger.run_tool_test(
            tool_name='get_current_weather',
            tool_params={}
        )
        
        # Should handle missing parameter gracefully
        content = debugger.extract_content_from_results(results)
        assert content is not None
        # The tool should either return an error or handle None location appropriately
    
    @pytest.mark.asyncio
    async def test_weather_tool_multiple_locations(self):
        """Test the tool interface with multiple different locations."""
        debugger = await self.setup_weather_tool()
        
        locations = ["London", "Tokyo", "Sydney"]
        
        for location in locations:
            results = await debugger.run_tool_test(
                tool_name='get_current_weather',
                tool_params={'location_name': location}
            )
            
            content = debugger.extract_content_from_results(results)
            assert content is not None
            
            # If we get valid results (not an error), validate structure
            if not content.startswith("Error getting weather:"):
                structured_content = debugger.extract_structured_content(results)
                if structured_content:
                    assert "currently" in structured_content
                    assert isinstance(structured_content["currently"]["current_temperature"], int)
    
    @pytest.mark.asyncio
    async def test_weather_tool_available_functions(self):
        """Test that the weather tool is properly set up and available."""
        debugger = await self.setup_weather_tool()
        
        # Check that the tool is available
        available_tools = debugger.get_available_tool_names()
        assert 'get_current_weather' in available_tools
        
        # Print tool info for debugging
        debugger.print_tool_info()
    
    @pytest.mark.asyncio
    async def test_weather_tool_response_consistency(self):
        """Test that tool responses are consistent with expected format."""
        debugger = await self.setup_weather_tool()
        
        # Get weather for a known location
        results = await debugger.run_tool_test(
            tool_name='get_current_weather',
            tool_params={'location_name': 'Boston'}
        )
        
        content = debugger.extract_content_from_results(results)
        
        # Skip if we got an error (API issues, etc.)
        if content.startswith("Error getting weather:"):
            pytest.skip("API returned error, skipping consistency test")
        
        # Validate the response structure matches what we expect
        structured_content = debugger.extract_structured_content(results)
        assert structured_content is not None
        
        # Test the exact structure we expect from the tool
        assert isinstance(structured_content, dict)
        assert list(structured_content.keys()) == ["currently"]
        
        currently = structured_content["currently"]
        assert isinstance(currently, dict)
        
        # Test that forecasts have the right structure
        for forecast in currently["forecasts"]:
            assert isinstance(forecast, dict)
            expected_keys = {"date", "high_temperature", "low_temperature"}
            assert set(forecast.keys()) == expected_keys
            
            # Validate date format (YYYY-MM-DD)
            date_str = forecast["date"]
            assert len(date_str) == 10
            assert date_str[4] == "-" and date_str[7] == "-"
    
    @pytest.mark.asyncio
    async def test_weather_tool_parameter_handling(self):
        """Test that the tool properly handles different parameter formats."""
        debugger = await self.setup_weather_tool()
        
        # Test with various parameter formats
        test_cases = [
            {'location_name': 'Chicago'},
            {'location_name': 'New York, NY'},
            {'location_name': 'Paris, France'},
        ]
        
        for params in test_cases:
            results = await debugger.run_tool_test(
                tool_name='get_current_weather',
                tool_params=params
            )
            
            content = debugger.extract_content_from_results(results)
            assert content is not None
            # Each should either return valid weather data or a reasonable error


# Optional: Test runner for just integration tests
if __name__ == "__main__":
    print("Running Weather Tools Integration Tests...")
    pytest.main([__file__, "-v"])
