import json
import requests
from agent_c.toolsets import json_schema, Toolset


class HackerNewsTools(Toolset):
    """
    Hacker News content retrieval tool using the official Firebase API.
    
    This toolset provides access to Hacker News stories, enabling retrieval of top stories
    and job postings from the popular technology news and discussion platform.
    
    Available Methods:
        - get_top_stories: Fetch the top stories currently featured on Hacker News
        - get_job_stories: Fetch job postings from the Hacker News "Who is hiring?" threads
    
    Key Features:
        - Real-time access to Hacker News top stories
        - Job posting retrieval
        - Configurable result limits
        - No authentication required
    
    Requirements:
        - No API keys needed (uses public Firebase API)
        - requests Python package
    
    Usage Notes:
        - Results default to 10 items but can be customized
        - Stories include only titles (additional details require separate API calls)
        - Uses Hacker News Firebase API v0
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='hn')
        self.base_url = 'https://hacker-news.firebaseio.com/v0/'

    @json_schema(
        'Call this tool to get top stories from hacker news',
        {
            'limit': {
                'type': 'integer',
                'description': 'Number of Top Stories to display, Default to 10',
                'required': True
            }
        }
    )
    async def get_top_stories(self, **kwargs):
        result_count = kwargs.get('limit', 10)
        top_story_url = f"{self.base_url}/topstories.json?print=pretty"
        stories_ids = self.fetch_stories_ids(top_story_url, result_count)
        results = self.fetch_stories(stories_ids)
        return json.dumps(results)

    @json_schema(
        'Call this tool to get job stories from hacker news',
        {
            'limit': {
                'type': 'integer',
                'description': 'Number of Job Stories to display, Default to 10',
                'required': True
            }
        }
    )
    async def get_job_stories(self, **kwargs):
        result_count = kwargs.get('limit', 10)
        job_story_url = f"{self.base_url}/jobstories.json?print=pretty"
        stories_ids = self.fetch_stories_ids(job_story_url, result_count)
        results = self.fetch_stories(stories_ids)
        return json.dumps(results)

    def fetch_stories_ids(self, url, limit):
        response = requests.get(url)
        stories = response.content.decode('utf-8')
        return json.loads(stories)[:limit]

    def fetch_stories(self, stories_ids):
        stories_data = []
        for story_id in stories_ids:
            story_url = f"{self.base_url}/item/{story_id}.json?print=pretty"
            response = requests.get(story_url)
            try:
                story_data = response.json()
                title = story_data['title']
                if title:
                    stories_data.append({'title': title})
            except Exception as e:
                return json.dumps({'error': str(e)})
        return stories_data


Toolset.register(HackerNewsTools)
