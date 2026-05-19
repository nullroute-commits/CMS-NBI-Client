from typing import Any, Dict, Union
from xml.etree.ElementTree import Element, SubElement, tostring

import defusedxml.ElementTree as ET
import structlog

logger = structlog.get_logger()


class SecureXMLHandler:
    """Secure XML parsing and generation"""

    # XML Schema for validation
    NETCONF_SCHEMA = """<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
        <!-- Schema definition here -->
    </xs:schema>
    """

    def __init__(self) -> None:
        self._schema = None

    def parse(self, xml_string: str) -> Dict[str, Any]:
        """Safely parse XML string"""
        try:
            # Use defusedxml to prevent XML attacks
            root = ET.fromstring(xml_string)

            # Validate against schema if available
            if self._schema:
                self._schema.assertValid(root)

            # Convert to dict
            result = self._element_to_dict(root)
            # Ensure we always return a dict
            if isinstance(result, str):
                return {root.tag: result}
            return result

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise ValueError(f"Invalid XML: {e}")
        except Exception as e:
            logger.error(f"Unexpected error parsing XML: {e}")
            raise

    def _element_to_dict(self, element: Element) -> Union[Dict[str, Any], str]:
        """Convert XML element to dictionary"""
        result: Dict[str, Any] = {}

        # Add attributes
        if element.attrib:
            result["@attributes"] = element.attrib

        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # No children
                return element.text.strip()
            else:
                result["#text"] = element.text.strip()

        # Add children
        for child in element:
            child_data = self._element_to_dict(child)
            if child.tag in result:
                # Convert to list if multiple children with same tag
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)  # type: ignore
            else:
                result[child.tag] = child_data

        return result

    def build(self, data: Dict[str, Any]) -> str:
        """Build XML from dictionary using templates"""
        if len(data) != 1:
            raise ValueError("XML data must contain exactly one root element")

        root_name, root_value = next(iter(data.items()))
        root = Element(root_name)
        self._dict_to_element(root, root_value)
        return tostring(root, encoding="unicode")

    def _dict_to_element(self, element: Element, value: Any) -> None:
        """Recursively convert a dictionary value into XML elements."""
        if isinstance(value, dict):
            attributes = value.get("@attributes", {})
            for key, attr_value in attributes.items():
                element.set(key, str(attr_value))

            if "#text" in value and value["#text"] is not None:
                element.text = str(value["#text"])

            for child_name, child_value in value.items():
                if child_name in {"@attributes", "#text"}:
                    continue

                if isinstance(child_value, list):
                    for item in child_value:
                        child = SubElement(element, child_name)
                        self._dict_to_element(child, item)
                else:
                    child = SubElement(element, child_name)
                    self._dict_to_element(child, child_value)
            return

        if value is not None:
            element.text = str(value)


def parse_xml_safely(xml_string: str) -> Dict[str, Any]:
    """Parse XML with the repository's secure XML handler."""
    return SecureXMLHandler().parse(xml_string)
