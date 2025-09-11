/**
 * RichMediaHandler - Processes and validates rich media content
 * For core SDK, provides validation logic without sanitization (done in UI layer)
 */

import { RenderMediaEvent } from './types/ServerEvents';
import { Logger } from '../utils/logger';

/**
 * Rich media content structure
 */
export interface RichMediaContent {
  id: string;
  type: 'html' | 'svg' | 'image' | 'unknown';
  content: string;
  contentType: string;
  metadata: {
    sentByClass: string;
    sentByFunction: string;
    timestamp: Date;
  };
  needsSanitization: boolean;
}

/**
 * Media type detection patterns
 */
const MEDIA_TYPE_PATTERNS = {
  html: /text\/html/i,
  svg: /(image\/svg\+xml|text\/svg)/i,
  image: /image\/(png|jpeg|jpg|gif|webp)/i
};

/**
 * Processes rich media events from tools
 */
export class RichMediaHandler {
  
  constructor() {
  }
  
  /**
   * Process a render media event
   */
  processRenderMediaEvent(event: RenderMediaEvent): RichMediaContent {
    const mediaType = this.determineMediaType(event.content_type);
    const needsSanitization = this.requiresSanitization(mediaType);
    
    const media: RichMediaContent = {
      id: this.generateMediaId(),
      type: mediaType,
      content: event.content,
      contentType: event.content_type,
      metadata: {
        sentByClass: event.sent_by_class,
        sentByFunction: event.sent_by_function,
        timestamp: new Date()
      },
      needsSanitization
    };
    
    Logger.info(`[RichMediaHandler] Processed rich media`, {
      id: media.id,
      type: media.type,
      contentType: media.contentType,
      contentLength: media.content.length,
      sentBy: `${media.metadata.sentByClass}.${media.metadata.sentByFunction}`,
      needsSanitization
    });
    
    return media;
  }
  
  /**
   * Determine the media type from content type string
   */
  private determineMediaType(contentType: string): RichMediaContent['type'] {
    if (!contentType) {
      return 'unknown';
    }
    
    if (MEDIA_TYPE_PATTERNS.html.test(contentType)) {
      return 'html';
    }
    
    if (MEDIA_TYPE_PATTERNS.svg.test(contentType)) {
      return 'svg';
    }
    
    if (MEDIA_TYPE_PATTERNS.image.test(contentType)) {
      return 'image';
    }
    
    // Default to HTML for text types
    if (contentType.startsWith('text/')) {
      return 'html';
    }
    
    return 'unknown';
  }
  
  /**
   * Check if content requires sanitization
   */
  private requiresSanitization(type: RichMediaContent['type']): boolean {
    // HTML and SVG content should be sanitized before rendering
    return type === 'html' || type === 'svg';
  }
  
  /**
   * Validate media content structure
   */
  validateContent(content: string, type: RichMediaContent['type']): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];
    
    if (!content) {
      errors.push('Content is empty');
      return { isValid: false, errors };
    }
    
    // Basic validation based on type
    switch (type) {
      case 'svg':
        if (!content.includes('<svg') && !content.includes('<?xml')) {
          errors.push('Content does not appear to be valid SVG');
        }
        break;
        
      case 'html':
        // Very basic HTML validation
        if (content.length > 0 && !/<[^>]+>/.test(content)) {
          errors.push('Content does not appear to contain HTML tags');
        }
        break;
        
      case 'image':
        // For base64 images, check the data URI format
        if (content.startsWith('data:image/')) {
          const parts = content.split(',');
          if (parts.length !== 2) {
            errors.push('Invalid data URI format for image');
          }
        }
        break;
        
      case 'unknown':
        errors.push('Unknown media type');
        break;
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }
  
  /**
   * Extract metadata from content if available
   */
  extractContentMetadata(content: string, type: RichMediaContent['type']): Record<string, any> {
    const metadata: Record<string, any> = {};
    
    try {
      switch (type) {
        case 'svg':
          // Extract SVG dimensions if present
          const widthMatch = content.match(/width=["']?(\d+)/);
          const heightMatch = content.match(/height=["']?(\d+)/);
          if (widthMatch && widthMatch[1]) metadata.width = parseInt(widthMatch[1], 10);
          if (heightMatch && heightMatch[1]) metadata.height = parseInt(heightMatch[1], 10);
          
          // Extract viewBox if present
          const viewBoxMatch = content.match(/viewBox=["']?([\d\s\-\.]+)/);
          if (viewBoxMatch) metadata.viewBox = viewBoxMatch[1];
          break;
          
        case 'html':
          // Extract title if present
          const titleMatch = content.match(/<title[^>]*>([^<]+)<\/title>/i);
          if (titleMatch) metadata.title = titleMatch[1];
          
          // Check for scripts (security concern)
          metadata.hasScripts = /<script[^>]*>/i.test(content);
          
          // Check for external resources
          metadata.hasExternalResources = /(src|href)=["']?https?:/i.test(content);
          break;
          
        case 'image':
          // For data URIs, extract MIME type
          if (content.startsWith('data:')) {
            const mimeMatch = content.match(/^data:([^;]+)/);
            if (mimeMatch) metadata.mimeType = mimeMatch[1];
          }
          break;
      }
      
      metadata.contentLength = content.length;
    } catch (error) {
      Logger.warn('[RichMediaHandler] Error extracting content metadata', error);
    }
    
    return metadata;
  }
  
  /**
   * Generate a unique media ID
   */
  private generateMediaId(): string {
    return `media_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
  
  /**
   * Create a placeholder for unsupported media
   */
  createPlaceholder(type: string, reason: string): RichMediaContent {
    return {
      id: this.generateMediaId(),
      type: 'html',
      content: `
        <div style="padding: 16px; border: 1px solid #e0e0e0; border-radius: 4px; background: #f5f5f5;">
          <p style="margin: 0; color: #666;">
            <strong>Unsupported Media Type:</strong> ${type}<br/>
            <span style="color: #999; font-size: 0.9em;">${reason}</span>
          </p>
        </div>
      `,
      contentType: 'text/html',
      metadata: {
        sentByClass: 'system',
        sentByFunction: 'placeholder',
        timestamp: new Date()
      },
      needsSanitization: false
    };
  }
  
  /**
   * Check if content size is acceptable
   */
  isContentSizeAcceptable(content: string, maxSizeKB: number = 1024): boolean {
    const sizeInKB = content.length / 1024;
    const isAcceptable = sizeInKB <= maxSizeKB;
    
    if (!isAcceptable) {
      Logger.warn(`[RichMediaHandler] Content size exceeds limit`, {
        sizeKB: sizeInKB.toFixed(2),
        maxSizeKB
      });
    }
    
    return isAcceptable;
  }
}