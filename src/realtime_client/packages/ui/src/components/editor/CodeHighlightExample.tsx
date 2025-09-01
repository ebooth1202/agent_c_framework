/**
 * Example usage of the MarkdownEditor with code syntax highlighting
 * 
 * This demonstrates how to use the editor with code blocks that have
 * syntax highlighting for various programming languages.
 */

import * as React from 'react';
import { MarkdownEditor } from './MarkdownEditor';

const exampleContent = `# Code Syntax Highlighting Example

The editor now supports syntax highlighting for code blocks!

## JavaScript Example

\`\`\`javascript
// Function to calculate factorial
function factorial(n) {
  if (n === 0 || n === 1) {
    return 1;
  }
  return n * factorial(n - 1);
}

console.log(factorial(5)); // Output: 120
\`\`\`

## TypeScript Example

\`\`\`typescript
interface User {
  id: number;
  name: string;
  email: string;
  isActive: boolean;
}

class UserService {
  private users: User[] = [];

  addUser(user: User): void {
    this.users.push(user);
  }

  getActiveUsers(): User[] {
    return this.users.filter(user => user.isActive);
  }
}
\`\`\`

## Python Example

\`\`\`python
def quick_sort(arr):
    """Quick sort implementation in Python"""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

# Example usage
numbers = [3, 6, 8, 10, 1, 2, 1]
print(quick_sort(numbers))
\`\`\`

## JSON Example

\`\`\`json
{
  "name": "@agentc/realtime-ui",
  "version": "0.1.0",
  "dependencies": {
    "@tiptap/core": "^2.10.3",
    "@tiptap/extension-code-block-lowlight": "^2.10.3",
    "highlight.js": "^11.11.1",
    "lowlight": "^3.3.0"
  }
}
\`\`\`

## HTML/CSS Example

\`\`\`html
<!DOCTYPE html>
<html lang="en">
<head>
  <style>
    .highlight {
      background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 1rem;
      border-radius: 0.5rem;
    }
  </style>
</head>
<body>
  <div class="highlight">
    <h1>Hello, World!</h1>
    <p>This is a syntax highlighted HTML example.</p>
  </div>
</body>
</html>
\`\`\`

## Bash/Shell Example

\`\`\`bash
#!/bin/bash

# Script to backup files
SOURCE_DIR="/home/user/documents"
BACKUP_DIR="/backup/documents"
DATE=$(date +%Y%m%d)

# Create backup
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" "$SOURCE_DIR"

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully"
else
    echo "Backup failed"
    exit 1
fi
\`\`\`

## How to Use

1. Type triple backticks followed by the language name: \`\`\`javascript
2. Write your code
3. Close with triple backticks: \`\`\`

Supported languages include:
- JavaScript/TypeScript (\`js\`, \`javascript\`, \`ts\`, \`typescript\`)
- Python (\`python\`, \`py\`)
- JSON (\`json\`)
- HTML/XML (\`html\`, \`xml\`)
- CSS (\`css\`)
- Markdown (\`markdown\`, \`md\`)
- Bash/Shell (\`bash\`, \`sh\`, \`shell\`)
- YAML (\`yaml\`, \`yml\`)
- SQL (\`sql\`)
- Dockerfile (\`dockerfile\`, \`docker\`)
`;

export const CodeHighlightExample: React.FC = () => {
  const [content, setContent] = React.useState(exampleContent);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">Code Syntax Highlighting Demo</h1>
      <p className="text-muted-foreground mb-6">
        The MarkdownEditor now supports syntax highlighting for code blocks.
        Try editing the content below or adding your own code blocks!
      </p>
      
      <MarkdownEditor
        value={content}
        onChange={setContent}
        placeholder="Start typing... Use ```language to create code blocks"
        className="min-h-[500px]"
      />
      
      <div className="mt-6 p-4 bg-muted rounded-md">
        <h2 className="text-lg font-semibold mb-2">Raw Text Output:</h2>
        <pre className="text-xs whitespace-pre-wrap break-words">
          {content.slice(0, 500)}...
        </pre>
      </div>
    </div>
  );
};