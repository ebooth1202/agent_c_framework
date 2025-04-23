# CSS explorer tool
Large CSS files are a royal pain to work with for agents.  We need to streamline that, at least somewhat.  We don't really need to go full CSS parser to support any variant of CSS file, we can focus on how WE do it and worry about other cases later.

Our component CSS file looks like this:

```css
/* component-styles.css */
/* This file contains extracted styles from inline styling */

/* 
 * COMPONENT STYLES
 * ----------------
 * This file contains CSS classes extracted from inline styling.
 * Follow these conventions:
 * 1. Use descriptive class names with component prefixes
 * 2. Group styles by component
 * 3. Include comments for each component section
 * 4. Use CSS variables for themable properties
 */

/* ==============================
   Layout Component Styles
   ============================== */

/* Main layout container */
.layout-container {
  min-height: 100vh; /* min-h-screen */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-image: linear-gradient(to bottom, var(--layout-gradient-from), var(--layout-gradient-to));
}

/* Light mode gradient colors */
:root {
  --layout-gradient-from: #f9fafb; /* from-gray-50 */
  --layout-gradient-to: #f3f4f6; /* to-gray-100 */
}

/* Dark mode gradient colors */
.dark {
  --layout-gradient-from: #111827; /* from-gray-900 */
  --layout-gradient-to: #1f2937; /* to-gray-800 */
}

/* ==============================
   ThoughtDisplay Component Styles
   ============================== */

/* Thought container styles */
.thought-container {
  position: relative;
  max-width: 80%;
  border-radius: 1rem;
  padding: 0.75rem 1rem;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  background-color: #fffbeb; /* bg-amber-50 */
  color: rgba(180, 83, 9, 0.8); /* text-amber-700/80 */
  border: 1px solid #fde68a; /* border-amber-200 */
  border-bottom-left-radius: 0.125rem; /* rounded-bl-sm */
}

/* Dark theme container styles */
.dark .thought-container {
  background-color: rgba(55, 65, 81, 0.7); /* bg-gray-700/70 */
  color: rgba(252, 211, 77, 0.8); /* text-amber-200/80 */
  border-color: #92400e; /* border-amber-800 */
}
```
Because of this consistency we can locate groups of styles for each component, the individual style for that component, along with descriptions. We can use that to give the model an overview of what's in the file using FAR fewer tokens. 

If we provide the start and end line numbers including the comments the agent could read in the lines using the workspace tool and skip the rest of the file.  Heck, what would be SUPER awesome is if we could give it a way to rewrite a style by name within that file and just have us load the file find the body, replace it and save...

This shares a lot of similarity with how the XML explorer works at least in terms of using the workspace tool to do the heavy lifting.

