import json
import yaml
from lxml import etree
import xml.etree.ElementTree as ET

from typing import Optional, List


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

    def _xml_to_dict(self, element):
        """
        Convert an XML element to a Python dictionary.

        Args:
            element: XML element to convert

        Returns:
            Dictionary representation of the XML element
        """
        result = {}

        # Add attributes if any
        if element.attrib:
            result['@attributes'] = dict(element.attrib)

        # Add text content if any (and not just whitespace)
        if element.text and element.text.strip():
            result['#text'] = element.text.strip()

        # Process child elements
        for child in element:
            child_dict = self._xml_to_dict(child)

            # Use tag name as key
            tag = child.tag

            # Handle multiple elements with the same tag
            if tag in result:
                # Convert to list if not already
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_dict)
            else:
                result[tag] = child_dict

        # If the element has no attributes and only text content, simplify
        if list(result.keys()) == ['#text']:
            return result['#text']

        # If the element is empty with no attributes, return empty dict
        if not result:
            return None

        return result


    async def xpath_query(self, file_path: str, xpath: str, limit: int = 10, format: str = "yaml") -> str:
        """
        Execute an XPath query on the XML file and return matching elements in JSON or YAML format.

        Args:
            file_path: Path to the XML file relative to workspace root
            xpath: XPath query to execute
            limit: Maximum number of results to return
            format: Output format for XML elements ("json" or "yaml"), defaults to "yaml"

        Returns:
            JSON string with query results
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                return json.dumps({'error': f'Invalid file path: {file_path}'})

            # Parse the XML file with lxml instead of ElementTree
            tree = etree.parse(full_path)
            root = tree.getroot()

            # Use xpath() method instead of findall() for full XPath support
            matches = root.xpath(xpath)

            # Limit results
            matches = matches[:limit]

            # Convert results to serializable format
            results = []
            for elem in matches:
                # Handle different node types
                if isinstance(elem, etree._Element):
                    if format.lower() == "yaml":
                        # For YAML, convert to hierarchical dict structure
                        result = self._xml_to_dict(elem)
                    else:
                        # For JSON, use flat structure with metadata
                        result = {
                            'tag': elem.tag,
                            'attributes': dict(elem.attrib),
                            'text': elem.text.strip() if elem.text else None,
                            'children': [{'tag': child.tag, 'attributes': dict(child.attrib)} for child in elem]
                        }
                elif isinstance(elem, str):
                    # For text nodes or attribute values
                    result = {'value': elem}
                else:
                    # For other types (like numbers from count() functions)
                    result = {'value': str(elem)}

                results.append(result)

            response = {
                'success': True,
                'query': xpath,
                'count': len(matches),
                'format': format.lower()
            }

            # If output format is YAML, convert results to YAML string
            if format.lower() == "yaml":
                response['results_yaml'] = yaml.dump(results, default_flow_style=False, sort_keys=False)
            else:
                response['results'] = results

            return json.dumps(response)

        except Exception as e:
            error_msg = f'Error executing XPath query: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

    async def extract_subtree(self, file_path: str, xpath: str, output_path: Optional[str] = None, format: str = "yaml") -> str:
        """
        Extract a subtree from the XML file, convert to YAML (or keep as XML), and optionally save it to a new file.

        Args:
            file_path: Path to the XML file relative to workspace root
            xpath: XPath to the root element of the subtree to extract
            output_path: Optional path to save the extracted subtree
            format: Output format ("yaml" or "xml"), defaults to "yaml"

        Returns:
            JSON string with the extracted subtree in specified format or status message
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                return json.dumps({'error': f'Invalid file path: {file_path}'})

            # Parse the XML file with lxml
            tree = etree.parse(full_path)
            root = tree.getroot()

            # Find the first element matching the XPath using xpath() method
            subtree_elements = root.xpath(xpath)

            if not subtree_elements:
                return json.dumps({'error': f'No element matches XPath: {xpath}'})

            # Get the first matching element
            subtree_root = subtree_elements[0]

            # Check if we got a proper element (not a string or number)
            if not isinstance(subtree_root, etree._Element):
                return json.dumps({'error': f'XPath result is not an element: {type(subtree_root)}'})

            if format.lower() == "xml":
                # Keep as XML
                result_str = etree.tostring(subtree_root, encoding='utf-8', xml_declaration=False, pretty_print=True).decode('utf-8')
                result_format = "xml"
            else:
                # Convert XML to Python dict
                xml_dict = self._xml_to_dict(subtree_root)

                # Convert dict to YAML
                result_str = yaml.dump(xml_dict, default_flow_style=False, sort_keys=False)
                result_format = "yaml"

            # Write to output file if specified
            if output_path:
                # Get the full output path
                full_output_path = self.workspace.full_path(output_path)
                if not full_output_path:
                    return json.dumps({'error': f'Invalid output path: {output_path}'})

                # Change file extension based on format if it's .xml
                if full_output_path.endswith('.xml') and result_format == "yaml":
                    full_output_path = full_output_path[:-4] + '.yaml'

                # Write to the output file
                with open(full_output_path, 'w', encoding='utf-8') as f:
                    f.write(result_str)

                return json.dumps({
                    'success': True,
                    'message': f'Subtree extracted to {full_output_path} as {result_format.upper()}',
                    'size': len(result_str)
                })
            else:
                # Return the subtree in the specified format if no output path is specified
                return json.dumps({
                    'success': True,
                    'format': result_format,
                    'subtree': result_str
                })

        except Exception as e:
            error_msg = f'Error extracting subtree: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

    def _extract_structure(self, context, max_depth: int, sample_count: int) -> dict:
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

    def _get_section_xpath(self, section_type: str, entity_name: Optional[str] = None) -> str:
        """Helper method to construct appropriate XPath query based on section type and filters"""
        if section_type == 'Entity':
            if entity_name:
                return f"./Entity[@Name='{entity_name}']"
            else:
                return "./Entity"
        elif section_type == 'Form':
            if entity_name:
                # This is a simplification; actual path might be different
                return f"./Entity[@Name='{entity_name}']//form"
            else:
                return ".//form"
        elif section_type == 'Ribbon':
            if entity_name:
                return f"./Entity[@Name='{entity_name}']//RibbonDiffXml"
            else:
                return ".//RibbonDiffXml"
        elif section_type == 'SiteMap':
            return ".//SiteMap"
        elif section_type == 'SavedQuery':
            if entity_name:
                return f"./Entity[@Name='{entity_name}']//SavedQuery"
            else:
                return ".//SavedQuery"
        elif section_type == 'Workflow':
            return ".//Workflow"
        else:
            # Default case
            return f".//{section_type}"