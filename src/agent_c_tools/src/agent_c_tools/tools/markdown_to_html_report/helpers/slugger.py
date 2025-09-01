"""
Slugger - Shared slug normalization utilities.

This module provides consistent slug generation rules that match
what the browser-side renderer will produce for heading IDs.
"""

import re
import unicodedata
from typing import Set


class Slugger:
    """
    A slugger that generates URL-safe anchor IDs from heading text.

    Designed to match the behavior of marked.js Slugger for consistency
    between Python link processing and browser-side rendering.
    """

    def __init__(self):
        self.seen_slugs: Set[str] = set()

    def slug(self, text: str, maintain_case: bool = False) -> str:
        """
        Generate a URL-safe slug from text.

        Args:
            text: Input text (typically a heading)
            maintain_case: If True, preserve original case; if False, lowercase

        Returns:
            URL-safe slug string
        """
        # Start with the raw text
        slug = text.strip()

        # Remove markdown formatting (basic)
        slug = re.sub(r'[*_`]+', '', slug)  # Remove emphasis markers
        slug = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', slug)  # Extract link text

        # Normalize unicode characters
        slug = unicodedata.normalize('NFKD', slug)

        # Convert to lowercase unless maintaining case
        if not maintain_case:
            slug = slug.lower()

        # Replace spaces and non-alphanumeric chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars except spaces and hyphens
        slug = re.sub(r'[\s_-]+', '-', slug)  # Replace runs of spaces/underscores/hyphens with single hyphen
        slug = slug.strip('-')  # Remove leading/trailing hyphens

        # Handle empty slug
        if not slug:
            slug = 'heading'

        # Ensure uniqueness by appending numbers if needed
        original_slug = slug
        counter = 1
        while slug in self.seen_slugs:
            slug = f"{original_slug}-{counter}"
            counter += 1

        self.seen_slugs.add(slug)
        return slug

    def reset(self):
        """Reset the seen slugs tracker."""
        self.seen_slugs.clear()


def normalize_anchor(anchor: str) -> str:
    """
    Normalize an anchor string to match common slug generation rules.

    This is a simpler version that doesn't track uniqueness,
    useful for normalizing user-provided anchor links.

    Args:
        anchor: Raw anchor string (may include #)

    Returns:
        Normalized anchor string (without #)
    """
    # Remove leading # if present
    anchor = anchor.lstrip('#')

    # Basic normalization similar to slug()
    normalized = anchor.strip().lower()
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    normalized = re.sub(r'[\s_-]+', '-', normalized)
    normalized = normalized.strip('-')

    return normalized or 'heading'


def extract_headings_with_slugs(markdown_content: str) -> dict[str, str]:
    """
    Extract headings from markdown and generate consistent slugs.

    Args:
        markdown_content: Raw markdown content

    Returns:
        Dictionary mapping original heading text to generated slug
    """
    slugger = Slugger()
    headings = {}

    # Pattern for ATX headings (# ## ### etc.)
    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    for match in heading_pattern.finditer(markdown_content):
        level_markers = match.group(1)
        heading_text = match.group(2).strip()
        level = len(level_markers)

        slug = slugger.slug(heading_text)
        headings[heading_text] = slug

    return headings


def generate_toc_from_headings(markdown_content: str, max_level: int = 3) -> str:
    """
    Generate a table of contents from markdown headings.

    Args:
        markdown_content: Raw markdown content
        max_level: Maximum heading level to include (1-6)

    Returns:
        Markdown table of contents as string
    """
    slugger = Slugger()
    toc_lines = []

    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    for match in heading_pattern.finditer(markdown_content):
        level_markers = match.group(1)
        heading_text = match.group(2).strip()
        level = len(level_markers)

        if level <= max_level:
            slug = slugger.slug(heading_text)
            indent = '  ' * (level - 1)
            toc_lines.append(f"{indent}- [{heading_text}](#{slug})")

    return '\n'.join(toc_lines)


# JavaScript-compatible slugger for browser-side use
JAVASCRIPT_SLUGGER_CODE = '''
/**
 * JavaScript Slugger - matches Python slugger behavior
 * 
 * Usage:
 *   const slugger = new Slugger();
 *   const slug = slugger.slug("My Heading Text");
 */
class Slugger {
    constructor() {
        this.seen = new Set();
    }

    slug(text, maintainCase = false) {
        let slug = text.trim();

        // Remove markdown formatting
        slug = slug.replace(/[*_`]+/g, '');
        slug = slug.replace(/\\[([^\\]]+)\\]\\([^)]+\\)/g, '$1');

        // Normalize unicode (basic)
        slug = slug.normalize('NFKD');

        // Case handling
        if (!maintainCase) {
            slug = slug.toLowerCase();
        }

        // Replace special chars and spaces
        slug = slug.replace(/[^\\w\\s-]/g, '');
        slug = slug.replace(/[\\s_-]+/g, '-');
        slug = slug.replace(/^-+|-+$/g, '');

        // Handle empty
        if (!slug) {
            slug = 'heading';
        }

        // Ensure uniqueness
        let originalSlug = slug;
        let counter = 1;
        while (this.seen.has(slug)) {
            slug = `${originalSlug}-${counter}`;
            counter++;
        }

        this.seen.add(slug);
        return slug;
    }

    reset() {
        this.seen.clear();
    }
}

function normalizeAnchor(anchor) {
    // Remove leading # if present
    anchor = anchor.replace(/^#+/, '');

    // Basic normalization
    let normalized = anchor.trim().toLowerCase();
    normalized = normalized.replace(/[^\\w\\s-]/g, '');
    normalized = normalized.replace(/[\\s_-]+/g, '-');
    normalized = normalized.replace(/^-+|-+$/g, '');

    return normalized || 'heading';
}
'''


def get_javascript_slugger_code() -> str:
    """
    Get JavaScript code for browser-side slugger that matches Python behavior.

    Returns:
        JavaScript code as string
    """
    return JAVASCRIPT_SLUGGER_CODE