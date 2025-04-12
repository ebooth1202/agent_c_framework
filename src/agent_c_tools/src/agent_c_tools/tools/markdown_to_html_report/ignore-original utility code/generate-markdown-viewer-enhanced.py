#!/usr/bin/env python3

import os
import json
import re
from pathlib import Path

# Function to check if a file is a markdown file
def is_markdown_file(filename):
    return filename.lower().endswith('.md') or filename.lower().endswith('.markdown')

# Function to collect all markdown files in the directory structure
def collect_markdown_files(root_path):
    """
    Collect all markdown files in the directory structure.
    
    Args:
        root_path: Root directory to scan
    
    Returns:
        Dict mapping normalized paths to absolute paths for all markdown files
    """
    markdown_files = {}
    root_path = Path(root_path).resolve()
    
    for root, _, files in os.walk(root_path):
        for file in files:
            if is_markdown_file(file) and not file.startswith('.'):
                file_abs_path = Path(root) / file
                file_rel_path = file_abs_path.relative_to(root_path)
                normalized_path = str(file_rel_path).replace('\\', '/')
                markdown_files[normalized_path] = file_abs_path
    
    return markdown_files

# Function to process markdown links in content
def process_markdown_links(content, file_rel_path, root_path, markdown_files):
    """
    Convert markdown links to other markdown files into internal viewer links.
    
    Args:
        content: The markdown content to process
        file_rel_path: Relative path of the current file from root
        root_path: Root directory (absolute path)
        markdown_files: Dict mapping normalized paths to absolute paths for all markdown files
    
    Returns:
        Processed markdown content with updated links
    """
    # Get the directory of the current file for resolving relative paths
    file_dir = (root_path / file_rel_path).parent
    
    # Regular expression to find markdown links
    # Captures: [link text](path/to/file) - now handles both file and directory links
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    def replace_link(match):
        link_text = match.group(1)
        link_target = match.group(2)
        
        # Handle internal document links (just anchors)
        if link_target.startswith('#'):
            anchor_id = link_target.replace("#", "")
            return f'[{link_text}](javascript:void(scrollToAnchor("{anchor_id}")))'
            
        # Skip already processed javascript links
        if link_target.startswith('javascript:'):
            return match.group(0)
        
        # Skip external links
        if link_target.startswith(('http://', 'https://')):
            return match.group(0)
        
        # Skip already processed javascript links
        if link_target.startswith('javascript:'):
            return match.group(0)
        
        # Skip external links
        if link_target.startswith(('http://', 'https://')):
            return match.group(0)
            
        # Handle internal document links (just anchors)
        if link_target.startswith('#'):
            anchor_id = link_target.replace("#", "")
            return f'[{link_text}](javascript:void(scrollToAnchor("{anchor_id}")))'
            
        # Split target into file path and anchor if it exists
        parts = link_target.split('#', 1)
        target_file = parts[0]
        anchor = f"#{parts[1]}" if len(parts) > 1 else ""
        
        try:
            # Calculate the absolute path from the current file's directory
            if target_file.startswith('/'):
                # Handle absolute path (relative to root)
                target_abs_path = root_path / target_file[1:]
            else:
                # Handle relative path
                target_abs_path = (file_dir / target_file).resolve()
            
            # Get path relative to the root directory
            target_rel_path = target_abs_path.relative_to(root_path)
            target_path_str = str(target_rel_path).replace('\\', '/')
            
            # Check if the target is a markdown file in our collection
            if target_path_str in markdown_files:
                # Replace with internal link that uses void() to prevent return value display
                if anchor:
                    # If we have an anchor, pass it correctly to the openMarkdownFile function
                    return f'[{link_text}](javascript:void(openMarkdownFile("{target_path_str}", "{anchor}")))'
                else:
                    return f'[{link_text}](javascript:void(openMarkdownFile("{target_path_str}")))'
            
            # If it's potentially a directory link (ending with / or no extension)
            if target_path_str.endswith('/') or '.' not in target_path_str.split('/')[-1]:
                # Check if there are any markdown files in this directory
                for md_path in markdown_files.keys():
                    if md_path.startswith(target_path_str):
                        # It's a directory with markdown files, link to the first one
                        return f'[{link_text}](javascript:void(openMarkdownFile("{md_path}")))'
                        
                # If we didn't find any files in this directory, continue to warning
            
            # Debug info for missing files
            print(f"Warning: Link target '{target_path_str}' from file '{file_rel_path}' not found in markdown files.")
        except Exception as e:
            # If there's an error resolving the path, log it and leave the link unchanged
            print(f"Error processing link '{link_target}' in file '{file_rel_path}': {e}")
        
        # If target doesn't exist in our structure or path resolution failed, leave the link unchanged
        return match.group(0)
    
    # Process all links in the content
    processed_content = re.sub(link_pattern, replace_link, content)
    return processed_content

# Function to build file structure recursively
def build_file_structure(directory, root_path, markdown_files):
    """
    Build file structure for a directory recursively.
    
    Args:
        directory: Current directory to process
        root_path: Root directory (absolute path)
        markdown_files: Dict mapping normalized paths to absolute paths for all markdown files
    
    Returns:
        List of file structure objects for the directory
    """
    structure = []
    
    for item in sorted(directory.iterdir()):
        # Skip hidden files and directories
        if item.name.startswith('.'):
            continue
            
        # Skip the generated HTML file itself
        if item.name.lower() == 'markdown-viewer.html':
            continue
            
        item_rel_path = item.relative_to(root_path)
        item_path_str = str(item_rel_path).replace('\\', '/')
        
        if item.is_dir():
            # Process folder
            children = build_file_structure(item, root_path, markdown_files)
            # Only include folder if it contains markdown files (directly or in subdirectories)
            if children:
                structure.append({
                    'name': item.name,
                    'type': 'folder',
                    'path': item_path_str,
                    'children': children
                })
        elif is_markdown_file(item.name):
            # Process markdown file
            try:
                with open(item, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Process markdown links
                processed_content = process_markdown_links(
                    content, 
                    item_rel_path,
                    root_path,
                    markdown_files
                )
                
                structure.append({
                    'name': item.name,
                    'type': 'file',
                    'path': item_path_str,
                    'content': processed_content
                })
            except Exception as e:
                print(f"Error reading {item}: {e}")
                # Add with empty content
                structure.append({
                    'name': item.name,
                    'type': 'file',
                    'path': item_path_str,
                    'content': f"Error reading file: {str(e)}"
                })
    
    return structure

# Main function
def main():
    # Get the current directory
    current_dir = Path.cwd().resolve()
    print(f"Scanning directory: {current_dir}")
    
    # Collect all markdown files
    markdown_files = collect_markdown_files(current_dir)
    print(f"Found {len(markdown_files)} markdown files")
    
    # Build the file structure
    file_structure = build_file_structure(current_dir, current_dir, markdown_files)
    
    # If no markdown files were found
    if not file_structure:
        print("No markdown files found in the current directory or its subdirectories.")
        return
    
    # Read the template HTML file
    template_path = current_dir / "markdown-viewer-template-enhanced.html"
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            template = file.read()
    except FileNotFoundError:
        print(f"Template file not found: {template_path}")
        print("Make sure 'markdown-viewer-template-enhanced.html' is in the current directory.")
        return
    except Exception as e:
        print(f"Error reading template file: {e}")
        return
    
    # Replace placeholder with actual file structure
    json_structure = json.dumps(file_structure)
    html_content = template.replace('$FILE_STRUCTURE', json_structure)
    
    # Write the final HTML file
    output_path = current_dir / "markdown-viewer.html"
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"\nSuccess! Created markdown-viewer.html")
        print(f"Open this file in your browser to view your markdown files.")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()