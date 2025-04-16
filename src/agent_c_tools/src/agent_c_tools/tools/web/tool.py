import re
import httpx
import json
import logging
import datetime

from typing import List, Optional
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from agent_c import json_schema, Toolset
from agent_c_tools.tools.web.formatters import *
from agent_c_tools.tools.web.util.expires_header import expires_header_to_cache_seconds

class WebTools(Toolset):
    """
    WebTools class to fetch and format web page content.

    Attributes:
        default_formatter (ContentFormatter): Default formatter to use when no specific formatter is found.
        formatters (List[ContentFormatter]): List of custom formatters for specific URL patterns.
        cache (Cache): Cache object for storing responses.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='web', required_tools=['workspace'], use_prefix=False)
        self.default_formatter: ContentFormatter = kwargs.get('wt_default_formatter', ReadableFormatter(re.compile(r".*")))
        self.formatters: List[ContentFormatter] = kwargs.get('wt_formatters', [])
        self.driver = self.__init__wd()


    def __init__wd(self):
        try:
            options = Options()
            options.add_argument("--headless=new")
            # This is to get chrome driver to ignore SSL handshake between chromium and chrome, that resulted in the following error:
            # [23312:116032:0716/133843.497:ERROR:ssl_client_socket_impl.cc(878)] handshake failed; returned -1, SSL error code 1, net_error -100
            options.add_argument('--ignore-certificate-errors-spki-list')
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            # This is to get rid of the following error:
            # [115200:111428:0716/130536.999:ERROR:sandbox_win.cc(913)] Sandbox cannot access executable....
            # https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md
            options.add_argument('--no-sandbox')  # This is riskier
            options.add_argument('--log-level=3')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(options=options)
        except Exception as e:
            return None

        return driver

    def __del__(self):
        if self.driver:
            logging.info("Closing WebDriver")
            self.driver.close()

    def format_content(self, content: str, url: str) -> str:
        """
        Find a suitable formatter for the given URL and format the content.

        Args:
            content (str): Content to be formatted.
            url (str): URL of the content.

        Returns:
            str: Formatted content in Markdown.
        """
        formatter = next((f for f in self.formatters if f.match(url)), self.default_formatter)
        return formatter.format(content, url)

    @json_schema(
        'This will trigger the client to display a wab page for the user.',
        {
            'url': {
                'type': 'string',
                'description': 'The URL of the web page you would like to display for the user',
                'required': True
            }
        }
    )
    async def open_webpage(self, **kwargs) -> str:
        url: str = kwargs.get('url')
        if url is None:
            return 'url is required'

        await self._raise_render_media(content_type="text/html", url=url)

        return f"Client displaying web page: {url}"


    @json_schema(
        'This tool allows you to fetch the content of a web page and convert it to Markdown format.',
        {
            'url': {
                'type': 'string',
                'description': 'The URL of the web page you would like to fetch',
                'required': True
            },
            'save_to_workspace': {
                'type': 'boolean',
                'description': 'Whether to save the markdown content to a workspace',
                'required': False,
                'default': False
            },
            'workspace_name': {
                'type': 'string',
                'description': 'Workspace name to use for saving the markdown file',
                'required': False,
                'default': 'project'
            },
            'file_path': {
                'type': 'string',
                'description': 'File path within the workspace to save the markdown file',
                'required': False
            }
        }
    )
    async def fetch_webpage(self, **kwargs) -> str:
        """
        Fetch a webpage's content and convert it to Markdown format using the specified formatter.

        Args:
            **kwargs: Keyword arguments containing the 'url' and possibly other configuration details.
                url: The URL of the web page to fetch
                raw: Whether to return the raw HTML instead of formatted markdown
                expire_secs: How long to cache the content
                save_to_workspace: Whether to save the markdown content to a workspace
                workspace_name: Workspace name to use for saving the markdown file
                file_path: File path within the workspace to save the markdown file

        Returns:
            str: Page content in Markdown format or an error message if an exception occurs.
                 If saving to workspace, returns a JSON string with the status.
        """
        url: str = kwargs.get('url')
        raw: bool = kwargs.get("raw", False)
        default_expire: int = kwargs.get("expire_secs", 3600)
        save_to_workspace: bool = kwargs.get("save_to_workspace", False)
        workspace_name: str = kwargs.get("workspace_name", "project")
        file_path: str = kwargs.get("file_path", None)

        if url is None:
            return 'url is required'

        response_content: Optional[str] = self.tool_cache.get(url)
        if response_content is not None:
            return response_content

        async with httpx.AsyncClient() as client:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"}
                response = await client.get(url, headers=headers)
                if response.status_code == 403 and self.driver is not None:
                    self.driver.get(url)
                    expires_in = 600
                    response_content = self.driver.page_source
                else:
                    response.raise_for_status()
                    expires_in = expires_header_to_cache_seconds(response.headers.get('expires'))
                    encoding = response.encoding or 'utf-8'
                    response_content = response.content.decode(encoding)

                if not raw:
                    response_content = self.format_content(response_content, url)

                if expires_in is not None:
                    self.tool_cache.set(url, response_content, expire=expires_in)
                    logging.debug(f'URL cached with expiration: {url}')
                else:
                    self.tool_cache.set(url, response_content, expire=default_expire)
                    logging.debug(f'URL cached with default expiration: {url}')

                # If save_to_workspace is true, save the content to the specified workspace
                if save_to_workspace:
                    try:
                        # If file_path is not provided, generate one based on the URL
                        if file_path is None:
                            # Extract domain from URL and create a clean filename
                            from urllib.parse import urlparse
                            parsed_url = urlparse(url)
                            domain = parsed_url.netloc.replace('.', '_')
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                            file_path = f"{domain}_{timestamp}.md"
                        
                        # Ensure file has .md extension
                        if not file_path.endswith('.md'):
                            file_path = f"{file_path}.md"
                        
                        # Get workspace toolset
                        workspace_tool = self.tool_chest.active_tools.get("workspace")
                        if workspace_tool is None:
                            return json.dumps({
                                'error': "Workspace tool not available. Cannot save markdown.",
                                'content': response_content
                            })
                        
                        # Find the workspace and save the content
                        workspace_obj = workspace_tool.find_workspace_by_name(workspace_name)
                        if workspace_obj is None:
                            return json.dumps({
                                'error': f"No workspace found with the name: {workspace_name}",
                                'content': response_content
                            })
                        
                        # Save the markdown content to the workspace
                        result = await workspace_obj.write(file_path=file_path, mode='write', data=response_content)
                        logging.info(f'Saved webpage content to workspace: {workspace_name} with file name: {file_path}')
                        
                        return json.dumps({
                            'result': result,
                            'message': f"Webpage content saved to {workspace_name}/{file_path}",
                            'file_path': file_path,
                            'workspace_name': workspace_name
                        })
                        
                    except Exception as e:
                        logging.error(f'Error saving to workspace: {str(e)}')
                        return json.dumps({
                            'error': f'Error saving to workspace: {str(e)}',
                            'content': response_content,
                            'result': result if result is not None else None
                        })
                else:
                    return response_content
            except httpx.HTTPStatusError as e:
                logging.error(f'HTTP error occurred: {e}')
                return f'HTTP error occurred: {e}'
            except httpx.RequestError as e:
                logging.error(f'Request error occurred: {e}')
                return f'Request error occurred: {e}'
            except Exception as e:
                logging.error(f'An error occurred: {e}')
                return f'An error occurred: {e}'


Toolset.register(WebTools)
