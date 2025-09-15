/**
 * ToolCallManager - Tracks tool usage lifecycle and manages tool state
 * Manages tool state from selection through completion
 */

import { ToolCall, ToolResult } from './types/CommonTypes';
import { ToolSelectDeltaEvent, ToolCallEvent } from './types/ServerEvents';
import { Logger } from '../utils/logger';

/**
 * Tool notification for UI display
 */
export interface ToolNotification {
  id: string;
  toolName: string;
  status: 'preparing' | 'executing' | 'complete';
  timestamp: Date;
  arguments?: string;
}

/**
 * Extended tool call with result
 */
export interface ToolCallWithResult extends ToolCall {
  result?: ToolResult;
}

/**
 * Manages tool call state and notifications
 */
export class ToolCallManager {
  private activeTools: Map<string, ToolNotification> = new Map();
  private completedToolCalls: ToolCallWithResult[] = [];
  
  constructor() {
  }
  
  /**
   * Handle tool selection event (before execution)
   */
  onToolSelect(event: ToolSelectDeltaEvent): ToolNotification {
    const toolCall = event.tool_calls[0];
    if (!toolCall) {
      throw new Error('ToolSelectDeltaEvent has no tool calls');
    }
    
    const notification: ToolNotification = {
      id: toolCall.id,
      toolName: toolCall.name,
      status: 'preparing',
      timestamp: new Date(),
      arguments: JSON.stringify(toolCall.input)
    };
    
    this.activeTools.set(toolCall.id, notification);
    
    Logger.info(`[ToolCallManager] Tool selected: ${toolCall.name}`, {
      id: toolCall.id,
      arguments: JSON.stringify(toolCall.input)
    });
    
    return notification;
  }
  
  /**
   * Handle tool call active event (during execution)
   */
  onToolCallActive(event: ToolCallEvent): ToolNotification | null {
    if (!event.active) {
      return null;
    }
    
    const toolCall = event.tool_calls[0];
    if (!toolCall) {
      return null;
    }
    
    const notification = this.activeTools.get(toolCall.id);
    
    if (notification) {
      notification.status = 'executing';
      Logger.info(`[ToolCallManager] Tool executing: ${notification.toolName}`, {
        id: toolCall.id
      });
      return notification;
    }
    
    // If we don't have a notification yet, create one
    const newNotification: ToolNotification = {
      id: toolCall.id,
      toolName: toolCall.name,
      status: 'executing',
      timestamp: new Date(),
      arguments: JSON.stringify(toolCall.input)
    };
    
    this.activeTools.set(toolCall.id, newNotification);
    
    Logger.info(`[ToolCallManager] Tool executing (no prior selection): ${toolCall.name}`, {
      id: toolCall.id
    });
    
    return newNotification;
  }
  
  /**
   * Handle tool call completion event
   */
  onToolCallComplete(event: ToolCallEvent): ToolCallWithResult[] {
    if (event.active) {
      return [];
    }
    
    const newlyCompleted: ToolCallWithResult[] = [];
    
    event.tool_calls.forEach(toolCall => {
      // Mark as complete and remove from active
      const notification = this.activeTools.get(toolCall.id);
      if (notification) {
        notification.status = 'complete';
      }
      this.activeTools.delete(toolCall.id);
      
      // Find the result for this tool call
      const result = event.tool_results?.find(r => r.tool_use_id === toolCall.id);
      
      // Add to completed list
      const completedCall: ToolCallWithResult = {
        ...toolCall,
        result
      };
      
      this.completedToolCalls.push(completedCall);
      newlyCompleted.push(completedCall);
      
      Logger.info(`[ToolCallManager] Tool completed: ${toolCall.name}`, {
        id: toolCall.id,
        hasResult: !!result,
        resultLength: result?.content?.length
      });
    });
    
    return newlyCompleted;
  }
  
  /**
   * Get all active tool notifications
   */
  getActiveNotifications(): ToolNotification[] {
    return Array.from(this.activeTools.values())
      .filter(n => n.status !== 'complete');
  }
  
  /**
   * Get all completed tool calls
   */
  getCompletedToolCalls(): ToolCallWithResult[] {
    return [...this.completedToolCalls];
  }
  
  /**
   * Get a specific tool notification by ID
   */
  getNotification(id: string): ToolNotification | undefined {
    return this.activeTools.get(id);
  }
  
  /**
   * Check if a tool is currently active
   */
  isToolActive(id: string): boolean {
    const notification = this.activeTools.get(id);
    return notification !== undefined && notification.status !== 'complete';
  }
  
  /**
   * Get count of active tools
   */
  getActiveToolCount(): number {
    return this.getActiveNotifications().length;
  }
  
  /**
   * Clear completed tool calls
   */
  clearCompleted(): void {
    this.completedToolCalls = [];
    Logger.debug('[ToolCallManager] Cleared completed tool calls');
  }
  
  /**
   * Reset all state
   */
  reset(): void {
    this.activeTools.clear();
    this.completedToolCalls = [];
    Logger.debug('[ToolCallManager] ToolCallManager reset');
  }
  
  /**
   * Get statistics about tool usage
   */
  getStatistics(): {
    activeCount: number;
    completedCount: number;
    totalCount: number;
  } {
    return {
      activeCount: this.getActiveToolCount(),
      completedCount: this.completedToolCalls.length,
      totalCount: this.getActiveToolCount() + this.completedToolCalls.length
    };
  }
}