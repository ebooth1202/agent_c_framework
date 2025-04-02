import json
import xml.etree.ElementTree as ET

from typing import Optional, List
from agent_c_tools.tools.workspace.util.xml_to_yaml_converter import convert_dynamics_xml_to_yaml, extract_key_info_from_element

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

    async def extract_section(self, file_path: str, section_type: str, entity_name: Optional[str] = None,
                              output_path: Optional[str] = None, metadata_only: bool = False,
                              limit: int = 10, attributes_to_include: Optional[List[str]] = None,
                              format: str = "yaml") -> str:
        """
        Extract a specific section from the XML file for detailed analysis.

        Args:
            file_path: Path to the XML file relative to workspace root
            section_type: Type of section to extract (Entity, Form, Ribbon, SiteMap, etc.)
            entity_name: Optional entity name to filter by
            output_path: Optional path to save the extracted section
            metadata_only: Return only metadata about the sections found, not their content
            limit: Maximum number of sections to return
            attributes_to_include: List of specific attributes to include in metadata
            format: Output format ("yaml", "json", or "xml")

        Returns:
            String with the extracted section in the specified format
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                return json.dumps({'error': f'Invalid file path: {file_path}'})

            # Default attributes to include if not specified
            if attributes_to_include is None:
                if section_type == 'Entity':
                    attributes_to_include = ['Name', 'unmodified', 'description']
                elif section_type == 'Form':
                    attributes_to_include = ['id', 'name', 'type']
                elif section_type == 'SavedQuery':
                    attributes_to_include = ['name', 'returnedtypecode']
                else:
                    attributes_to_include = []

            # Use ElementTree's iterparse for memory-efficient parsing
            section_metadata = []
            section_texts = []
            count = 0

            # Get the appropriate XPath based on section type
            xpath = self._get_section_xpath(section_type, entity_name)

            # Use full parsing for extracting complete sections
            tree = ET.parse(full_path)
            root = tree.getroot()

            # Find matching sections
            elements = []

            if section_type == 'Entity':
                xpath = './/Entity'
                if entity_name:
                    xpath = f".//Entity[@Name='{entity_name}']"
            elif section_type == 'Form':
                xpath = './/form'
                # Entity filtering for forms is more complex, handle separately
            elif section_type == 'Ribbon':
                xpath = './/RibbonDiffXml'
            elif section_type == 'SiteMap':
                xpath = './/SiteMap'
            elif section_type == 'SavedQuery':
                xpath = './/SavedQuery'
            elif section_type == 'Workflow':
                xpath = './/Workflow'

            # Find elements matching the xpath
            elements = root.findall(xpath)

            # Apply entity filtering for forms if needed
            if section_type == 'Form' and entity_name:
                # This is a simplification; we need context to properly filter forms by entity
                # In a real implementation, we would need to trace back from form to entity
                filtered_elements = []
                for elem in elements:
                    # Check if this form belongs to the specified entity
                    # This is a heuristic - actual implementation would depend on XML structure
                    if entity_name.lower() in ET.tostring(elem, encoding='utf-8').decode('utf-8').lower():
                        filtered_elements.append(elem)
                elements = filtered_elements

            # Limit the results
            elements = elements[:limit]
            count = len(elements)

            # If no elements found
            if count == 0:
                return json.dumps({
                    'success': False,
                    'message': f'No {section_type} sections found' + (f' for entity {entity_name}' if entity_name else '')
                })

            # Process the elements
            for elem in elements:
                # Extract metadata
                metadata = {}
                for attr in attributes_to_include:
                    if attr in elem.attrib:
                        metadata[attr] = elem.attrib[attr]

                # Add additional information
                if section_type == 'Entity':
                    name_elem = elem.find('.//n')
                    if name_elem is not None and name_elem.text:
                        metadata['display_name'] = name_elem.text

                section_metadata.append(metadata)

                # Extract full section text if needed
                if not metadata_only:
                    section_text = ET.tostring(elem, encoding='utf-8').decode('utf-8')
                    section_texts.append(section_text)

            # Write to output file if specified
            if output_path and not metadata_only and section_texts:
                # Get the full output path
                full_output_path = self.workspace.full_path(output_path)
                if not full_output_path:
                    return json.dumps({'error': f'Invalid output path: {output_path}'})

                if format.lower() == 'xml':
                    # Create a basic XML wrapper
                    output_content = f'<?xml version="1.0" encoding="utf-8"?>\n<Sections>\n'
                    for section_text in section_texts:
                        output_content += section_text + '\n'
                    output_content += '</Sections>'
                elif format.lower() == 'yaml':
                    # Convert to YAML
                    output_content = ''
                    for i, section_text in enumerate(section_texts):
                        yaml_content = convert_dynamics_xml_to_yaml(
                            section_text,
                            section_type,
                            simplified=True
                        )
                        output_content += f"# Section {i + 1}\n{yaml_content}\n---\n"
                else:  # Default to JSON
                    sections_data = []
                    for i, section_text in enumerate(section_texts):
                        # Extract key info and convert to JSON
                        elem = elements[i]
                        section_data = extract_key_info_from_element(elem, section_type)
                        sections_data.append(section_data)
                    output_content = json.dumps(sections_data, indent=2)

                # Write to the output file
                with open(full_output_path, 'w', encoding='utf-8') as f:
                    f.write(output_content)

                return json.dumps({
                    'success': True,
                    'message': f'{count} {section_type} sections extracted to {output_path}',
                    'count': count,
                    'metadata': section_metadata
                })
            else:
                # Return data based on format preference
                if metadata_only:
                    return json.dumps({
                        'success': True,
                        'count': count,
                        'metadata': section_metadata
                    })
                else:
                    if format.lower() == 'yaml':
                        # Convert XML to YAML for response
                        yaml_sections = []
                        for i, section_text in enumerate(section_texts):
                            yaml_content = convert_dynamics_xml_to_yaml(
                                section_text,
                                section_type,
                                simplified=True
                            )
                            yaml_sections.append(yaml_content)

                        return json.dumps({
                            'success': True,
                            'count': count,
                            'metadata': section_metadata,
                            'format': 'yaml',
                            'sections': yaml_sections
                        })
                    elif format.lower() == 'json':
                        # Convert to structured JSON
                        json_sections = []
                        for i, elem in enumerate(elements):
                            section_data = extract_key_info_from_element(elem, section_type)
                            json_sections.append(section_data)

                        return json.dumps({
                            'success': True,
                            'count': count,
                            'metadata': section_metadata,
                            'format': 'json',
                            'sections': json_sections
                        })
                    else:
                        # Return raw XML
                        return json.dumps({
                            'success': True,
                            'count': count,
                            'metadata': section_metadata,
                            'format': 'xml',
                            'sections': section_texts
                        })
        except Exception as e:
            error_msg = f'Error extracting section: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})


    async def find_customizations(self, file_path: str) -> str:
        """
        Find customizations in a Dynamics customizations.xml file.

        Args:
            file_path: Path to the XML file relative to workspace root

        Returns:
            JSON string with customization information
        """
        try:
            # Get the full path to the file
            full_path = self.workspace.full_path(file_path, mkdirs=False)
            if not full_path:
                return json.dumps({'error': f'Invalid file path: {file_path}'})

            # Use iterative parsing to find customizations
            context = ET.iterparse(full_path, events=('start', 'end'))

            # Look for key customization indicators
            custom_entities = []
            modified_entities = []
            custom_attributes = []
            form_customizations = []
            ribbon_customizations = []
            sitemap_customizations = []
            saved_queries = []
            workflows = []

            # Track current element context
            current_entity = None
            in_form = False
            in_ribbon = False
            in_sitemap = False
            in_saved_query = False

            for event, elem in context:
                if event == 'start':
                    # Check for entity definitions
                    if elem.tag == 'Entity':
                        current_entity = elem.attrib.get('Name', 'Unknown')
                        # Check if this is a custom entity
                        if current_entity.startswith('new_') or elem.attrib.get('unmodified') == '0':
                            if current_entity.startswith('new_'):
                                custom_entities.append(current_entity)
                            else:
                                modified_entities.append(current_entity)

                    # Check for attribute definitions
                    elif elem.tag == 'Attribute' and current_entity:
                        attribute_name = elem.attrib.get('PhysicalName', '')
                        if attribute_name.startswith('new_') or elem.attrib.get('unmodified') == '0':
                            custom_attributes.append({
                                'entity': current_entity,
                                'attribute': attribute_name,
                                'is_custom': attribute_name.startswith('new_'),
                                'is_modified': elem.attrib.get('unmodified') == '0'
                            })

                    # Check for form definitions
                    elif elem.tag == 'form':
                        in_form = True
                        form_id = elem.attrib.get('id', 'Unknown')
                        form_name = elem.find('formid')
                        form_customizations.append({
                            'entity': current_entity,
                            'form_id': form_id,
                            'form_name': form_name.text if form_name is not None else 'Unknown'
                        })

                    # Check for ribbon customizations
                    elif elem.tag == 'RibbonDiffXml':
                        in_ribbon = True
                        ribbon_customizations.append({
                            'entity': current_entity,
                            'has_customizations': True
                        })

                    # Check for sitemap customizations
                    elif elem.tag == 'SiteMap':
                        in_sitemap = True
                        sitemap_customizations.append({
                            'has_customizations': True
                        })

                    # Check for saved queries
                    elif elem.tag == 'SavedQuery':
                        in_saved_query = True
                        query_name = elem.find('name')
                        saved_queries.append({
                            'entity': current_entity,
                            'query_name': query_name.text if query_name is not None else 'Unknown'
                        })

                    # Check for workflows
                    elif elem.tag == 'Workflow':
                        workflow_name = elem.find('Name')
                        workflows.append({
                            'name': workflow_name.text if workflow_name is not None else 'Unknown',
                            'is_custom': True
                        })

                elif event == 'end':
                    # Reset context flags
                    if elem.tag == 'Entity':
                        current_entity = None
                    elif elem.tag == 'form':
                        in_form = False
                    elif elem.tag == 'RibbonDiffXml':
                        in_ribbon = False
                    elif elem.tag == 'SiteMap':
                        in_sitemap = False
                    elif elem.tag == 'SavedQuery':
                        in_saved_query = False

                # Clear memory
                elem.clear()

            # Prepare results
            results = {
                'custom_entities': custom_entities,
                'modified_entities': modified_entities,
                'custom_attributes': custom_attributes,
                'form_customizations': form_customizations,
                'ribbon_customizations': ribbon_customizations,
                'sitemap_customizations': sitemap_customizations,
                'saved_queries': saved_queries,
                'workflows': workflows
            }

            return json.dumps({
                'success': True,
                'customizations': results,
                'summary': {
                    'custom_entities_count': len(custom_entities),
                    'modified_entities_count': len(modified_entities),
                    'custom_attributes_count': len(custom_attributes),
                    'form_customizations_count': len(form_customizations),
                    'ribbon_customizations_count': len(ribbon_customizations),
                    'sitemap_customizations_count': len(sitemap_customizations),
                    'saved_queries_count': len(saved_queries),
                    'workflows_count': len(workflows)
                }
            })

        except Exception as e:
            error_msg = f'Error finding customizations: {str(e)}'
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
