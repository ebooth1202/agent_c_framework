# Night Sky Color Palette Implementation

## Color Palette

| Color Name  | Hex Code | RGB Value       | HSL Value        | Usage                            |
|-------------|----------|-----------------|------------------|---------------------------------|
| Port Gore   | #1d213e  | rgb(29, 33, 62) | hsl(240, 35%, 18%) | Background, darkest elements    |
| Martinique  | #2a2e51  | rgb(42, 46, 81) | hsl(242, 32%, 24%) | Card backgrounds, popovers      |
| Fiord       | #3d406b  | rgb(61, 64, 107)| hsl(245, 28%, 33%) | Secondary elements, muted areas  |
| East Bay    | #4e4e83  | rgb(78, 78, 131)| hsl(242, 26%, 41%) | Accent colors, highlights       |
| Mid Gray    | #606271  | rgb(96, 98, 113)| hsl(240, 8%, 52%)  | Borders, subtle UI elements     |

## Variable Mapping

The Night Sky palette has been implemented in the dark theme using the following variable mappings:

### Primary Theme Variables

```css
--background: 240 35% 18%;      /* Port Gore #1d213e */
--foreground: 0 0% 100%;        /* White */

--card: 242 32% 24%;           /* Martinique #2a2e51 */
--card-foreground: 0 0% 100%;   /* White */

--popover: 242 32% 24%;        /* Martinique #2a2e51 */
--popover-foreground: 0 0% 100%; /* White */

--secondary: 245 28% 33%;      /* Fiord #3d406b */
--muted: 245 28% 33%;          /* Fiord #3d406b */

--accent: 242 26% 41%;         /* East Bay #4e4e83 */

--border: 240 8% 52%;          /* Mid Gray #606271 */
--input: 245 28% 33%;          /* Fiord #3d406b */
--ring: 242 26% 41%;           /* East Bay #4e4e83 */
```

### Sidebar Variables

```css
--sidebar-background: 240 35% 18%;     /* Port Gore #1d213e */
--sidebar-accent: 242 26% 41%;         /* East Bay #4e4e83 */
--sidebar-border: 240 8% 52%;          /* Mid Gray #606271 */
```

### State Colors

State colors have been adjusted to complement the Night Sky palette:

```css
--success-background: hsl(142, 40%, 20%);   /* Darker green */
--warning-background: hsl(30, 30%, 25%);    /* Darker amber */
--info-background: hsl(242, 32%, 24%);      /* Martinique #2a2e51 */
```

## Notes

1. The primary blue color was kept consistent for brand identity and to maintain visual hierarchy
2. All colors were chosen to maintain sufficient contrast for accessibility
3. Text colors were kept light (white or near-white) for maximum readability against the darker backgrounds
4. The Night Sky palette offers a sophisticated, deep color scheme that reduces eye strain in dark mode
5. Chat message bubbles (assistant, user, system, thought, media) retain their distinct color identities while complementing the new Night Sky theme