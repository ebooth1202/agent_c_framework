import xml.etree.ElementTree as ET
import json
from typing import Optional, List, Dict, Any, Union


class XMLNavigator:
    """A tool to navigate large XML files without loading the entire file into memory"""

    def __init__(self, workspace):
        self.workspace = workspace
        self.logger = workspace.logger

    async def get_structure(self, file_path: str, max_depth: int = 3, sample_count: int = 5) -> str:
        """
        Get a structural overview of the XML file without loading the entire content.

        Args:
            file_path: Path to the XML file relative to workspace root
            max_depth: Maximum depth to traverse in the XML structure
            sample_count: Number of sample elements to include at each level

        Returns:
            JSON string with structure information
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                return json.dumps({'error': f'Invalid file path: {file_path}'})

            # Create an iterative parser
            context = ET.iterparse(full_path, events=('start', 'end'))

            # Extract structure information
            structure = self._extract_structure(context, max_depth, sample_count)

            return json.dumps({
                'success': True,
                'structure': structure
            })

        except Exception as e:
            error_msg = f'Error processing XML file: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

    def _extract_structure(self, context, max_depth: int, sample_count: int) -> Dict:
        """Extract structural information from XML using iterative parsing"""
        root_info = {}
        path_stack = []
        current_depth = 0
        element_counts = {}
        samples = {}

        for event, elem in context:
            path = '/'.join([e.tag for e in path_stack]) + '/' + elem.tag if path_stack else elem.tag

            if event == 'start':
                # Track element path
                path_stack.append(elem)
                current_depth = len(path_stack)

                # Count elements at this path
                if path not in element_counts:
                    element_counts[path] = 0
                    samples[path] = []

                element_counts[path] += 1

                # Collect sample attributes if we haven't reached the limit
                if len(samples[path]) < sample_count:
                    if elem.attrib:
                        samples[path].append({
                            'attributes': dict(elem.attrib),
                            'text': elem.text.strip() if elem.text else None
                        })

                # Stop if we've reached max depth
                if current_depth > max_depth:
                    elem.clear()

            elif event == 'end':
                # Remove element from stack
                if path_stack:
                    path_stack.pop()

                # Clear memory
                elem.clear()

        # Construct the structure information
        structure = {
            'elements': element_counts,
            'samples': samples
        }

        return structure

    async def xpath_query(self, file_path: str, xpath: str, limit: int = 10) -> str:
        """
        Execute an XPath query on the XML file and return matching elements.

        Args:
            file_path: Path to the XML file relative to workspace root
            xpath: XPath query to execute
            limit: Maximum number of results to return

        Returns:
            JSON string with query results
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                return json.dumps({'error': f'Invalid file path: {file_path}'})

            # Parse the XML file
            tree = ET.parse(full_path)
            root = tree.getroot()

            # Find all elements matching the XPath
            matches = root.findall(xpath)

            # Limit results
            matches = matches[:limit]

            # Convert results to serializable format
            results = []
            for elem in matches:
                results.append({
                    'tag': elem.tag,
                    'attributes': dict(elem.attrib),
                    'text': elem.text.strip() if elem.text else None,
                    'children': [{'tag': child.tag, 'attributes': dict(child.attrib)} for child in elem]
                })

            return json.dumps({
                'success': True,
                'query': xpath,
                'count': len(matches),
                'results': results
            })

        except Exception as e:
            error_msg = f'Error executing XPath query: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

    async def extract_subtree(self, file_path: str, xpath: str, output_path: Optional[str] = None) -> str:
        """
        Extract a subtree from the XML file and optionally save it to a new file.

        Args:
            file_path: Path to the XML file relative to workspace root
            xpath: XPath to the root element of the subtree to extract
            output_path: Optional path to save the extracted subtree

        Returns:
            JSON string with the extracted subtree or status message
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                return json.dumps({'error': f'Invalid file path: {file_path}'})

            # Parse the XML file
            tree = ET.parse(full_path)
            root = tree.getroot()

            # Find the first element matching the XPath
            subtree_root = root.find(xpath)
            if subtree_root is None:
                return json.dumps({'error': f'No element matches XPath: {xpath}'})

            # Convert subtree to string representation
            subtree_str = ET.tostring(subtree_root, encoding='utf-8').decode('utf-8')

            # Write to output file if specified
            if output_path:
                # Get the full output path
                full_output_path = self.workspace.full_path(output_path)
                if not full_output_path:
                    return json.dumps({'error': f'Invalid output path: {output_path}'})

                # Create a new XML tree with the subtree as root
                subtree_tree = ET.ElementTree(subtree_root)

                # Write to the output file
                subtree_tree.write(full_output_path, encoding='utf-8', xml_declaration=True)

                return json.dumps({
                    'success': True,
                    'message': f'Subtree extracted to {output_path}',
                    'size': len(subtree_str)
                })
            else:
                # Return the subtree as string if no output path is specified
                return json.dumps({
                    'success': True,
                    'subtree': subtree_str
                })

        except Exception as e:
            error_msg = f'Error extracting subtree: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})