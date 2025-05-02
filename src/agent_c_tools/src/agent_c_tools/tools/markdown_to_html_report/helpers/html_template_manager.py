import logging
from pathlib import Path



logger = logging.getLogger(__name__)


class HtmlTemplateManager:
    """Helper class for managing HTML templates."""

    @staticmethod
    async def get_html_template() -> str:
        """Get the HTML template for the markdown viewer."""
        try:
            # If no workspace template found, try local file system
            local_template_path = Path(__file__).parent / "markdown-viewer-template.html"

            # Check if the template file exists
            if not local_template_path.exists():
                logger.warning(f"Template file not found: {local_template_path}")
                # Try alternate locations in case __file__ is not working as expected
                alt_paths = [
                    Path.cwd() / "markdown-viewer-template.html",
                    Path.cwd() / "tools" / "markdown_viewer" / "markdown-viewer-template.html",
                ]

                for alt_path in alt_paths:
                    if alt_path.exists():
                        local_template_path = alt_path
                        logger.info(f"Found template at alternate location: {local_template_path}")
                        break
                else:
                    raise FileNotFoundError("Could not find template file in workspace or local paths")

            # Read the template file from local file system
            with open(local_template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading template file: {e}")
            raise RuntimeError(f"Failed to load HTML template: {e}")