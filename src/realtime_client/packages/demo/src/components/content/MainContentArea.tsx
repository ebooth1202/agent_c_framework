"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { ChatMessagesView } from "./ChatMessagesView"
import { AvatarDisplayView } from "./AvatarDisplayView"
import { VoiceVisualizerView } from "./VoiceVisualizerView"

export type OutputMode = 'chat' | 'avatar' | 'voice'

export interface MainContentAreaProps {
  outputMode: OutputMode
  className?: string
}

/**
 * MainContentArea component - Container that switches between display modes
 * Renders different views based on the selected output mode
 */
export const MainContentArea = React.forwardRef<HTMLDivElement, MainContentAreaProps>(
  ({ outputMode, className }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex-1 overflow-hidden relative",
          className
        )}
      >
        {outputMode === 'chat' && <ChatMessagesView />}
        {outputMode === 'avatar' && <AvatarDisplayView />}
        {outputMode === 'voice' && <VoiceVisualizerView />}
      </div>
    )
  }
)
MainContentArea.displayName = "MainContentArea"