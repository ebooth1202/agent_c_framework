from typing import Dict, Any


class MediaEventHelper:
    """Helper for raising media events."""

    @staticmethod
    async def create_result_html(output_info: Dict[str, Any]) -> str:
        """Generate HTML content for displaying results."""
        file_system_path = output_info.get('file_system_path')
        output_path = output_info.get('output_path', '')
        output_filename = output_info.get('output_filename', '')
        file_count = output_info.get('file_count', 0)

        # Create file:// URL
        if file_system_path:
            url_path = file_system_path.replace('\\', '/')
            file_url = f"file:///{url_path}" if not url_path.startswith('/') else f"file://{url_path}"
        else:
            file_url = f"file:///{output_path.replace('//', '').replace('\\', '/')}"

        # Generate appropriate HTML based on output type
        if output_info.get('type') == 'html_viewer':
            title = "Report Generated Successfully"
            content_desc = f"{file_count} markdown files"
        elif output_info.get('type') == 'docx':
            title = "Word Document Generated Successfully"
            content_desc = f"Style: {output_info.get('style', 'default')}"
        else:
            title = "File Generated Successfully"
            content_desc = ""

        html_content = f"""
        <div style="padding: 20px; font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f8fafc;">
            <h2 style="color: #334155; margin-top: 0;">{title}</h2>

            <div style="background-color: #f1f5f9; border-radius: 6px; padding: 16px; margin-bottom: 20px;">
                <p style="margin: 0 0 8px 0;"><strong>File:</strong> {output_filename}</p>
                <p style="margin: 0 0 8px 0;"><strong>Contents:</strong> {content_desc}</p>
                <p style="margin: 0;"><strong>Location:</strong> <code style="background: #e2e8f0; padding: 2px 4px; border-radius: 4px;">{output_path}</code></p>
            </div>

            <div style="background-color: #fff7ed; border-left: 4px solid #f97316; padding: 16px; margin-bottom: 20px;">
                <p style="margin: 0; font-weight: 500; color: #9a3412;">Browser Security Notice</p>
                <p style="margin: 8px 0 0 0;">Due to browser security restrictions, you'll need to manually open the file:</p>
            </div>

            <div style="margin-bottom: 16px;">
                <p><strong>File path:</strong> <br/>
                <code style="background: #e2e8f0; padding: 8px; border-radius: 4px; display: block; margin-top: 8px; word-break: break-all;">{file_system_path if file_system_path else output_path}</code>
                </p>
            </div>
        </div>
        """
        return html_content

    @staticmethod
    async def create_markdown_media(output_info: Dict[str, Any]) -> str:
        """Generate HTML content for displaying results."""
        file_system_path = output_info.get('file_system_path')
        output_path = output_info.get('output_path', '')
        output_filename = output_info.get('output_filename', '')
        file_count = output_info.get('file_count', 0)

        # Create file:// URL
        if file_system_path:
            url_path = file_system_path.replace('\\', '/')
            file_url = f"file:///{url_path}" if not url_path.startswith('/') else f"file://{url_path}"
        else:
            file_url = f"file:///{output_path.replace('//', '').replace('\\', '/')}"

        # Generate appropriate HTML based on output type
        if output_info.get('type') == 'html_viewer':
            title = "Report Generated Successfully"
            content_desc = f"{file_count} markdown files"
        elif output_info.get('type') == 'docx':
            title = "Word Document Generated Successfully"
            content_desc = f"Style: {output_info.get('style', 'default')}"
        else:
            title = "File Generated Successfully"
            content_desc = ""

        markdown_content = f"""# Your Report is Ready
                        # The report containing **{file_count} markdown files** has been generated.
                        # ## Details
                        # - Filename: `{output_filename}`
                        # - Location: `{file_url}`
                        #
                        # [Click here to open the report]({file_url})"""
        return markdown_content