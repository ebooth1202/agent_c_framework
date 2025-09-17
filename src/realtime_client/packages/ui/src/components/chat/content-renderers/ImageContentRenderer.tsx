'use client'

import * as React from 'react'
import { cn } from '../../../lib/utils'
import { ImageOff, Maximize2, Minimize2, Download, ExternalLink } from 'lucide-react'
import { Button } from '../../ui/button'

export interface ImageSource {
  type: 'base64' | 'url'
  media_type?: string
  data?: string
  url?: string
}

export interface ImageContentRendererProps {
  /**
   * The image source information
   */
  source: ImageSource
  /**
   * Index of the image in the content array (for unique IDs)
   */
  index?: number
  /**
   * Additional CSS classes
   */
  className?: string
}

/**
 * Renders image content with expand/collapse functionality
 * Supports both base64 and URL image sources
 */
export const ImageContentRenderer: React.FC<ImageContentRendererProps> = ({
  source,
  index = 0,
  className
}) => {
  const [loadError, setLoadError] = React.useState(false)
  const [isExpanded, setIsExpanded] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(true)
  
  // Generate unique ID for accessibility
  const imageId = React.useMemo(() => `image-content-${index}-${Date.now()}`, [index])
  
  // Construct image source URL
  const imageSrc = React.useMemo(() => {
    if (source.type === 'url' && source.url) {
      return source.url
    }
    if (source.type === 'base64' && source.data) {
      const mediaType = source.media_type || 'image/png'
      return `data:${mediaType};base64,${source.data}`
    }
    return null
  }, [source])
  
  // Handle image load completion
  const handleImageLoad = React.useCallback(() => {
    setIsLoading(false)
  }, [])
  
  // Handle image load error
  const handleImageError = React.useCallback(() => {
    setLoadError(true)
    setIsLoading(false)
  }, [])
  
  // Handle download for base64 images
  const handleDownload = React.useCallback(() => {
    if (!imageSrc) return
    
    const link = document.createElement('a')
    link.href = imageSrc
    link.download = `image-${index}.${source.media_type?.split('/')[1] || 'png'}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }, [imageSrc, index, source.media_type])
  
  // Handle open in new tab for URL images
  const handleOpenExternal = React.useCallback(() => {
    if (source.type === 'url' && source.url) {
      window.open(source.url, '_blank', 'noopener,noreferrer')
    }
  }, [source])
  
  // Render error state
  if (!imageSrc || loadError) {
    return (
      <div 
        className={cn(
          "flex items-center gap-2 p-4 bg-muted/30 rounded-lg border border-border",
          className
        )}
        role="alert"
        aria-label={loadError ? 'Failed to load image' : 'Invalid image source'}
      >
        <ImageOff className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
        <span className="text-sm text-muted-foreground">
          {loadError ? 'Failed to load image' : 'Invalid image source'}
        </span>
      </div>
    )
  }
  
  return (
    <div 
      className={cn("relative group", className)}
      role="img"
      aria-labelledby={`${imageId}-label`}
      aria-describedby={`${imageId}-desc`}
    >
      {/* Hidden labels for screen readers */}
      <span id={`${imageId}-label`} className="sr-only">
        Image attachment
      </span>
      <span id={`${imageId}-desc`} className="sr-only">
        {source.media_type || 'Image'} - {isExpanded ? 'Expanded view' : 'Click to expand'}
      </span>
      
      {/* Image container with expand/collapse */}
      <div
        role="button"
        tabIndex={0}
        onClick={() => setIsExpanded(!isExpanded)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault()
            setIsExpanded(!isExpanded)
          }
        }}
        className={cn(
          "relative overflow-hidden rounded-lg border border-border",
          "transition-all duration-200 cursor-pointer",
          "hover:border-primary/50 focus-visible:outline-none",
          "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          isExpanded ? "max-w-full" : "max-w-md"
        )}
        aria-expanded={isExpanded}
        aria-label={isExpanded ? "Collapse image" : "Expand image"}
      >
        {/* Loading placeholder */}
        {isLoading && (
          <div className="absolute inset-0 bg-muted animate-pulse" />
        )}
        
        {/* Actual image */}
        <img
          src={imageSrc}
          alt="Message attachment"
          className={cn(
            "block w-full h-auto",
            !isExpanded && "max-h-64 object-cover",
            isLoading && "opacity-0"
          )}
          onLoad={handleImageLoad}
          onError={handleImageError}
        />
        
        {/* Overlay controls */}
        <div 
          className={cn(
            "absolute top-2 right-2",
            "opacity-0 group-hover:opacity-100",
            "transition-opacity duration-200"
          )}
          onClick={(e) => e.stopPropagation()} // Prevent expand/collapse when clicking controls
        >
          <div className="flex items-center gap-1 bg-background/90 backdrop-blur-sm rounded-md px-2 py-1">
            {/* Expand/Collapse button */}
            <div className="flex items-center gap-1">
              {isExpanded ? (
                <>
                  <Minimize2 className="h-3 w-3" aria-hidden="true" />
                  <span className="text-xs">Collapse</span>
                </>
              ) : (
                <>
                  <Maximize2 className="h-3 w-3" aria-hidden="true" />
                  <span className="text-xs">Expand</span>
                </>
              )}
            </div>
            
            {/* Separator */}
            <div className="w-px h-4 bg-border mx-1" />
            
            {/* Download/Open button */}
            {source.type === 'base64' ? (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-1"
                onClick={handleDownload}
                aria-label="Download image"
              >
                <Download className="h-3 w-3" aria-hidden="true" />
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 px-1"
                onClick={handleOpenExternal}
                aria-label="Open image in new tab"
              >
                <ExternalLink className="h-3 w-3" aria-hidden="true" />
              </Button>
            )}
          </div>
        </div>
      </div>
      
      {/* Media type label */}
      {source.media_type && (
        <div 
          className="mt-1 text-xs text-muted-foreground"
          aria-label={`Image type: ${source.media_type}`}
        >
          {source.media_type}
        </div>
      )}
    </div>
  )
}

export default ImageContentRenderer