/**
 * UserDisplay Component - Display user profile information from WebSocket events
 * Supports compact and full display variants with loading states
 */

import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { 
  LogOut, 
  Settings, 
  User as UserIcon, 
  ChevronDown,
  Shield,
  Users,
  Calendar,
  Clock,
  Mail
} from "lucide-react";
import { cn } from "../../lib/utils";
import { 
  useAgentCData, 
  useInitializationStatus, 
  useConnection 
} from "@agentc/realtime-react";
import { ConnectionState } from "@agentc/realtime-core";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Separator } from "../ui/separator";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";

const userDisplayVariants = cva(
  "inline-flex items-center transition-colors",
  {
    variants: {
      variant: {
        compact: "gap-2",
        full: "flex-col gap-4 p-4 rounded-lg border bg-card",
      },
      state: {
        loading: "animate-pulse opacity-70",
        error: "opacity-50",
        ready: "",
      }
    },
    defaultVariants: {
      variant: "compact",
      state: "ready",
    },
  }
);

export interface UserDisplayProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof userDisplayVariants> {
  /** Show dropdown menu with actions */
  showMenu?: boolean;
  /** Show connection status indicator */
  showConnectionStatus?: boolean;
  /** Custom avatar URL (overrides user data) */
  avatarUrl?: string;
  /** Avatar size (for compact variant) */
  avatarSize?: "sm" | "md" | "lg";
  /** Callback when logout is clicked */
  onLogout?: () => void;
  /** Callback when settings is clicked */
  onSettings?: () => void;
  /** Custom menu items to add to dropdown */
  customMenuItems?: Array<{
    label: string;
    icon?: React.ReactNode;
    onClick: () => void;
    variant?: "default" | "destructive";
  }>;
}

const UserDisplay = React.forwardRef<HTMLDivElement, UserDisplayProps>(
  (
    {
      className,
      variant = "compact",
      showMenu = false,
      showConnectionStatus = false,
      avatarUrl,
      avatarSize = "md",
      onLogout,
      onSettings,
      customMenuItems,
      ...props
    },
    ref
  ) => {
    // Get user data from SDK hooks
    const { user } = useAgentCData();
    const { isInitialized, pendingEvents } = useInitializationStatus();
    const { isConnected, connectionState } = useConnection();

    // Determine loading state
    const isLoading = !isInitialized || pendingEvents.includes('chat_user_data');
    
    // Calculate display name and initials
    const displayName = React.useMemo(() => {
      if (!user) return "Loading...";
      
      // Try full name first
      if (user.first_name && user.last_name) {
        return `${user.first_name} ${user.last_name}`;
      }
      
      // Fall back to user_name
      if (user.user_name) {
        return user.user_name;
      }
      
      // Fall back to email
      if (user.email) {
        return user.email.split('@')[0];
      }
      
      return "Unknown User";
    }, [user]);

    const initials = React.useMemo(() => {
      if (!user) return "??";
      
      if (user.first_name && user.last_name) {
        return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
      }
      
      if (user.user_name && user.user_name.length > 1) {
        return user.user_name.substring(0, 2).toUpperCase();
      }
      
      if (user.email) {
        return user.email.substring(0, 2).toUpperCase();
      }
      
      return "??";
    }, [user]);

    // Avatar sizes mapping
    const avatarSizeClasses = {
      sm: "h-8 w-8",
      md: "h-10 w-10",
      lg: "h-12 w-12",
    };

    // Format date helper
    const formatDate = (dateStr: string | null) => {
      if (!dateStr) return "Never";
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, { 
        month: 'short', 
        day: 'numeric', 
        year: 'numeric' 
      });
    };

    // Loading skeleton for compact variant
    if (variant === "compact" && isLoading) {
      return (
        <div 
          ref={ref} 
          className={cn(userDisplayVariants({ variant, state: "loading" }), className)}
          {...props}
        >
          <div className={cn("rounded-full bg-muted", avatarSizeClasses[avatarSize])} />
          <div className="space-y-1">
            <div className="h-4 w-24 bg-muted rounded" />
            <div className="h-3 w-16 bg-muted rounded" />
          </div>
        </div>
      );
    }

    // Loading skeleton for full variant
    if (variant === "full" && isLoading) {
      return (
        <div 
          ref={ref}
          className={cn(userDisplayVariants({ variant, state: "loading" }), className)}
          {...props}
        >
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-muted" />
            <div className="space-y-2 flex-1">
              <div className="h-5 w-32 bg-muted rounded" />
              <div className="h-4 w-48 bg-muted rounded" />
            </div>
          </div>
          <Separator />
          <div className="space-y-3">
            <div className="h-4 w-full bg-muted rounded" />
            <div className="h-4 w-3/4 bg-muted rounded" />
            <div className="h-4 w-1/2 bg-muted rounded" />
          </div>
        </div>
      );
    }

    // Error state
    if (!user && isInitialized) {
      return (
        <div 
          ref={ref}
          className={cn(userDisplayVariants({ variant, state: "error" }), className)}
          {...props}
        >
          <Avatar className={avatarSizeClasses[avatarSize]}>
            <AvatarFallback className="bg-destructive/10 text-destructive">
              <UserIcon className="h-4 w-4" />
            </AvatarFallback>
          </Avatar>
          {variant === "compact" && (
            <span className="text-sm text-muted-foreground">No user data</span>
          )}
          {variant === "full" && (
            <div className="text-center space-y-2">
              <p className="text-sm font-medium text-destructive">Unable to load user data</p>
              <p className="text-xs text-muted-foreground">Please check your connection</p>
            </div>
          )}
        </div>
      );
    }

    // Compact variant display
    if (variant === "compact") {
      const compactContent = (
        <div className={cn(userDisplayVariants({ variant }), className)} {...props}>
          <Avatar className={avatarSizeClasses[avatarSize]}>
            {avatarUrl && <AvatarImage src={avatarUrl} alt={displayName} />}
            <AvatarFallback>{initials}</AvatarFallback>
          </Avatar>
          
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium truncate">{displayName}</p>
            {user?.email && (
              <p className="text-xs text-muted-foreground truncate">{user.email}</p>
            )}
          </div>

          {showConnectionStatus && (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span
                    className={cn(
                      "h-2 w-2 rounded-full",
                      isConnected ? "bg-green-500" : "bg-gray-400",
                      connectionState === ConnectionState.CONNECTING && "bg-yellow-500 animate-pulse"
                    )}
                    aria-label={`Connection status: ${connectionState}`}
                  />
                </TooltipTrigger>
                <TooltipContent>
                  <p className="text-xs capitalize">{connectionState}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}
        </div>
      );

      if (showMenu) {
        return (
          <div ref={ref}>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="h-auto p-2 justify-start"
                  aria-label="User menu"
                >
                  {compactContent}
                  <ChevronDown className="h-4 w-4 ml-2 opacity-50" />
                </Button>
              </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{displayName}</p>
                  {user?.email && (
                    <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                  )}
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              
              {onSettings && (
                <DropdownMenuItem onClick={onSettings}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
              )}
              
              {customMenuItems?.map((item, index) => (
                <DropdownMenuItem
                  key={index}
                  onClick={item.onClick}
                  className={item.variant === "destructive" ? "text-destructive focus:text-destructive" : ""}
                >
                  {item.icon && <span className="mr-2">{item.icon}</span>}
                  <span>{item.label}</span>
                </DropdownMenuItem>
              ))}
              
              {onLogout && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={onLogout} className="text-destructive focus:text-destructive">
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      );
      }

      return <div ref={ref}>{compactContent}</div>;
    }

    // Full variant display
    return (
      <div
        ref={ref}
        className={cn(userDisplayVariants({ variant }), className)}
        {...props}
      >
        {/* Header Section */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16">
              {avatarUrl && <AvatarImage src={avatarUrl} alt={displayName} />}
              <AvatarFallback className="text-lg">{initials}</AvatarFallback>
            </Avatar>
            
            <div className="space-y-1">
              <h3 className="text-lg font-semibold">{displayName}</h3>
              {user?.email && (
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Mail className="h-3 w-3" />
                  {user.email}
                </p>
              )}
              <div className="flex items-center gap-2">
                {user?.is_active ? (
                  <Badge variant="secondary" className="text-xs">Active</Badge>
                ) : (
                  <Badge variant="outline" className="text-xs">Inactive</Badge>
                )}
                {showConnectionStatus && (
                  <Badge 
                    variant={isConnected ? "secondary" : "outline"}
                    className="text-xs"
                  >
                    {connectionState === ConnectionState.CONNECTING ? "Connecting..." : 
                     isConnected ? "Connected" : "Disconnected"}
                  </Badge>
                )}
              </div>
            </div>
          </div>

          {showMenu && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" aria-label="User actions">
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {onSettings && (
                  <DropdownMenuItem onClick={onSettings}>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                )}
                {customMenuItems?.map((item, index) => (
                  <DropdownMenuItem
                    key={index}
                    onClick={item.onClick}
                    className={item.variant === "destructive" ? "text-destructive" : ""}
                  >
                    {item.icon && <span className="mr-2">{item.icon}</span>}
                    <span>{item.label}</span>
                  </DropdownMenuItem>
                ))}
                {onLogout && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem onClick={onLogout} className="text-destructive">
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Log out</span>
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>

        <Separator />

        {/* Details Section */}
        <div className="space-y-3 text-sm">
          {/* Roles */}
          {user?.roles && user.roles.length > 0 && (
            <div className="flex items-start gap-2">
              <Shield className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <p className="font-medium mb-1">Roles</p>
                <div className="flex flex-wrap gap-1">
                  {user.roles.map((role) => (
                    <Badge key={role} variant="outline" className="text-xs">
                      {role}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Groups */}
          {user?.groups && user.groups.length > 0 && (
            <div className="flex items-start gap-2">
              <Users className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <p className="font-medium mb-1">Groups</p>
                <div className="flex flex-wrap gap-1">
                  {user.groups.map((group) => (
                    <Badge key={group} variant="outline" className="text-xs">
                      {group}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Account Info */}
          <div className="space-y-2 pt-2">
            {user?.created_at && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-3 w-3" />
                <span className="text-xs">
                  Member since {formatDate(user.created_at)}
                </span>
              </div>
            )}
            
            {user?.last_login && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span className="text-xs">
                  Last login {formatDate(user.last_login)}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
);

UserDisplay.displayName = "UserDisplay";

/**
 * Simplified user avatar component for minimal display
 */
export const UserAvatar = React.forwardRef<
  HTMLDivElement,
  {
    size?: "sm" | "md" | "lg";
    avatarUrl?: string;
    className?: string;
  }
>(({ size = "md", avatarUrl, className }, ref) => {
  const { user } = useAgentCData();
  const { isInitialized } = useInitializationStatus();
  
  const sizeClasses = {
    sm: "h-6 w-6 text-xs",
    md: "h-8 w-8 text-sm",
    lg: "h-10 w-10 text-base",
  };
  
  const initials = React.useMemo(() => {
    if (!user) return "?";
    
    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }
    
    return user.user_name ? user.user_name.substring(0, 2).toUpperCase() : "?";
  }, [user]);
  
  if (!isInitialized || !user) {
    return (
      <div 
        ref={ref}
        className={cn(
          "rounded-full bg-muted animate-pulse",
          sizeClasses[size],
          className
        )}
        aria-hidden="true"
      />
    );
  }
  
  return (
    <Avatar ref={ref} className={cn(sizeClasses[size], className)}>
      {avatarUrl && <AvatarImage src={avatarUrl} alt={user.user_name} />}
      <AvatarFallback>{initials}</AvatarFallback>
    </Avatar>
  );
});

UserAvatar.displayName = "UserAvatar";

export { UserDisplay, userDisplayVariants };