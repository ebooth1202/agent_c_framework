import asyncio
import json
from typing import Union
from urllib.parse import quote_plus

import httpx
import logging
from .constants import _Unit, METRIC, IMPERIAL
from .enums import Locale
from .forecast import BaseForecast, HourlyForecast, DailyForecast, Forecast


class Weather:
    def __init__(self, locale: str = 'en', unit: str = 'imperial'):
        self.locale = Locale(locale)
        self.unit = IMPERIAL if unit.lower() == 'imperial' else METRIC
        self.logger: logging.Logger = logging.getLogger(__name__)

    async def get_forecast(self, location: str) -> Forecast | str:
        url = f'https://{self.locale.value}.wttr.in/{quote_plus(location)}?format=j1'
        try:
            return await self._fetch_url(url)
        except Exception as e:
            message = f"Error fetching weather from: {url}.  Message: {str(e)}"
            self.logger.error(message)
            return message

    async def _fetch_url(self, url: str, raw: bool = False, max_retries: int = 3) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
            'Content-Type': 'application/json'
        }

        for attempt in range(max_retries):
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(url, headers=headers)

                    if response.status_code == 404 and response.text:
                        self.logger.warning(f'Got 404 but received content for URL: {url}')
                        response_content = response.text
                        if not raw:
                            response_content = self._format_content(response.content, url)
                        return response_content

                    response.raise_for_status()
                    response_content = response.text

                    if not raw:
                        response_content = self._format_content(response.content, url)
                    return response_content

                except httpx.HTTPStatusError as e:
                    if attempt == max_retries - 1:
                        self.logger.error(f'HTTP error occurred: {e}')
                        raise
                    await asyncio.sleep(1 * (attempt + 1))  # exponential backoff
                except httpx.RequestError as e:
                    self.logger.error(f'Request error occurred: {e}')
                    raise
                except Exception as e:
                    self.logger.error(f'An error occurred: {e}')
                    raise

    def _format_content(self, content: Union[str, bytes], url: str) -> Forecast:
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            data = json.loads(content)
            return Forecast(data, self.unit, self.locale)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON from {url}")
            raise
        except Exception as e:
            self.logger.error(f"Error formatting content from {url}: {str(e)}")
            raise

    async def get_formatted_weather_data(self, location: str) -> str:
        """
        Get weather data formatted as JSON string for tool consumption.
        
        Args:
            location: The location to get weather for
            
        Returns:
            JSON string with formatted weather data or error message
        """
        try:
            weather = await self.get_forecast(location)
            
            # Handle case where get_forecast returns an error string
            if isinstance(weather, str):
                self.logger.error(f"Weather API returned error: {weather}")
                return f"Error getting weather: {weather}"
            
            # Process daily forecasts
            forecasts = []
            for forecast in weather.daily_forecasts:
                forecasts.append({
                    'date': forecast.date.strftime('%Y-%m-%d'),
                    'high_temperature': forecast.highest_temperature,
                    'low_temperature': forecast.lowest_temperature
                })
            
            # Build the response structure
            weather_data = {
                "currently": {
                    "current_temperature": weather.temperature,
                    "sky": weather.kind.emoji,
                    "feels_like": weather.feels_like,
                    "humidity": weather.humidity,
                    "wind_speed": weather.wind_speed,
                    "wind_direction": (weather.wind_direction.value + weather.wind_direction.emoji),
                    "visibility": weather.visibility,
                    "uv_index": weather.ultraviolet.index,
                    "description": weather.description,
                    "forecasts": forecasts
                }
            }
            
            return json.dumps(weather_data)
            
        except Exception as e:
            error_msg = f"Error getting weather: {str(e)}"
            self.logger.error(error_msg)
            return error_msg