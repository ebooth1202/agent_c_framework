import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HtmlTemplateManager:
    """Helper class for managing HTML templates."""

    @staticmethod
    async def get_html_template(filename: str = "markdown-viewer-template.html") -> str:
        """Get the HTML template for the markdown viewer.

        Args:
            filename: Template filename (default: "markdown-viewer-template.html")

        Returns:
            str: The HTML template content

        Raises:
            FileNotFoundError: If the template file doesn't exist
            RuntimeError: If there's an error reading the file
        """
        try:
            template_path = Path(__file__).parent / filename

            if not template_path.exists():
                raise FileNotFoundError(f"Template file not found: {template_path}")

            with open(template_path, 'r', encoding='utf-8') as file:
                template_content = file.read()
                # logger.info(f"Successfully loaded template: {template_path}")
                return template_content

        except FileNotFoundError:
            logger.error(f"Template file not found: {filename}")
            raise
        except Exception as e:
            logger.error(f"Error reading template file {filename}: {e}")
            raise RuntimeError(f"Failed to load HTML template: {e}")