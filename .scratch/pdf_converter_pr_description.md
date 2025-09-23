# Add PDF to YAML Converter Tool

## Description

This PR adds a new tool to Agent C that converts PDF documents to structured YAML format. The tool extracts text content, metadata, and document structure, making it easier for agents to work with information contained in PDF files.

## Features

- Extract text content from PDFs by page or as a single text block
- Extract PDF metadata (title, author, creation date, etc.)
- Output structured data in YAML format
- Robust error handling for various PDF parsing issues

## Implementation Details

- Added new `pdf_converter` toolset with a `pdf_to_yaml` tool
- Implemented `PDFProcessor` utility class for PDF parsing and conversion
- Added unit tests to verify functionality
- Added comprehensive documentation
- Added PyPDF2 as a dependency in setup.py

## Testing

Unit tests have been added that verify:
- Tool parameter validation
- PDF processing logic
- Error handling

## Dependencies

- Added PyPDF2 to the project dependencies
- PyYAML was already a dependency

## Documentation

Added a README.md file with usage examples, parameter descriptions, and output format documentation.

## Checklist

- [x] Added new toolset and tool implementation
- [x] Added comprehensive error handling
- [x] Updated tool registration in `__init__.py`
- [x] Added unit tests
- [x] Added documentation
- [x] Updated dependencies in setup.py