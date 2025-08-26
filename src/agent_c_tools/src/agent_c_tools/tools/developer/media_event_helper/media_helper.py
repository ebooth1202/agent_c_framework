from typing import Dict, Any
import html

class MediaEventHelper:
    """Helper for raising media events."""

    @staticmethod
    async def stdout_html(output_info: Dict[str, Any]) -> str:
        """
        Render CommandExecutionResult-like info for git (stdout-focused) as HTML.
        Expected keys in output_info:
          - type = "git_stdout"
          - command, working_directory, status, return_code, duration_ms
          - stdout, stderr, truncated_stdout, truncated_stderr
          - (optional) max_lines: int (default 400)
        """
        command = output_info.get("command", "")
        working_directory = output_info.get("working_directory", "")
        status = output_info.get("status", "")
        return_code = output_info.get("return_code", None)
        duration_ms = output_info.get("duration_ms", None)

        stdout = output_info.get("stdout", "") or ""
        stderr = output_info.get("stderr", "") or ""
        trunc_out = bool(output_info.get("truncated_stdout", False))
        trunc_err = bool(output_info.get("truncated_stderr", False))

        # Show at most N lines (view-only limit). Executor-level truncation is separate.
        max_lines = int(output_info.get("max_lines", 400))
        lines = stdout.splitlines()
        line_count = len(lines)
        shown_lines = lines[:max_lines]
        clipped_view = line_count > max_lines
        shown_stdout = "\n".join(shown_lines)

        # Escape to be safe in HTML
        esc_cmd = html.escape(command)
        esc_wd = html.escape(working_directory)
        esc_stdout = html.escape(shown_stdout)
        esc_stderr = html.escape(stderr)

        # Little badges
        def badge(text, color="#334155", bg="#e2e8f0"):
            return f'<span style="display:inline-block;padding:2px 8px;border-radius:999px;background:{bg};color:{color};font-size:12px;line-height:20px;">{html.escape(str(text))}</span>'

        # Notices
        view_notice = f"{badge('view clipped')} Showing first {max_lines} of {line_count} lines." if clipped_view else ""
        trunc_notice = badge("truncated by executor") if trunc_out else ""

        html_content = f"""
        <div style="padding: 16px; font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f8fafc;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
            <strong style="color:#334155;">git output</strong>
            {badge(status or 'unknown')}
            {badge(f"rc={return_code}") if return_code is not None else ""}
            {badge(f"{duration_ms} ms")} 
            {trunc_notice}
            {view_notice}
          </div>

          <div style="margin-bottom: 8px; color:#475569;">
            <div><strong>Command:</strong> <code style="background:#e2e8f0; padding:2px 6px; border-radius:4px;">{esc_cmd}</code></div>
            <div><strong>Working dir:</strong> <code style="background:#e2e8f0; padding:2px 6px; border-radius:4px;">{esc_wd}</code></div>
          </div>

          <div style="border:1px solid #e2e8f0; border-radius:6px; background:#ffffff;">
            <div style="padding:8px 12px; border-bottom:1px solid #e2e8f0; color:#334155; font-weight:600;">STDOUT</div>
            <pre style="margin:0; padding:12px; white-space:pre-wrap; word-break:break-word; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; font-size:12px; line-height:1.5; max-height:420px; overflow:auto;">{esc_stdout or "(no stdout)"}</pre>
          </div>

          {""
           if not stderr else
           f'''
           <div style="border:1px solid #e2e8f0; border-radius:6px; background:#ffffff; margin-top:12px;">
             <div style="padding:8px 12px; border-bottom:1px solid #e2e8f0; color:#334155; font-weight:600;">
               STDERR {badge("truncated by executor") if trunc_err else ""}
             </div>
             <pre style="margin:0; padding:12px; white-space:pre-wrap; word-break:break-word; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace; font-size:12px; line-height:1.5; max-height:240px; overflow:auto;">{esc_stderr}</pre>
           </div>
           '''
          }
        </div>
        """
        return html_content