"""
Link Rewriter - Smart link processing with code fence awareness.

This module handles the conversion of markdown links to the viewer:// protocol
while preserving code blocks and handling various link resolution strategies.
"""

import re
import logging
from typing import NamedTuple, List, Optional
from urllib.parse import urlparse

from .doc_registry import DocRegistry, DocMeta

logger = logging.getLogger(__name__)


class LinkMatch(NamedTuple):
    """Represents a found markdown link."""
    text: str          # Link text (between [ ])
    target: str        # Link target (between ( ))
    start: int         # Start position in content
    end: int           # End position in content
    full_match: str    # Full matched string


class LinkClassification(NamedTuple):
    """Classification result for a link."""
    link_type: str         # 'external', 'anchor', 'cross_doc', 'unresolved'
    rewritten_target: str  # New target URL
    title: Optional[str] = None  # Optional title attribute


class LinkRewriter:
    """
    Processes markdown content to rewrite links with viewer:// protocol.

    Features:
    - Code fence awareness (skips links inside code blocks)
    - Multiple resolution strategies
    - Unresolved link handling
    - Preserves external URLs and same-doc anchors
    """

    def __init__(self, registry: DocRegistry):
        self.registry = registry

        # Regex patterns
        self.code_fence_pattern = re.compile(r'^(```|~~~)(\w+)?', re.MULTILINE)
        # Use negative lookbehind to avoid matching images ![alt](url)
        self.link_pattern = re.compile(r'(?<!\!)\[([^\]]*)\]\(([^)]+(?:\([^)]*\))*[^)]*)\)')

        # External schemes that should be left unchanged
        self.external_schemes = {'http', 'https', 'mailto', 'tel', 'ftp', 'file', 'data'}

    def rewrite_document_links(self, content: str, source_path: str) -> str:
        """
        Rewrite all links in a document.

        Args:
            content: Raw markdown content
            source_path: Canonical path of the source document

        Returns:
            Content with rewritten links
        """
        # Track code fence boundaries
        fence_ranges = self._find_code_fence_ranges(content)

        # Find all links
        links = self._find_links_outside_code_fences(content, fence_ranges)

        # Process links in reverse order to maintain string positions
        processed_content = content
        for link in reversed(links):
            classification = self._classify_link(link, source_path)
            new_link = self._build_rewritten_link(link, classification)

            processed_content = (
                processed_content[:link.start] +
                new_link +
                processed_content[link.end:]
            )

        return processed_content

    def _find_code_fence_ranges(self, content: str) -> List[tuple[int, int]]:
        """
        Find all code fence ranges in the content.

        Supports both ``` and ~~~ fences, handles unmatched fences (treat as "until EOF"),
        and supports complex language specifications.

        Returns:
            List of (start, end) tuples for code block ranges
        """
        ranges = []
        lines = content.split('\n')
        in_code_block = False
        code_start = 0
        current_pos = 0
        fence_marker = None  # Track which type of fence opened the block

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            # Check for fence markers (``` or ~~~)
            fence_match = re.match(r'^(```|~~~)(.*)$', stripped_line)

            if fence_match:
                current_marker = fence_match.group(1)

                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    code_start = current_pos
                    fence_marker = current_marker
                elif current_marker == fence_marker:
                    # Ending a code block (must match opening fence type)
                    in_code_block = False
                    code_end = current_pos + len(line)
                    ranges.append((code_start, code_end))
                    fence_marker = None
                # If in_code_block but marker doesn't match, ignore (it's content)

            current_pos += len(line) + 1  # +1 for newline

        # Handle unmatched opening fence (treat as "until EOF")
        if in_code_block:
            ranges.append((code_start, current_pos - 1))  # -1 to remove final newline

        return ranges

    def _find_links_outside_code_fences(self, content: str, fence_ranges: List[tuple[int, int]]) -> List[LinkMatch]:
        """Find all markdown links that are outside code fence ranges."""
        links = []

        for match in self.link_pattern.finditer(content):
            start, end = match.span()

            # Check if this link is inside any code fence
            inside_code = any(
                fence_start <= start < fence_end
                for fence_start, fence_end in fence_ranges
            )

            if not inside_code:
                links.append(LinkMatch(
                    text=match.group(1),
                    target=match.group(2),
                    start=start,
                    end=end,
                    full_match=match.group(0)
                ))

        return links

    def _classify_link(self, link: LinkMatch, source_path: str) -> LinkClassification:
        """
        Classify a link and determine how to rewrite it.
        """
        target = (link.target or "").strip()

        # Handle titles: [text](url "title") — keep only the URL part for resolution
        url_only = target.split('"', 1)[0].strip()

        # External URLs/schemes — leave unchanged
        parsed = urlparse(url_only)
        if parsed.scheme in self.external_schemes:
            return LinkClassification(
                link_type='external',
                rewritten_target=link.target  # keep original including any title
            )

        # Same-document anchors — leave unchanged
        if url_only.startswith('#'):
            return LinkClassification(
                link_type='anchor',
                rewritten_target=link.target
            )

        # Split base path and fragment BEFORE resolving
        if '#' in url_only:
            base, frag = url_only.split('#', 1)
            fragment = '#' + frag
        else:
            base, fragment = url_only, ''

        # Resolve only the base path (registry will also unquote if you added that)
        resolved_path = self.registry.resolve_link_target(base, source_path)

        if resolved_path:
            viewer_url = f"viewer://{resolved_path}{fragment}"
            return LinkClassification(
                link_type='cross_doc',
                rewritten_target=viewer_url
            )

        # Unresolved link — render as inline HTML so the template can show a tooltip
        return LinkClassification(
            link_type='unresolved',
            rewritten_target='#',
            title='Not available'
        )

    def _build_rewritten_link(self, link: LinkMatch, classification: LinkClassification) -> str:
        """
        Build the rewritten link string.

        Args:
            link: Original link match
            classification: How to rewrite it

        Returns:
            New link markdown string or inline HTML for unresolved links
        """
        if classification.link_type == 'unresolved':
            # keep your inline-HTML unresolved output
            return (
                f'<a href="{classification.rewritten_target}" '
                f'class="unresolved" title="{classification.title}">{link.text}</a>'
            )

        target = classification.rewritten_target  # e.g., 'viewer://dir2/04 faq.md'
        # NEW: wrap if URL has spaces or other whitespace
        if any(ch.isspace() for ch in target):
            target = f'<{target}>'

        return f'[{link.text}]({target})'

    def get_rewrite_stats(self, content: str, source_path: str) -> dict:
        """Get statistics about link rewriting for debugging."""
        fence_ranges = self._find_code_fence_ranges(content)
        all_links = list(self.link_pattern.finditer(content))
        processable_links = self._find_links_outside_code_fences(content, fence_ranges)

        # Classify all processable links
        classifications = [
            self._classify_link(link, source_path)
            for link in processable_links
        ]

        stats = {
            'total_links_found': len(all_links),
            'links_in_code_fences': len(all_links) - len(processable_links),
            'processable_links': len(processable_links),
            'external_links': sum(1 for c in classifications if c.link_type == 'external'),
            'anchor_links': sum(1 for c in classifications if c.link_type == 'anchor'),
            'cross_doc_links': sum(1 for c in classifications if c.link_type == 'cross_doc'),
            'unresolved_links': sum(1 for c in classifications if c.link_type == 'unresolved'),
            'code_fence_ranges': len(fence_ranges)
        }

        return stats


def rewrite_all_documents(registry: DocRegistry) -> DocRegistry:
    """
    Rewrite links in all documents in the registry.

    Args:
        registry: DocRegistry with documents to process

    Returns:
        New DocRegistry with rewritten content
    """
    rewriter = LinkRewriter(registry)
    new_registry = DocRegistry()

    for path, doc in registry.by_path.items():
        # Rewrite links in the document
        rewritten_content = rewriter.rewrite_document_links(doc.content, doc.path)

        # Create new DocMeta with rewritten content
        new_doc = DocMeta(
            display_name=doc.display_name,
            path=doc.path,
            anchors=doc.anchors,
            content=rewritten_content
        )

        new_registry.add_document(new_doc)

        # Log stats for debugging
        stats = rewriter.get_rewrite_stats(doc.content, doc.path)
        if stats['unresolved_links'] > 0:
            logger.warning(f"Document {path} has {stats['unresolved_links']} unresolved links")
            # Debug: Show what links couldn't be resolved
            debug_changes = preview_link_changes(doc.content, doc.path, registry)
            unresolved_links = [change for change in debug_changes if change['classification'] == 'unresolved']
            for unresolved in unresolved_links[:3]:  # Show first 3 unresolved links
                print(f"  Unresolved link: {unresolved['original']} -> {unresolved['new']}")

        logger.debug(f"Processed {path}: {stats}")

    return new_registry


# Utility functions for testing and debugging

def preview_link_changes(content: str, source_path: str, registry: DocRegistry) -> List[dict]:
    """
    Preview what changes would be made to links without modifying content.

    Returns:
        List of dictionaries with original and new link information
    """
    rewriter = LinkRewriter(registry)
    fence_ranges = rewriter._find_code_fence_ranges(content)
    links = rewriter._find_links_outside_code_fences(content, fence_ranges)

    changes = []
    for link in links:
        classification = rewriter._classify_link(link, source_path)
        new_link = rewriter._build_rewritten_link(link, classification)

        changes.append({
            'original': link.full_match,
            'new': new_link,
            'classification': classification.link_type,
            'position': (link.start, link.end)
        })

    return changes