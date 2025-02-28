import * as React from "react";
import * as SwitchPrimitives from "@radix-ui/react-switch";
import { cn } from "@/lib/utils";

/**
 * Switch component that provides a toggle control.
 * Based on the Radix UI Switch primitive with custom styling.
 *
 * @component
 * @example
 * ```jsx
 * <Switch
 *   checked={isEnabled}
 *   onCheckedChange={setIsEnabled}
 *   aria-label="Enable feature"
 * />
 * ```
 */
const Switch = React.forwardRef(({ className, ...props }, ref) => (
  <SwitchPrimitives.Root
    className={cn(
      "peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 focus-visible:ring-offset-white disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-blue-500 data-[state=unchecked]:bg-gray-200 dark:focus-visible:ring-blue-500 dark:focus-visible:ring-offset-gray-900 dark:data-[state=checked]:bg-blue-600 dark:data-[state=unchecked]:bg-gray-700",
      className
    )}
    {...props}
    ref={ref}
  >
    <SwitchPrimitives.Thumb
      className={cn(
        "pointer-events-none block h-4 w-4 rounded-full bg-white shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0"
      )}
    />
  </SwitchPrimitives.Root>
));

Switch.displayName = SwitchPrimitives.Root.displayName;

export { Switch };