import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef(({ className, variant, ...props }, ref) => {
  // Define base classes for the card
  const baseClasses = "rounded-xl border shadow"
  
  // Add background classes based on variant
  const bgClasses = variant === "transparent" 
    ? "bg-transparent" 
    : "bg-card text-card-foreground"
  
  return (
    <div
      ref={ref}
      className={cn(baseClasses, bgClasses, className)}
      {...props}
    />
  )
})
Card.displayName = "Card"

const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("font-semibold leading-none tracking-tight", className)}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

export { Card, CardHeader, CardTitle, CardContent }