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
