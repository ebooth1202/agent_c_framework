import json

from markdownify import markdownify
from agent_c_tools.tools.web.formatters.base import ContentFormatter
import re
from bs4 import BeautifulSoup, Comment

class ZillowFormatter(ContentFormatter):
    """
    A Formatter that converts the entire HTML page to Markdown without content extraction.
    Inherits from ContentFormatter.
    """

    @staticmethod
    def get_property_info(inner_json):
        """
        Extract property information from the inner JSON.  In Zillow hidden json data may be in
        ForSaleShopperPlatformFullRenderQuery or NotForSaleShopperPlatformFullRenderQuery key.  This handles both. and any others
        so long as ShopperPlatformFullRenderQuery portion is present.
        Args:
            inner_json:

        Returns:
            dict: Property information
        """
        try:
            # Try to find any key containing the query pattern
            query_key = next((k for k in inner_json.keys()
                              if 'ShopperPlatformFullRenderQuery' in k), None)

            if not query_key:
                raise KeyError("No query key found")

            property_data = inner_json[query_key].get("property")
            if not property_data:
                raise KeyError("No property data found")

            return property_data

        except (AttributeError, KeyError) as e:
            raise KeyError(f"Failed to extract property info: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error while extracting property info: {str(e)}")

    def format(self, content: str, url: str) -> str:
        """
        Override format method to convert the entire page.
        """
        try:

           # Clean the HTML first
            soup = BeautifulSoup(content, 'html.parser')

            script_tag = soup.find('script', id='__NEXT_DATA__')
            json_data = script_tag.string
            json_data2 = json.loads(json_data)
            gdp_cache = json_data2.get('props', {}).get('pageProps', {}).get('componentProps', {}).get('gdpClientCache', '{}')
            inner_json = json.loads(gdp_cache)
            # property_info = inner_json[
            #     "NotForSaleShopperPlatformFullRenderQuery{\"zpid\":29077246,\"altId\":null,\"deviceType\":\"tablet\"}"][
            #     "property"]
            try:
               property_info = self.get_property_info(inner_json)
            except Exception as e:
               return f"Could not get property info: {e}"

            markdown = f"""
            # JSON WebPage Property Details
            - **Lot Size**: {property_info.get('lotSize', 'Unknown')} sqft or {property_info.get('lotAreaValue', 'Unknown')} {property_info.get('lotAreaUnits','Unknown')}
            - **Living Space**: {property_info.get('livingAreaValue', 'Unknown')} {property_info.get('livingAreaUnitsShort', 'Unknown')}
            - **Year Built**: {property_info.get('yearBuilt', 'Unknown')}
            - **Bedrooms**: {property_info.get('bedrooms', 'Unknown')}
            - **Bathrooms**: {property_info.get('bathrooms', 'Unknown')}          
            - **Currently Rented**: {property_info.get('isNonOwnerOccupied', 'Unknown')}
            - **Stories:** {property_info.get('stories', property_info.get('storiesTotal', 'Unknown'))}
            ## Description
            - **Property Type:** {property_info.get('resoFacts', {}).get('atAGlanceFacts', [{}])[0].get('factValue')}
            - **Description:** {property_info.get('description', 'Unknown')}
            """
            return markdown

        except Exception as e:
            # If anything goes wrong, return error as markdown
            return f"# Error Processing Property Data\nAn error occurred: {str(e)}"

