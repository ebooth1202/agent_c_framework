# Web Search Tools

This directory contains the unified web search system that consolidates all web search functionality into a single, powerful interface.

## Directory Structure

```
web_search/
├── web_search_tools.py          # Main unified interface (USE THIS)
├── base/                        # Core infrastructure
│   ├── engine.py               # Base engine interface
│   ├── models.py               # Data models and types
│   ├── registry.py             # Engine registry system
│   ├── router.py               # Intelligent routing logic
│   ├── validator.py            # Parameter validation
│   ├── standardizer.py         # Response standardization
│   └── error_handler.py        # Error handling
├── engines/                     # Engine adapters
│   ├── duckduckgo_engine.py    # DuckDuckGo adapter
│   ├── google_serp_engine.py   # Google SERP adapter
│   ├── tavily_engine.py        # Tavily research adapter
│   ├── wikipedia_engine.py     # Wikipedia adapter
│   ├── news_api_engine.py      # NewsAPI adapter
│   └── hacker_news_engine.py   # HackerNews adapter
├── deprecated/                  # Deprecated standalone tools
│   ├── google_trends/          # Google Trends (not integrated)
│   └── seeking_alpha/          # Seeking Alpha (not integrated)
├── duck_duck_go/               # Legacy tool (used by engine)
├── google_serp/                # Legacy tool (used by engine)
├── hacker_news/                # Legacy tool (used by engine)
├── news_api/                   # Legacy tool (used by engine)
├── tavily_research/            # Legacy tool (used by engine)
├── wikipedia/                  # Legacy tool (used by engine)
├── MIGRATION_GUIDE.md          # Migration guide
└── README.md                   # This file
```

## Quick Start

### Using the Unified Interface (Recommended)

```python
from agent_c_tools.tools.web_search import WebSearchTools

# Create the unified search tool
search = WebSearchTools()

# General web search with automatic engine selection
results = await search.web_search(query="machine learning")

# Specialized searches
news = await search.news_search(query="AI breakthroughs")
research = await search.research_search(query="quantum computing")
tech = await search.tech_search(query="Python frameworks")
```

### Available Search Methods

1. **`web_search()`** - General web search with intelligent engine routing
2. **`news_search()`** - News-optimized search
3. **`educational_search()`** - Academic and educational content
4. **`research_search()`** - Deep research with content analysis
5. **`tech_search()`** - Technology community content
6. **`flights_search()`** - Flight search
7. **`events_search()`** - Event search
8. **`get_engine_info()`** - Engine status and capabilities

### Engine Selection

```python
# Automatic selection (recommended)
results = await search.web_search(query="climate change")

# Explicit engine selection
results = await search.web_search(query="climate change", engine="tavily")

# Available engines: duckduckgo, google_serp, tavily, wikipedia, newsapi, hackernews
```

### Advanced Features

```python
results = await search.web_search(
    query="artificial intelligence research",
    search_type="research",
    max_results=20,
    include_domains=["arxiv.org", "nature.com"],
    exclude_domains=["wikipedia.org"],
    start_date="2023-01-01",
    end_date="2024-01-01",
    search_depth="advanced",
    language="en",
    region="us"
)
```

## Architecture

### Core Components

- **WebSearchTools**: Main unified interface
- **Engine Registry**: Manages available search engines
- **Engine Router**: Intelligent routing based on query analysis
- **Parameter Validator**: Validates and normalizes parameters
- **Error Handler**: Comprehensive error handling with fallbacks

### Engine Adapters

Each search provider has an adapter that:
- Implements the `BaseWebSearchEngine` interface
- Wraps the legacy tool implementation
- Standardizes responses to a common format
- Provides health monitoring and availability checking

### Intelligent Routing

The system automatically selects the best engine based on:
- Query content analysis (financial, technical, academic, etc.)
- Search type preferences
- Engine availability and health
- User preferences (explicit engine selection)

## Legacy Tools

Legacy individual tools are deprecated but still available for backward compatibility:

- `DuckDuckGoTools` → Use `WebSearchTools.web_search(engine="duckduckgo")`
- `GoogleSerpTools` → Use `WebSearchTools.web_search(engine="google_serp")`
- `NewsApiTools` → Use `WebSearchTools.news_search(engine="newsapi")`
- `TavilyResearchTools` → Use `WebSearchTools.research_search(engine="tavily")`
- `WikipediaTools` → Use `WebSearchTools.educational_search(engine="wikipedia")`
- `HackerNewsTools` → Use `WebSearchTools.tech_search(engine="hackernews")`

## Migration

See `MIGRATION_GUIDE.md` for detailed migration instructions from legacy tools to the unified interface.

## Benefits

- **Unified Interface**: Single tool for all search needs
- **Intelligent Routing**: Automatic engine selection
- **Standardized Responses**: Consistent JSON format
- **Enhanced Features**: Domain filtering, date ranges, etc.
- **Better Error Handling**: Comprehensive error management
- **Type Safety**: Full parameter validation
- **Extensible**: Easy to add new engines

## Future Plans

- Integration of Google Trends functionality
- Integration of Seeking Alpha functionality
- Additional search engines
- Advanced caching and performance optimization
- Enhanced query analysis and routing