import json

import wikipedia

from agent_c.toolsets import Toolset, json_schema
from agent_c.util import filter_dict_by_keys

class WikipediaTools(Toolset):
    """
    Wikipedia search and content retrieval tool.
    
    This toolset provides access to Wikipedia's vast knowledge base, enabling searches for
    articles and information from the world's largest online encyclopedia.
    
    Available Methods:
        - search_wiki: Search Wikipedia and retrieve article information
    
    Key Features:
        - Search Wikipedia articles by query
        - Returns structured results with article IDs, titles, and descriptions
        - Free to use with no API key required
    
    Requirements:
        - wikipedia Python package
        - No authentication required
    
    Usage Notes:
        - Generic search terms may return keyword lists rather than full articles
        - Results are filtered to include relevant metadata (id, key, title, description)
        - This tool may benefit from refactoring for enhanced search capabilities
    """

    def __init__(self, **kwargs):
        super().__init__(name='wikipedia', **kwargs)

    @json_schema(
        'Perform a wikipedia search using this tool',
        {
            'search': {
                'type': 'string',
                'description': 'Query input to search Wikipedia',
                'required': True
            },
        }
    )
    async def search_wiki(self, **kwargs):
        search_query = kwargs.get('search')
        wanted_keys = [
            'id',
            'key',
            'title',
            'description'
        ]
        results = wikipedia.search(search_query)
        filtered_results = filter_dict_by_keys(results, wanted_keys)
        # TODO: This tool needs refactored to better search wikipedia - see https://medium.com/@shashankvats/building-a-wikipedia-search-engine-with-langchain-and-streamlit-d63cb11181d0 for ideas
        if filtered_results is None or len(filtered_results) == 0:
            # if you search a generic term, you'll get a list of search results keywords returned
            # Causing filtered_results to be empty or none
            return json.dumps(results)
        else:
            return json.dumps(filtered_results)


Toolset.register(WikipediaTools)
