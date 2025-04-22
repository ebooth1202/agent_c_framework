import re
from typing import Dict, List, Optional, Tuple, Any


class CssNavigator:
    """A tool to navigate and manipulate large CSS files efficiently"""

    def __init__(self, workspace):
        self.workspace = workspace
        self.logger = workspace.logger

    async def scan_css_file(self, file_path: str) -> str:
        """
        Scans a CSS file and builds a Markdown overview of component sections.

        Args:
            file_path: Path to the CSS file relative to workspace root

        Returns:
            Markdown string with CSS structure information
        """
        try:
            # Read the file content using workspace
            content_str = await self.workspace.read_internal(file_path)
            content = content_str.splitlines(True)  # Keep line endings

            # Count total lines and characters
            total_lines = len(content)
            total_chars = sum(len(line) for line in content)

            # Extract component sections
            components = self._extract_components_with_lines(content)

            # Format the result as markdown
            result = f"# CSS Explorer: {file_path}\n\n"
            result += f"- File size: {total_lines} lines, {total_chars} characters\n"
            result += f"- Components found: {len(components)}\n\n"

            # Add component overview
            result += "## Component Sections:\n\n"
            for component in components:
                name = component['name']
                start = component['start_line']
                end = component['end_line']
                styles_count = len(component['styles'])
                result += f"- **{name}** (lines {start}-{end}): {styles_count} styles\n"

            return result

        except Exception as e:
            error_msg = f"Error processing CSS file: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def get_component_styles(self, file_path: str, component_name: str) -> str:
        """
        Gets styles for a specific component from a CSS file in Markdown format.

        Args:
            file_path: Path to the CSS file relative to workspace root
            component_name: Name of the component to extract styles for

        Returns:
            Markdown string with component styles information
        """
        try:
            # Read the file content using workspace
            content_str = await self.workspace.read_internal(file_path)
            content = content_str.splitlines(True)  # Keep line endings

            # Extract component information
            components = self._extract_components_with_lines(content)

            # Find the requested component
            component = next((c for c in components if c['name'].lower() == component_name.lower()), None)
            if not component:
                available = ", ".join([c['name'] for c in components])
                return f"Error: Component not found: {component_name}\n\nAvailable components: {available}"

            # Format component overview
            result = f"# Component: {component['name']}\n\n"
            result += f"- Location: lines {component['start_line']}-{component['end_line']}\n"
            result += f"- Styles: {len(component['styles'])}\n\n"

            # Add all styles
            result += "## Styles:\n\n"
            for style in component['styles']:
                selector = style['selector']
                description = style['description']
                start = style['start_line']
                end = style['end_line']
                content = style['content']

                result += f"### {selector}\n"
                if description:
                    result += f"*{description}*\n\n"
                result += f"Lines: {start}-{end}\n\n"
                result += "```css\n"
                result += content + "\n"
                result += "```\n\n"

            return result

        except Exception as e:
            error_msg = f"Error retrieving component styles: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    async def update_style(self, file_path: str, component_name: str, 
                         class_name: str, new_style: str) -> str:
        """
        Updates a specific CSS class within a component section.

        Args:
            file_path: Path to the CSS file relative to workspace root
            component_name: Name of the component containing the style
            class_name: Name of the CSS class to update
            new_style: New style definition (including the class selector and braces)

        Returns:
            Markdown string with update status
        """
        try:
            # Read the file content using workspace
            content_str = await self.workspace.read_internal(file_path)
            content = content_str.splitlines(True)  # Keep line endings

            # Extract component information
            components = self._extract_components_with_lines(content)

            # Find the requested component
            component = next((c for c in components if c['name'].lower() == component_name.lower()), None)
            if not component:
                available = ", ".join([c['name'] for c in components])
                return f"Error: Component not found: {component_name}\n\nAvailable components: {available}"

            # Find the requested style within the component
            style = next((s for s in component['styles'] if s['selector'].strip() == class_name.strip()), None)
            if not style:
                available = ", ".join([s['selector'] for s in component['styles']])
                return f"Error: Style not found: {class_name}\n\nAvailable styles: {available}"

            # Replace the style in the content
            start_line = style['start_line']
            end_line = style['end_line']
            
            # Create the new content
            new_content = content[:start_line]
            new_content.extend(new_style.splitlines(True))  # Keep line endings
            new_content.extend(content[end_line + 1:])

            # Write the updated content back to the file using workspace
            new_content_str = ''.join(new_content)
            await self.workspace.write(file_path, new_content_str, 'write')

            return f"# Style Update Successful\n\n" + \
                   f"- Component: **{component_name}**\n" + \
                   f"- Selector: **{class_name}**\n" + \
                   f"- Lines updated: {start_line}-{end_line}\n\n" + \
                   f"```css\n{new_style}\n```"

        except Exception as e:
            error_msg = f"Error updating style: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def get_component_source(self, file_path: str, component_name: str) -> str:
        """
        Gets raw CSS source for a specific component, including its header comment and all styles.

        Args:
            file_path: Path to the CSS file relative to workspace root
            component_name: Name of the component to extract source for

        Returns:
            Raw CSS source code for the component
        """
        try:
            # Read the file content using workspace
            content_str = await self.workspace.read_internal(file_path)
            content = content_str.splitlines(True)  # Keep line endings

            # Extract component information
            components = self._extract_components_with_lines(content)

            # Find the requested component
            component = next((c for c in components if c['name'].lower() == component_name.lower()), None)
            if not component:
                available = ", ".join([c['name'] for c in components])
                return f"Error: Component not found: {component_name}\n\nAvailable components: {available}"

            # Extract the component source
            start_line = component['start_line']
            end_line = component['end_line']
            component_source = ''.join(content[start_line:end_line + 1])
            
            return component_source

        except Exception as e:
            error_msg = f"Error retrieving component source: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    async def get_style_source(self, file_path: str, component_name: str, class_name: str) -> str:
        """
        Gets raw CSS source for a specific style within a component, including its preceding comment.

        Args:
            file_path: Path to the CSS file relative to workspace root
            component_name: Name of the component containing the style
            class_name: Name of the CSS class to get source for

        Returns:
            Raw CSS source code for the style including its comment
        """
        try:
            # Read the file content using workspace
            content_str = await self.workspace.read_internal(file_path)
            content = content_str.splitlines(True)  # Keep line endings

            # Extract component information
            components = self._extract_components_with_lines(content)

            # Find the requested component
            component = next((c for c in components if c['name'].lower() == component_name.lower()), None)
            if not component:
                available = ", ".join([c['name'] for c in components])
                return f"Error: Component not found: {component_name}\n\nAvailable components: {available}"

            # Find the requested style within the component
            style = next((s for s in component['styles'] if s['selector'].strip() == class_name.strip()), None)
            if not style:
                available = ", ".join([s['selector'] for s in component['styles']])
                return f"Error: Style not found: {class_name}\n\nAvailable styles: {available}"

            # Get style source lines
            start_line = style['start_line']
            end_line = style['end_line']
            
            # Get the comment section before the style
            # Look for /* pattern before the start line to find the comment start
            comment_start = start_line
            for i in range(start_line - 1, max(0, start_line - 10), -1):  # Look up to 10 lines back
                if "/*" in content[i]:
                    comment_start = i
                    break
            
            style_source = ''.join(content[comment_start:end_line + 1])
            return style_source

        except Exception as e:
            error_msg = f"Error retrieving style source: {str(e)}"
            self.logger.error(error_msg)
            return error_msg

    def _extract_components_with_lines(self, content_lines: List[str]) -> List[Dict[str, Any]]:
        """
        Extracts component sections from CSS content with line numbers.

        Args:
            content_lines: CSS file content as a list of lines

        Returns:
            List of component dictionaries with names, line numbers, and styles
        """
        components = []
        content = ''.join(content_lines)

        component_pattern = r"COMPONENT:\s*(?P<comp_name1>[A-Za-z0-9_-]+)[\s\S]*?\*\/|\*\s*={2,}\s*(?P<comp_name2>[^=\n]+)\s*Component\s*Styles\s*={2,}\s*\*/"
        for match in re.finditer(component_pattern, content, re.IGNORECASE):
            component_name = (match.group('comp_name1') or match.group('comp_name2')).strip()

            # Find the line number for this component header by calculating the position
            match_start_pos = match.start() - 1
            content_before_match = content[:match_start_pos]
            start_line = content_before_match.count('\n')

            # Find the next component or the end of the file
            next_component_match = None
            for next_match in re.finditer(component_pattern, content, re.IGNORECASE):
                if next_match.start() > match.end():
                    next_component_match = next_match
                    break

            # Get the end line for this component
            if next_component_match:
                next_match_start_pos = next_component_match.start()
                content_before_next_match = content[:next_match_start_pos]
                end_line = content_before_next_match.count('\n') - 1
            else:
                end_line = len(content_lines) - 1

            # Extract styles within this component
            component_content = ''.join(content_lines[start_line:end_line + 1])
            styles = self._extract_styles(content_lines, start_line, end_line)

            components.append({
                'name': component_name,
                'start_line': start_line,
                'end_line': end_line,
                'styles': styles
            })

        return components

    def _extract_styles(self, content_lines: List[str], start_line: int, end_line: int) -> List[Dict[str, Any]]:
        """
        Extracts individual CSS styles from a component section.
        
        Args:
            content_lines: CSS file content as a list of lines
            start_line: Starting line number of the component section
            end_line: Ending line number of the component section
            
        Returns:
            List of style dictionaries with selectors, descriptions, and line numbers
        """
        styles = []
        component_content = ''.join(content_lines[start_line:end_line + 1])
        
        # Pattern to find CSS style blocks with comments
        style_pattern = r"/\*([^*]*)\*/\s*([\s\S]*?\{[\s\S]*?\})"
        
        # Track the current line number relative to the component start
        current_line = start_line
        
        # Find all style blocks with their preceding comments
        for match in re.finditer(style_pattern, component_content):
            description = match.group(1).strip() if match.group(1) else ""
            style_block = match.group(2).strip()
            
            # Get the selector from the style block
            selector_match = re.match(r"([^{]+)\{", style_block)
            selector = selector_match.group(1).strip() if selector_match else ""
            
            # Find the line numbers for this style block
            match_text = match.group(0)
            relative_start = component_content.find(match_text)
            preceding_content = component_content[:relative_start]
            line_offset = preceding_content.count('\n')
            
            style_start_line = start_line + line_offset
            style_end_line = style_start_line + match_text.count('\n')
            
            styles.append({
                'selector': selector,
                'description': description,
                'start_line': style_start_line,
                'end_line': style_end_line,
                'content': style_block
            })
            
        return styles