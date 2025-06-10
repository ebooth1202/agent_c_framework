import re
import logging
from typing import List, Tuple, Dict

logger = logging.getLogger(__name__)


class MarkdownJavaScriptSafetyValidator:
    """Validates markdown content for potential JavaScript template literal conflicts."""

    def __init__(self):
        # Patterns that could cause issues in JavaScript template literals
        self.risky_patterns = [
            (r'\$\{[^}]*\}', 'Template literal expressions (${...})'),
            (r'`[^`]*`', 'Backtick strings'),
            (r'\$"[^"]*"', 'C# interpolated strings'),
            (r'`[^`]*\$\{[^}]*\}[^`]*`', 'Template literals with expressions'),
            (r'</script>', 'Script tag closures'),
            (r'javascript:', 'JavaScript protocol'),
        ]

    def validate_content(self, content: str, filename: str = "unknown") -> Dict:
        """Validate markdown content for JavaScript safety issues.

        Args:
            content: The markdown content to validate
            filename: Optional filename for context

        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        line_number = 1
        in_code_block = False
        code_block_language = None

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Track code block boundaries
            code_fence_match = re.match(r'^```(\w+)?', line.strip())
            if code_fence_match:
                if not in_code_block:
                    in_code_block = True
                    code_block_language = code_fence_match.group(1) or 'unknown'
                else:
                    in_code_block = False
                    code_block_language = None
                continue

            # Check for risky patterns
            if in_code_block:
                for pattern, description in self.risky_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        severity = self._assess_severity(match.group(), code_block_language)
                        issue = {
                            'line': line_num,
                            'column': match.start() + 1,
                            'pattern': match.group(),
                            'description': description,
                            'severity': severity,
                            'context': line.strip(),
                            'language': code_block_language,
                            'suggestion': self._get_suggestion(match.group(), code_block_language)
                        }

                        if severity == 'error':
                            issues.append(issue)
                        else:
                            warnings.append(issue)

        return {
            'filename': filename,
            'is_safe': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'summary': self._create_summary(issues, warnings)
        }

    def _assess_severity(self, pattern: str, language: str) -> str:
        """Assess the severity of a risky pattern."""
        # C# interpolated strings in C# code are high risk
        if re.match(r'\$"[^"]*"', pattern) and language in ['csharp', 'cs', 'c#']:
            return 'error'

        # Template literal expressions are always high risk
        if re.match(r'\$\{[^}]*\}', pattern):
            return 'error'

        # JavaScript protocol is high risk
        if 'javascript:' in pattern.lower():
            return 'error'

        # Script closures are high risk
        if '</script>' in pattern.lower():
            return 'error'

        # Everything else is warning
        return 'warning'

    def _get_suggestion(self, pattern: str, language: str) -> str:
        """Get a suggestion for fixing the issue."""
        if re.match(r'\$\{[^}]*\}', pattern):
            return "Consider using HTML entity encoding: &#36;&#123;...&#125;"

        if re.match(r'\$"[^"]*"', pattern) and language in ['csharp', 'cs', 'c#']:
            return "C# interpolated strings may conflict with JS template literals"

        if '`' in pattern:
            return "Consider using HTML entity &#96; for backticks"

        if 'javascript:' in pattern.lower():
            return "Avoid javascript: protocol in links"

        return "Consider escaping special characters"

    def _create_summary(self, issues: List, warnings: List) -> str:
        """Create a summary of validation results."""
        if not issues and not warnings:
            return "✅ Content is safe for JavaScript template processing"

        summary_parts = []

        if issues:
            summary_parts.append(f"🚨 {len(issues)} critical issues found")

        if warnings:
            summary_parts.append(f"⚠️ {len(warnings)} warnings found")

        return " | ".join(summary_parts)

    def validate_file(self, file_path: str) -> Dict:
        """Validate a markdown file for JavaScript safety."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.validate_content(content, file_path)
        except Exception as e:
            return {
                'filename': file_path,
                'is_safe': False,
                'issues': [{'error': f"Failed to read file: {e}"}],
                'warnings': [],
                'summary': f"❌ File read error: {e}"
            }

    def generate_report(self, validation_result: Dict) -> str:
        """Generate a detailed validation report."""
        result = validation_result
        report_lines = [
            f"# Markdown JavaScript Safety Report",
            f"**File**: {result['filename']}",
            f"**Status**: {'✅ SAFE' if result['is_safe'] else '🚨 UNSAFE'}",
            f"**Summary**: {result['summary']}",
            ""
        ]

        if result['issues']:
            report_lines.extend([
                "## 🚨 Critical Issues",
                ""
            ])

            for issue in result['issues']:
                report_lines.extend([
                    f"### Line {issue['line']}, Column {issue['column']}",
                    f"**Pattern**: `{issue['pattern']}`",
                    f"**Language**: {issue['language']}",
                    f"**Description**: {issue['description']}",
                    f"**Context**: `{issue['context']}`",
                    f"**Suggestion**: {issue['suggestion']}",
                    ""
                ])

        if result['warnings']:
            report_lines.extend([
                "## ⚠️ Warnings",
                ""
            ])

            for warning in result['warnings']:
                report_lines.extend([
                    f"### Line {warning['line']}, Column {warning['column']}",
                    f"**Pattern**: `{warning['pattern']}`",
                    f"**Language**: {warning['language']}",
                    f"**Description**: {warning['description']}",
                    f"**Context**: `{warning['context']}`",
                    f"**Suggestion**: {warning['suggestion']}",
                    ""
                ])

        if result['is_safe']:
            report_lines.extend([
                "## ✅ All Clear",
                "This markdown file is safe for JavaScript template literal processing.",
                ""
            ])

        return "\n".join(report_lines)


# Example usage
def main():
    validator = MarkdownJavaScriptSafetyValidator()

    # Example problematic content
    test_content = """
# Test Document

```csharp
public class Example 
{
    private readonly string template = $"Hello {name}!";
    var query = $"SELECT * FROM Users WHERE Id = {userId}";
}
```

```javascript
const template = `Hello ${name}!`;
```

Some inline `code with backticks` here.
"""

    result = validator.validate_content(test_content, "test.md")
    report = validator.generate_report(result)
    print(report)


if __name__ == "__main__":
    main()