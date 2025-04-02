import xml.etree.ElementTree as ET
import yaml
import json
from typing import Optional, List, Dict, Any, Union

def xml_element_to_dict(element, include_text=True, max_depth=10, current_depth=0):
    """Convert an XML element to a dictionary suitable for YAML conversion"""
    if current_depth >= max_depth:
        return {"warning": "Max depth reached, content truncated"}
    
    result = {}
    
    # Add attributes
    if element.attrib:
        result["@attributes"] = dict(element.attrib)
    
    # Add text content if it exists and is meaningful
    if include_text and element.text and element.text.strip():
        result["#text"] = element.text.strip()
    
    # Process child elements
    for child in element:
        child_dict = xml_element_to_dict(
            child, 
            include_text=include_text, 
            max_depth=max_depth, 
            current_depth=current_depth + 1
        )
        
        # Handle multiple children with the same tag
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_dict)
        else:
            result[child.tag] = child_dict
    
    return result

def convert_xml_to_yaml(xml_string, include_text=True, max_depth=5):
    """Convert XML string to YAML string"""
    try:
        root = ET.fromstring(xml_string)
        data = {root.tag: xml_element_to_dict(root, include_text, max_depth)}
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    except Exception as e:
        return f"Error converting XML to YAML: {str(e)}"

def extract_key_info_from_element(element, element_type):
    """Extract only the most relevant information from an XML element based on its type"""
    result = {}
    
    # Common attributes to extract
    if element.attrib:
        result["attributes"] = dict(element.attrib)
    
    # Type-specific extraction
    if element_type == "Entity":
        # Get name
        name_elem = element.find(".//n")
        if name_elem is not None and name_elem.text:
            result["name"] = name_elem.text
        elif "Name" in element.attrib:
            result["name"] = element.attrib["Name"]
            
        # Get description
        desc_elem = element.find(".//Description")
        if desc_elem is not None:
            label_elem = desc_elem.find(".//Label")
            if label_elem is not None and "description" in label_elem.attrib:
                result["description"] = label_elem.attrib["description"]
        
        # Get attributes (fields) summary
        attributes = element.findall(".//Attribute")
        if attributes:
            result["attributes_count"] = len(attributes)
            result["custom_attributes"] = [
                attr.find(".//n").text if attr.find(".//n") is not None else attr.attrib.get("PhysicalName", "Unknown")
                for attr in attributes
                if attr.find(".//IsCustomAttribute") is not None and attr.find(".//IsCustomAttribute").text == "1"
            ][:10]  # Limit to first 10 to keep response size reasonable
            
    elif element_type == "Form":
        # Get form name
        name_elem = element.find(".//n")
        if name_elem is not None and name_elem.text:
            result["name"] = name_elem.text
            
        # Get form type
        type_elem = element.find(".//type")
        if type_elem is not None and type_elem.text:
            result["form_type"] = type_elem.text
            
        # Count sections and fields
        tabs = element.findall(".//tab")
        sections = element.findall(".//section")
        controls = element.findall(".//control")
        
        result["structure"] = {
            "tabs_count": len(tabs),
            "sections_count": len(sections),
            "controls_count": len(controls)
        }
        
    elif element_type == "SavedQuery":
        # Get query name
        name_elem = element.find(".//n")
        if name_elem is not None and name_elem.text:
            result["name"] = name_elem.text
            
        # Get query type
        type_elem = element.find(".//QueryType")
        if type_elem is not None and type_elem.text:
            result["query_type"] = type_elem.text
            
        # Get fetch XML summary if it exists
        fetch_elem = element.find(".//FetchXml")
        if fetch_elem is not None and fetch_elem.text:
            result["has_fetch_xml"] = True
            
            # Try to extract entity name from FetchXML
            try:
                fetch_root = ET.fromstring(fetch_elem.text)
                entity_elem = fetch_root.find(".//entity")
                if entity_elem is not None:
                    result["entity_name"] = entity_elem.attrib.get("name")
                    
                # Get attribute count
                attrs = fetch_root.findall(".//attribute")
                result["attribute_count"] = len(attrs)
                
                # Check for filters
                filters = fetch_root.findall(".//filter")
                if filters:
                    result["has_filters"] = True
                    result["filter_count"] = len(filters)
                
                # Check for links to other entities
                links = fetch_root.findall(".//link-entity")
                if links:
                    result["has_link_entities"] = True
                    result["link_count"] = len(links)
                    result["linked_entities"] = [link.attrib.get("name") for link in links if "name" in link.attrib]
            except:
                # If we can't parse the FetchXML, just indicate it exists
                result["fetch_xml_parse_error"] = True
    
    elif element_type == "RibbonDiffXml":
        # For ribbon customizations, get counts of different elements
        custom_actions = element.findall(".//CustomAction")
        result["custom_actions_count"] = len(custom_actions)
        
        command_defs = element.findall(".//CommandDefinition")
        result["command_definitions_count"] = len(command_defs)
        
        # Look for JavaScript references
        js_functions = element.findall(".//JavaScriptFunction")
        result["javascript_functions_count"] = len(js_functions)
        
        if js_functions:
            # Extract JavaScript libraries referenced
            libraries = set()
            for js in js_functions:
                if "Library" in js.attrib:
                    lib = js.attrib["Library"]
                    if lib.startswith("$webresource:"):
                        lib = lib.replace("$webresource:", "")
                    libraries.add(lib)
            
            if libraries:
                result["javascript_libraries"] = list(libraries)
    
    elif element_type == "SiteMap":
        # For site maps, summarize the structure
        areas = element.findall(".//Area")
        result["areas_count"] = len(areas)
        
        area_names = []
        for area in areas:
            title_elem = area.find(".//Title")
            if title_elem is not None and "Title" in title_elem.attrib:
                area_names.append(title_elem.attrib["Title"])
            elif "Id" in area.attrib:
                area_names.append(area.attrib["Id"])
        
        if area_names:
            result["areas"] = area_names
            
        # Count groups and subareas
        groups = element.findall(".//Group")
        result["groups_count"] = len(groups)
        
        subareas = element.findall(".//SubArea")
        result["subareas_count"] = len(subareas)
        
        # Find entity references
        entity_refs = []
        for subarea in subareas:
            if "Entity" in subarea.attrib:
                entity_refs.append(subarea.attrib["Entity"])
        
        if entity_refs:
            result["referenced_entities"] = entity_refs
    
    elif element_type == "Workflow":
        # For workflows, get basic information
        name_elem = element.find(".//n")
        if name_elem is not None and name_elem.text:
            result["name"] = name_elem.text
            
        # Get primary entity
        entity_elem = element.find(".//PrimaryEntity")
        if entity_elem is not None and entity_elem.text:
            result["primary_entity"] = entity_elem.text
            
        # Get trigger conditions
        if element.find(".//TriggerOnCreate") is not None:
            result["triggers_on_create"] = element.find(".//TriggerOnCreate").text == "1"
            
        if element.find(".//TriggerOnDelete") is not None:
            result["triggers_on_delete"] = element.find(".//TriggerOnDelete").text == "1"
            
        if element.find(".//TriggerOnUpdate") is not None:
            result["triggers_on_update"] = element.find(".//TriggerOnUpdate").text == "1"
            
        # Check if it's a custom process
        if element.find(".//IsCustomProcess") is not None:
            result["is_custom_process"] = element.find(".//IsCustomProcess").text == "1"
            
        # XAML file reference
        xaml_elem = element.find(".//XamlFileName")
        if xaml_elem is not None and xaml_elem.text:
            result["xaml_file"] = xaml_elem.text
    
    return result

def convert_dynamics_xml_to_yaml(xml_string, element_type, simplified=True, max_elements=10):
    """
    Convert Dynamics XML to YAML with special handling for known element types
    
    Args:
        xml_string: XML content as string
        element_type: Type of element ('Entity', 'Form', etc.)
        simplified: Whether to extract only key information instead of converting entire structure
        max_elements: Maximum number of elements to process
        
    Returns:
        YAML representation of the XML content
    """
    try:
        root = ET.fromstring(xml_string)
        
        # For single element processing
        if root.tag == element_type:
            if simplified:
                result = extract_key_info_from_element(root, element_type)
                return yaml.dump(result, default_flow_style=False, sort_keys=False)
            else:
                data = {root.tag: xml_element_to_dict(root, include_text=True, max_depth=5)}
                return yaml.dump(data, default_flow_style=False, sort_keys=False)
        
        # For processing multiple elements (e.g. from a sections wrapper)
        elements = root.findall(f".//{element_type}")
        if not elements:
            return yaml.dump({"error": f"No {element_type} elements found"})
        
        # Limit number of elements to process
        elements = elements[:max_elements]
        
        result = {}
        for i, elem in enumerate(elements):
            if simplified:
                elem_data = extract_key_info_from_element(elem, element_type)
            else:
                elem_data = xml_element_to_dict(elem, include_text=True, max_depth=3)
            
            # Use name attribute or index as key
            if "Name" in elem.attrib:
                key = f"{element_type}_{elem.attrib['Name']}"
            else:
                key = f"{element_type}_{i+1}"
                
            result[key] = elem_data
        
        return yaml.dump(result, default_flow_style=False, sort_keys=False)
        
    except Exception as e:
        return yaml.dump({"error": f"Error converting XML to YAML: {str(e)}"})
