def get_file_html(os_path: str, unc_path: str, additional_html: str = None):
    html_content = f"""
    <div style="padding: 20px; font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f8fafc;">
        <h2 style="color: #334155; margin-top: 0;">File Saved Successfully</h2>

        {f"<div style='margin-bottom: 16px;'>{additional_html}</div>" if additional_html else ""}

        <div style="background-color: #fff7ed; border-left: 4px solid #f97316; padding: 16px; margin-bottom: 20px;">
            <p style="margin: 0; font-weight: 500; color: #9a3412;">Browser Security Notice</p>
            <p style="margin: 8px 0 0 0;">Due to browser security restrictions, you'll need to manually open the file:</p>
        </div>

        <div style="margin-bottom: 16px;">
            <p><strong>File path:</strong> <br/>
            <code style="background: #e2e8f0; padding: 8px; border-radius: 4px; display: block; margin-top: 8px; word-break: break-all;">{unc_path}</code>
            <p style="margin: 0;"></p>
            </p>
        </div>

        <div style="margin-top: 16px;">
            <a href="{os_path}" target="_blank" style="display: inline-block; background-color: #3b82f6; color: white; text-decoration: none; padding: 10px 16px; border-radius: 6px; font-weight: 500;">Try Direct Link</a>
            <span style="margin-left: 8px; color: #6b7280;">(may not work due to browser restrictions)</span>
        </div>
    </div>
                """
    return html_content