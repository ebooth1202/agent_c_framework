/**
 * Viewer Bridge - Browser-side link handling for the markdown viewer
 *
 * Handles:
 * - viewer:// protocol links for cross-document navigation
 * - Enhanced anchor scrolling with slug normalization
 * - Unresolved link handling with user feedback
 * - External link management
 */

class ViewerBridge {
    constructor() {
        this.slugger = new Slugger();
        this.setupLinkHandlers();
        this.setupScrollHandlers();
    }

    setupLinkHandlers() {
        // Handle all link clicks through event delegation
        document.addEventListener('click', (event) => {
            const link = event.target.closest('a');
            if (!link) return;

            const href = link.getAttribute('href');
            if (!href) return;

            // Handle different link types
            if (href.startsWith('viewer://')) {
                event.preventDefault();
                this.handleViewerLink(href, link);
            } else if (href.startsWith('#')) {
                event.preventDefault();
                this.handleAnchorLink(href.substring(1), link);
            } else if (link.classList.contains('unresolved')) {
                event.preventDefault();
                this.handleUnresolvedLink(link);
            } else if (href.startsWith('http://') || href.startsWith('https://')) {
                // External links - ensure they open in new tab
                if (!link.hasAttribute('target')) {
                    link.setAttribute('target', '_blank');
                    link.setAttribute('rel', 'noopener noreferrer');
                }
                // Let the browser handle it normally
            }
        });
    }

    setupScrollHandlers() {
        // Handle URL hash changes for direct anchor navigation
        window.addEventListener('hashchange', () => {
            const hash = window.location.hash.substring(1);
            if (hash) {
                this.scrollToAnchor(hash);
            }
        });

        // Handle initial page load with hash
        if (window.location.hash) {
            // Wait for content to render then scroll
            setTimeout(() => {
                const hash = window.location.hash.substring(1);
                this.scrollToAnchor(hash);
            }, 100);
        }
    }

    handleViewerLink(href) {
  const raw = href.slice('viewer://'.length);
  const [pathPart, frag] = raw.split('#', 2);
  let path = pathPart, anchor = frag || '';
  try { path = decodeURIComponent(pathPart); } catch {}
  try { anchor = frag ? decodeURIComponent(frag) : ''; } catch {}
  const ok = typeof openMarkdownFile === 'function' ? openMarkdownFile(path) : false;
  if (ok && anchor) setTimeout(() => this.scrollToAnchor(anchor), 150);
  else if (!ok) this.showNotification(`Document not found: ${path}`, 'error');
}

    handleAnchorLink(anchor, linkElement) {
        console.log(`Anchor navigation: #${anchor}`);
        this.scrollToAnchor(anchor);
    }

    handleUnresolvedLink(linkElement) {
        const title = linkElement.getAttribute('title') || 'Link not available';
        const text = linkElement.textContent || 'link';

        console.log(`Unresolved link clicked: ${text}`);
        this.showNotification(title, 'warning');

        // Add visual feedback
        linkElement.style.backgroundColor = '#fff3cd';
        setTimeout(() => {
            linkElement.style.backgroundColor = '';
        }, 1000);
    }

    scrollToAnchor(anchor) {
        if (!anchor) return;

        console.log(`Attempting to scroll to anchor: ${anchor}`);

        // Strategy 1: Try direct ID match
        let element = document.getElementById(anchor);
        if (element) {
            this.performScroll(element, anchor);
            return;
        }

        // Strategy 2: Try normalized anchor
        const normalizedAnchor = this.normalizeAnchor(anchor);
        if (normalizedAnchor !== anchor) {
            element = document.getElementById(normalizedAnchor);
            if (element) {
                console.log(`Found with normalized anchor: ${normalizedAnchor}`);
                this.performScroll(element, anchor);
                return;
            }
        }

        // Strategy 3: Try case-insensitive search
        const allElements = document.querySelectorAll('[id]');
        for (const el of allElements) {
            if (el.id.toLowerCase() === anchor.toLowerCase()) {
                console.log(`Found with case-insensitive match: ${el.id}`);
                this.performScroll(el, anchor);
                return;
            }
        }

        // Strategy 4: Try heading text matching
        const headings = document.querySelectorAll('#markdown-content h1, #markdown-content h2, #markdown-content h3, #markdown-content h4, #markdown-content h5, #markdown-content h6');
        for (const heading of headings) {
            const headingSlug = this.slugger.slug(heading.textContent);
            if (headingSlug === normalizedAnchor || headingSlug === anchor.toLowerCase()) {
                console.log(`Found by heading text matching: ${heading.textContent} -> ${headingSlug}`);
                this.performScroll(heading, anchor);
                return;
            }
        }

        console.warn(`Anchor not found: ${anchor}`);
        this.showNotification(`Section not found: ${anchor}`, 'warning');
    }

    performScroll(element, originalAnchor) {
        // Smooth scroll to element
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });

        // Visual highlight
        this.highlightElement(element);

        // Update URL hash if different
        if (window.location.hash !== `#${originalAnchor}`) {
            // Update without triggering hashchange event
            history.replaceState(null, null, `#${originalAnchor}`);
        }
    }

    highlightElement(element) {
        const originalBackground = element.style.backgroundColor;
        const originalTransition = element.style.transition;

        // Add highlight
        element.style.transition = 'background-color 0.3s ease';
        element.style.backgroundColor = 'rgba(253, 184, 37, 0.3)'; // Brand gold with transparency

        // Remove highlight after delay
        setTimeout(() => {
            element.style.backgroundColor = originalBackground;
            setTimeout(() => {
                element.style.transition = originalTransition;
            }, 300);
        }, 1500);
    }

    normalizeAnchor(anchor) {
        // Remove leading # if present
        anchor = anchor.replace(/^#+/, '');

        // Basic normalization to match slugger
        let normalized = anchor.trim().toLowerCase();
        normalized = normalized.replace(/[^\w\s-]/g, '');
        normalized = normalized.replace(/[\s_-]+/g, '-');
        normalized = normalized.replace(/^-+|-+$/g, '');

        return normalized || 'heading';
    }

    showNotification(message, type = 'info') {
        // Create or update notification element
        let notification = document.getElementById('viewer-notification');
        if (!notification) {
            notification = document.createElement('div');
            notification.id = 'viewer-notification';
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 16px;
                border-radius: 6px;
                color: white;
                font-family: 'Roboto', sans-serif;
                font-size: 14px;
                z-index: 10000;
                opacity: 0;
                transition: opacity 0.3s ease;
                max-width: 300px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            `;
            document.body.appendChild(notification);
        }

        // Set type-specific styling
        const colors = {
            info: '#2d84bb',      // Cerulean
            warning: '#fdb825',   // Gold
            error: '#dc3545',     // Red
            success: '#2fb677'    // Shamrock
        };

        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;

        // Show notification
        notification.style.opacity = '1';

        // Auto-hide after delay
        setTimeout(() => {
            notification.style.opacity = '0';
        }, 3000);
    }

    // Utility method to get all available anchors (for debugging)
    getAvailableAnchors() {
        const anchors = [];
        const elements = document.querySelectorAll('[id]');
        elements.forEach(el => {
            anchors.push({
                id: el.id,
                tag: el.tagName.toLowerCase(),
                text: el.textContent.substring(0, 50)
            });
        });
        return anchors;
    }
}

// Slugger class (same as Python version)
class Slugger {
    constructor() {
        this.seen = new Set();
    }

    slug(text, maintainCase = false) {
        let slug = text.trim();

        // Remove markdown formatting
        slug = slug.replace(/[*_`]+/g, '');
        slug = slug.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

        // Normalize unicode (basic)
        slug = slug.normalize('NFKD');

        // Case handling
        if (!maintainCase) {
            slug = slug.toLowerCase();
        }

        // Replace special chars and spaces
        slug = slug.replace(/[^\w\s-]/g, '');
        slug = slug.replace(/[\s_-]+/g, '-');
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

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.viewerBridge = new ViewerBridge();
    });
} else {
    window.viewerBridge = new ViewerBridge();
}

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ViewerBridge, Slugger };
}