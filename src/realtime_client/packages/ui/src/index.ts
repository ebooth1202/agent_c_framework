// Utility exports
export { cn } from './lib/utils';

// Core UI Components (CenSuite Design System)
// These are production-ready components following CenSuite patterns

// Alert
export { Alert, AlertTitle, AlertDescription } from './components/ui/alert';

// Avatar
export { Avatar, AvatarImage, AvatarFallback } from './components/ui/avatar';

// Badge
export { Badge } from './components/ui/badge';
export type { BadgeProps } from './components/ui/badge';

// Button
export { Button, buttonVariants } from './components/ui/button';
export type { ButtonProps } from './components/ui/button';

// Card
export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent 
} from './components/ui/card';

// Dropdown Menu
export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup,
} from './components/ui/dropdown-menu';

// Form
export {
  useFormField,
  Form,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
  FormField,
} from './components/ui/form';

// Input
export { Input } from './components/ui/input';
export type { InputProps } from './components/ui/input';

// Label
export { Label } from './components/ui/label';

// ScrollArea
export { ScrollArea, ScrollBar } from './components/ui/scroll-area';

// Select
export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
} from './components/ui/select';

// Separator
export { Separator } from './components/ui/separator';

// Sheet
export {
  Sheet,
  SheetPortal,
  SheetOverlay,
  SheetTrigger,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetFooter,
  SheetTitle,
  SheetDescription,
} from './components/ui/sheet';

// Skeleton
export { Skeleton } from './components/ui/skeleton';

// Tabs
export { Tabs, TabsList, TabsTrigger, TabsContent } from './components/ui/tabs';

// Textarea
export { Textarea } from './components/ui/textarea';
export type { TextareaProps } from './components/ui/textarea';

// Toggle Group
export { ToggleGroup, ToggleGroupItem } from './components/ui/toggle-group';

// Tooltip
export {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
  TooltipProvider,
} from './components/ui/tooltip';

// Toast/Sonner
export { Toaster } from './components/ui/sonner';

// Editor component exports (legacy - use input/MarkdownEditor instead)
export { MarkdownEditor as LegacyMarkdownEditor } from './components/editor';
export type { MarkdownEditorProps as LegacyMarkdownEditorProps } from './components/editor';

// Input component exports
export { 
  // Main integrated component
  InputArea,
  // Individual components
  InputContainer, 
  RichTextEditor,
  MarkdownEditor,
  InputToolbar,
  MicrophoneButton,
  // Temporarily rename the old ones to avoid conflicts
  AgentSelector as LegacyAgentSelector
  // Note: OutputSelector has been removed from input components
  // Use the fixed OutputSelector from controls instead
} from './components/input';

export type { 
  InputAreaProps,
  InputContainerProps, 
  RichTextEditorProps,
  MarkdownEditorProps,
  InputToolbarProps,
  MicrophoneButtonProps,
  // Rename old types too
  AgentSelectorProps as LegacyAgentSelectorProps,
  // OutputSelectorProps removed - use controls/OutputSelector
  Agent,
  OutputMode,
  OutputOption
} from './components/input';

// Control component exports - Include the new selectors here
export {
  ConnectionButton,
  AudioControls,
  AgentSelector,
  OutputSelector
} from './components/controls';

export type {
  ConnectionButtonProps,
  AudioControlsProps,
  AgentSelectorProps,
  OutputSelectorProps
} from './components/controls';