from enum import Enum
from typing import Union
from .constants import WIND_DIRECTION_EMOJIS


class BasicEnum(Enum):
    """Base enum with improved string representation."""

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}.{self.name}'

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title()


class IndexedEnum(Enum):
    """Enum with numeric index for comparison operations."""

    def __init__(self, index: int):
        self.index = index

    def __lt__(self, other: Union['IndexedEnum', int, float]) -> bool:
        return self.index < getattr(other, 'index', other)

    def __eq__(self, other: Union['IndexedEnum', int, float]) -> bool:
        return self.index == getattr(other, 'index', other)

    def __gt__(self, other: Union['IndexedEnum', int, float]) -> bool:
        return self.index > getattr(other, 'index', other)

    def __hash__(self) -> int:
        return hash(self.index)

    def __int__(self) -> int:
        return self.index


class HeatIndex(IndexedEnum):
    """Represents a heat index based on Celsius temperature."""

    CAUTION = 25
    EXTREME_CAUTION = 35
    DANGER = 45
    EXTREME_DANGER = 55

    @classmethod
    def from_celsius(cls, celsius: float) -> 'HeatIndex':
        """Get heat index category from Celsius temperature."""
        if celsius <= 32:
            return cls.CAUTION
        elif celsius <= 39:
            return cls.EXTREME_CAUTION
        elif celsius <= 51:
            return cls.DANGER
        else:
            return cls.EXTREME_DANGER


class UltraViolet(BasicEnum):
    """Represents ultra-violet (UV) index."""

    LOW = 1
    MODERATE = 4
    HIGH = 6
    VERY_HIGH = 8
    EXTREME = 12

    def __init__(self, index: int):
        self.index = index

    def __lt__(self, other: Union['UltraViolet', int, float]) -> bool:
        return self.index < getattr(other, 'index', other)

    def __eq__(self, other: Union['UltraViolet', int, float]) -> bool:
        return self.index == getattr(other, 'index', other)

    def __gt__(self, other: Union['UltraViolet', int, float]) -> bool:
        return self.index > getattr(other, 'index', other)

    def __int__(self) -> int:
        return self.index

    @classmethod
    def from_index(cls, index: float) -> 'UltraViolet':
        """Get UV category from numeric index."""
        if index <= 2:
            return cls.LOW
        elif index <= 5:
            return cls.MODERATE
        elif index <= 7:
            return cls.HIGH
        elif index <= 10:
            return cls.VERY_HIGH
        else:
            return cls.EXTREME


class WindDirection(BasicEnum):
    """Represents a wind direction with degree ranges."""

    NORTH = ('N', 0.0)
    NORTH_NORTHEAST = ('NNE', 22.5)
    NORTHEAST = ('NE', 45.0)
    EAST_NORTHEAST = ('ENE', 67.5)
    EAST = ('E', 90.0)
    EAST_SOUTHEAST = ('ESE', 112.5)
    SOUTHEAST = ('SE', 135.0)
    SOUTH_SOUTHEAST = ('SSE', 157.5)
    SOUTH = ('S', 180.0)
    SOUTH_SOUTHWEST = ('SSW', 202.5)
    SOUTHWEST = ('SW', 225.0)
    WEST_SOUTHWEST = ('WSW', 247.5)
    WEST = ('W', 270.0)
    WEST_NORTHWEST = ('WNW', 292.5)
    NORTHWEST = ('NW', 315.0)
    NORTH_NORTHWEST = ('NNW', 337.5)

    def __init__(self, abbreviation: str, degrees: float):
        self.abbreviation = abbreviation
        self.degrees = degrees

    def contains_degrees(self, degrees: float) -> bool:
        """Check if given degrees fall within this wind direction's range."""
        if self is self.NORTH:
            return degrees > 348.75 or degrees <= 11.25
        elif self is self.NORTH_NORTHEAST:
            return 11.25 < degrees <= 33.75
        elif self is self.NORTHEAST:
            return 33.75 < degrees <= 56.25
        elif self is self.EAST_NORTHEAST:
            return 56.25 < degrees <= 78.75
        elif self is self.EAST:
            return 78.75 < degrees <= 101.25
        elif self is self.EAST_SOUTHEAST:
            return 101.25 < degrees <= 123.75
        elif self is self.SOUTHEAST:
            return 123.75 < degrees <= 146.25
        elif self is self.SOUTH_SOUTHEAST:
            return 146.25 < degrees <= 168.75
        elif self is self.SOUTH:
            return 168.75 < degrees <= 191.25
        elif self is self.SOUTH_SOUTHWEST:
            return 191.25 < degrees <= 213.75
        elif self is self.SOUTHWEST:
            return 213.75 < degrees <= 236.25
        elif self is self.WEST_SOUTHWEST:
            return 236.25 < degrees <= 258.75
        elif self is self.WEST:
            return 258.75 < degrees <= 281.25
        elif self is self.WEST_NORTHWEST:
            return 281.25 < degrees <= 303.75
        elif self is self.NORTHWEST:
            return 303.75 < degrees <= 326.25
        else:  # NORTH_NORTHWEST
            return 326.25 < degrees <= 348.75

    def __int__(self) -> int:
        return int(self.degrees)

    def __float__(self) -> float:
        return self.degrees

    @classmethod
    def from_degrees(cls, degrees: float) -> 'WindDirection':
        """Get wind direction from degrees."""
        # Normalize degrees to 0-360 range
        degrees = degrees % 360

        for direction in cls:
            if direction.contains_degrees(degrees):
                return direction
        return cls.NORTH  # fallback

    @property
    def emoji(self) -> str:
        """The emoji representing this wind direction."""
        return WIND_DIRECTION_EMOJIS[int(((self.degrees + 22.5) % 360) / 45.0)]


class Locale(Enum):
    """Represents the list of supported locales/languages."""

    AFRIKAANS = 'af'
    AMHARIC = 'am'
    ARABIC = 'ar'
    ARMENIAN = 'hy'
    AZERBAIJANI = 'az'
    BANGLA = 'bn'
    BASQUE = 'eu'
    BELARUSIAN = 'be'
    BOSNIAN = 'bs'
    BULGARIAN = 'bg'
    CATALAN = 'ca'
    CHINESE_SIMPLIFIED = 'zh'
    CHINESE_SIMPLIFIED_CHINA = 'zh-cn'
    CHINESE_TRADITIONAL_TAIWAN = 'zh-tw'
    CROATIAN = 'hr'
    CZECH = 'cs'
    DANISH = 'da'
    DUTCH = 'nl'
    ENGLISH = 'en'
    ESPERANTO = 'eo'
    ESTONIAN = 'et'
    FINNISH = 'fi'
    FRENCH = 'fr'
    FRISIAN = 'fy'
    GALICIAN = 'gl'
    GEORGIAN = 'ka'
    GERMAN = 'de'
    GREEK = 'el'
    HINDI = 'hi'
    HIRI_MOTU = 'ho'
    HUNGARIAN = 'hu'
    ICELANDIC = 'is'
    INDONESIAN = 'id'
    INTERLINGUA = 'ia'
    IRISH = 'ga'
    ITALIAN = 'it'
    JAPANESE = 'ja'
    JAVANESE = 'jv'
    KAZAKH = 'kk'
    KISWAHILI = 'sw'
    KOREAN = 'ko'
    KYRGYZ = 'ky'
    LATVIAN = 'lv'
    LITHUANIAN = 'lt'
    MACEDONIAN = 'mk'
    MALAGASY = 'mg'
    MALAYALAM = 'ml'
    MARATHI = 'mr'
    NORWEGIAN_BOKMAL = 'nb'
    NORWEGIAN_NYNORSK = 'nn'
    OCCITAN = 'oc'
    PERSIAN = 'fa'
    POLISH = 'pl'
    PORTUGUESE = 'pt'
    PORTUGUESE_BRAZIL = 'pt-br'
    ROMANIAN = 'ro'
    RUSSIAN = 'ru'
    SERBIAN = 'sr'
    SERBIAN_LATIN = 'sr-lat'
    SLOVAK = 'sk'
    SLOVENIAN = 'sl'
    SPANISH = 'es'
    SWEDISH = 'sv'
    TAMIL = 'ta'
    TELUGU = 'te'
    THAI = 'th'
    TURKISH = 'tr'
    UKRAINIAN = 'uk'
    UZBEK = 'uz'
    VIETNAMESE = 'vi'
    WELSH = 'cy'
    ZULU = 'zu'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}.{self.name}'

    def __str__(self) -> str:
        parts = self.name.split('_')
        if len(parts) == 1:
            return parts[0].title()
        else:
            language = ' '.join(parts[:-1]).title()
            region = parts[-1].upper()
            return f'{language} ({region})'


class Kind(BasicEnum):
    """Represents a weather forecast kind."""

    SUNNY = 113
    PARTLY_CLOUDY = 116
    CLOUDY = 119
    VERY_CLOUDY = 122
    FOG = 143
    LIGHT_SHOWERS = 176
    LIGHT_SLEET_SHOWERS = 179
    LIGHT_SLEET = 182
    THUNDERY_SHOWERS = 200
    LIGHT_SNOW = 227
    HEAVY_SNOW = 230
    LIGHT_RAIN = 266
    HEAVY_SHOWERS = 299
    HEAVY_RAIN = 302
    LIGHT_SNOW_SHOWERS = 323
    HEAVY_SNOW_SHOWERS = 335
    THUNDERY_HEAVY_RAIN = 389
    THUNDERY_SNOW_SHOWERS = 392

    @classmethod
    def from_code(cls, code: int) -> 'Kind':
        """Get weather kind from numeric code."""
        # Direct mapping
        try:
            return cls(code)
        except ValueError:
            pass

        # Alternative codes mapping
        if code in (248, 260):
            return cls.FOG
        elif code in (263, 353):
            return cls.LIGHT_SHOWERS
        elif code in (362, 365, 374):
            return cls.LIGHT_SLEET_SHOWERS
        elif code in (185, 281, 284, 311, 314, 317, 350, 377):
            return cls.LIGHT_SLEET
        elif code == 386:
            return cls.THUNDERY_SHOWERS
        elif code == 320:
            return cls.LIGHT_SNOW
        elif code in (329, 332, 338):
            return cls.HEAVY_SNOW
        elif code in (293, 296):
            return cls.LIGHT_RAIN
        elif code in (305, 356):
            return cls.HEAVY_SHOWERS
        elif code in (308, 359):
            return cls.HEAVY_RAIN
        elif code in (326, 368):
            return cls.LIGHT_SNOW_SHOWERS
        elif code in (371, 395):
            return cls.HEAVY_SNOW_SHOWERS
        else:
            return cls.SUNNY  # Default fallback

    @property
    def emoji(self) -> str:
        """The emoji representing this weather condition."""
        emoji_map = {
            self.CLOUDY: '☁️',
            self.FOG: '🌫',
            self.HEAVY_RAIN: '🌧',
            self.HEAVY_SHOWERS: '🌧',
            self.HEAVY_SNOW: '❄️',
            self.HEAVY_SNOW_SHOWERS: '❄️',
            self.LIGHT_RAIN: '🌦',
            self.LIGHT_SHOWERS: '🌦',
            self.LIGHT_SLEET: '🌧',
            self.LIGHT_SLEET_SHOWERS: '🌧',
            self.LIGHT_SNOW: '🌨',
            self.LIGHT_SNOW_SHOWERS: '🌨',
            self.PARTLY_CLOUDY: '⛅️',
            self.SUNNY: '☀️',
            self.THUNDERY_HEAVY_RAIN: '🌩',
            self.THUNDERY_SHOWERS: '⛈',
            self.THUNDERY_SNOW_SHOWERS: '⛈',
            self.VERY_CLOUDY: '☁️',
        }
        return emoji_map.get(self, '✨')


class Phase(BasicEnum):
    """Represents a moon phase."""

    NEW_MOON = 'New Moon'
    WAXING_CRESCENT = 'Waxing Crescent'
    FIRST_QUARTER = 'First Quarter'
    WAXING_GIBBOUS = 'Waxing Gibbous'
    FULL_MOON = 'Full Moon'
    WANING_GIBBOUS = 'Waning Gibbous'
    LAST_QUARTER = 'Last Quarter'
    WANING_CRESCENT = 'Waning Crescent'

    @property
    def emoji(self) -> str:
        """The emoji representing this moon phase."""
        emoji_map = {
            self.NEW_MOON: '🌑',
            self.WAXING_CRESCENT: '🌒',
            self.FIRST_QUARTER: '🌓',
            self.WAXING_GIBBOUS: '🌔',
            self.FULL_MOON: '🌕',
            self.WANING_GIBBOUS: '🌖',
            self.LAST_QUARTER: '🌗',
            self.WANING_CRESCENT: '🌘',
        }
        return emoji_map.get(self, '🌘')