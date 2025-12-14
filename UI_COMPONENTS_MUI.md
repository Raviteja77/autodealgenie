# UI Components Documentation - Material-UI Version

## Overview

AutoDealGenie's frontend now uses Material-UI (MUI) components with Emotion for styling. All components are fully typed with TypeScript and follow Material Design principles.

## Table of Contents

- [Installation](#installation)
- [Theme Configuration](#theme-configuration)
- [Components](#components)
  - [ErrorBoundary](#errorboundary)
  - [Button](#button)
  - [Input](#input)
  - [Card](#card)
  - [Modal](#modal)
  - [Spinner](#spinner)
- [Dashboard Pages](#dashboard-pages)
- [Best Practices](#best-practices)

## Installation

### Dependencies

```json
{
  "@mui/material": "^5.15.0",
  "@mui/icons-material": "^5.15.0",
  "@emotion/react": "^11.11.0",
  "@emotion/styled": "^11.11.0",
  "@mui/x-data-grid": "^6.18.0",
  "@mui/x-date-pickers": "^6.18.0",
  "date-fns": "^3.0.0"
}
```

### Usage

All components are available through the centralized export:

```tsx
import { Button, Input, Card, Modal, Spinner, ErrorBoundary } from '@/components';
```

## Theme Configuration

The application uses a custom MUI theme defined in `frontend/lib/theme/theme.ts`:

### Color Palette

- **Primary**: Blue-600 (#2563eb)
- **Secondary**: Gray-600 (#4b5563)
- **Error**: Red-600 (#dc2626)
- **Warning**: Yellow-500 (#f59e0b)
- **Success**: Green-600 (#16a34a)
- **Background**: Gray-50 (#f9fafb)

### Typography

- Font Family: Geist Sans (with system font fallbacks)
- Headings: h1-h6 with appropriate sizes and weights
- Body text: Consistent sizing and line heights

### Theme Provider

Wrap your app with the ThemeProvider:

```tsx
import { ThemeProvider } from '@/lib/theme/ThemeProvider';

<ThemeProvider>
  <YourApp />
</ThemeProvider>
```

## Components

### ErrorBoundary

React Error Boundary component using MUI components for error display.

**Features:**
- MUI Card for error container
- Error icon from MUI icons
- Styled with Material Design
- Development mode error details

**Usage:**

```tsx
import { ErrorBoundary } from '@/components';

<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>
```

### Button

MUI Button component with custom variant mapping and loading states.

**Features:**
- 5 variants mapped to MUI colors
- 3 sizes (small, medium, large)
- Loading state with CircularProgress
- Icon support (start and end icons)
- Full width option

**Usage:**

```tsx
import { Button } from '@/components';
import SearchIcon from '@mui/icons-material/Search';

<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>

<Button 
  variant="danger" 
  isLoading 
  leftIcon={<SearchIcon />}
>
  Loading...
</Button>
```

**Props:**
- `variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'outline'`
- `size?: 'sm' | 'md' | 'lg'`
- `isLoading?: boolean`
- `leftIcon?: ReactNode`
- `rightIcon?: ReactNode`
- `fullWidth?: boolean`
- All MUI Button props

### Input

MUI TextField component with enhanced features.

**Features:**
- Label support
- Error state with helper text
- Input adornments (left/right icons)
- Full MUI TextField capabilities

**Usage:**

```tsx
import { Input } from '@/components';
import SearchIcon from '@mui/icons-material/Search';

<Input
  label="Email"
  type="email"
  placeholder="Enter your email"
  error={errors.email}
  helperText="We'll never share your email"
/>

<Input
  label="Search"
  leftIcon={<SearchIcon />}
  fullWidth
/>
```

**Props:**
- `label?: string`
- `error?: string`
- `helperText?: string`
- `leftIcon?: ReactNode`
- `rightIcon?: ReactNode`
- `fullWidth?: boolean`
- All MUI TextField props

### Card

MUI Card component with compound components.

**Features:**
- Configurable shadow levels
- Hover effect option
- Compound components (Header, Body, Footer)
- MUI CardContent, CardHeader, CardActions

**Usage:**

```tsx
import { Card } from '@/components';

<Card shadow="md" hover>
  <Card.Header>
    <Typography variant="h5">Card Title</Typography>
  </Card.Header>
  <Card.Body>
    <Typography>Main content goes here</Typography>
  </Card.Body>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```

**Props:**
- `shadow?: 'none' | 'sm' | 'md' | 'lg'`
- `hover?: boolean`
- All MUI Card props

### Modal

MUI Dialog component with custom close handling.

**Features:**
- MUI Dialog with full features
- Custom close button in title
- Configurable overlay click behavior
- Keyboard support (ESC to close)
- Size options

**Usage:**

```tsx
import { Modal } from '@/components';
import { useState } from 'react';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>Open Modal</Button>
      
      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Confirm Action"
        size="md"
      >
        <Typography>Are you sure you want to continue?</Typography>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mt: 2 }}>
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button variant="primary">Confirm</Button>
        </Box>
      </Modal>
    </>
  );
}
```

**Props:**
- `isOpen: boolean`
- `onClose: () => void`
- `title?: string`
- `size?: 'sm' | 'md' | 'lg' | 'xl'`
- `closeOnOverlayClick?: boolean`
- `showCloseButton?: boolean`

### Spinner

MUI CircularProgress component with optional backdrop.

**Features:**
- 3 sizes (20px, 40px, 60px)
- Color options matching theme
- Full screen backdrop option
- Optional loading text

**Usage:**

```tsx
import { Spinner } from '@/components';

// Inline spinner
<Spinner size="sm" color="primary" />

// Full screen loading
<Spinner fullScreen text="Loading..." />
```

**Props:**
- `size?: 'sm' | 'md' | 'lg'`
- `color?: 'primary' | 'secondary' | 'white'`
- `fullScreen?: boolean`
- `text?: string`

## Dashboard Pages

### Main Dashboard (/dashboard)

Features:
- Hero section with search button
- Quick action cards (Search, Deals, Favorites)
- Statistics overview (Active Deals, Saved Searches, etc.)
- Platform features grid

### Search Page (/dashboard/search)

Advanced car search interface:
- Make and Model inputs
- Car Type, Fuel Type, Transmission selectors
- Year range slider (2000-2024)
- Budget slider ($5K-$100K)
- Mileage slider (10K-200K miles)
- Popular search presets
- Reset and Search buttons

### Results Page (/dashboard/results)

Vehicle listing interface:
- Grid layout with vehicle cards
- Vehicle images and details
- Favorite/unfavorite functionality
- Price, mileage, fuel type, location
- Features chips
- View Details and Contact Dealer buttons
- Active filters display
- Mock data generation for demonstration

## MUI Features

### Grid System

```tsx
import Grid from '@mui/material/Grid';

<Grid container spacing={3}>
  <Grid item xs={12} md={6} lg={4}>
    <Card>Content</Card>
  </Grid>
</Grid>
```

### Icons

```tsx
import SearchIcon from '@mui/icons-material/Search';
import DirectionsCarIcon from '@mui/icons-material/DirectionsCar';

<Button leftIcon={<SearchIcon />}>Search</Button>
```

### Box Component

```tsx
import Box from '@mui/material/Box';

<Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
  <Typography>Content</Typography>
</Box>
```

### Typography

```tsx
import Typography from '@mui/material/Typography';

<Typography variant="h3" gutterBottom fontWeight={700}>
  Title
</Typography>
<Typography variant="body1" color="text.secondary">
  Description
</Typography>
```

## Best Practices

### 1. Use sx Prop for Styling

```tsx
<Box sx={{ 
  display: 'flex', 
  gap: 2, 
  alignItems: 'center',
  bgcolor: 'background.paper',
  p: 2 
}}>
  Content
</Box>
```

### 2. Theme Colors

Use theme colors instead of hardcoded values:

```tsx
<Typography color="primary">Primary Text</Typography>
<Typography color="text.secondary">Secondary Text</Typography>
<Box sx={{ bgcolor: 'error.light' }}>Error Background</Box>
```

### 3. Responsive Design

```tsx
<Grid item xs={12} sm={6} md={4} lg={3}>
  Responsive content
</Grid>
```

### 4. Icons from MUI

Always use MUI icons for consistency:

```tsx
import SearchIcon from '@mui/icons-material/Search';
import CloseIcon from '@mui/icons-material/Close';
```

### 5. Spacing with Theme

```tsx
<Box sx={{ p: 2, m: 1, mt: 3, mb: 4 }}>
  // p = padding, m = margin (in theme spacing units)
</Box>
```

## Migration from Tailwind

### Before (Tailwind):
```tsx
<div className="bg-blue-600 text-white px-4 py-2 rounded">
  Button
</div>
```

### After (MUI):
```tsx
<Button variant="primary">
  Button
</Button>
```

or with custom styling:

```tsx
<Box sx={{ bgcolor: 'primary.main', color: 'white', px: 2, py: 1, borderRadius: 1 }}>
  Content
</Box>
```

## TypeScript Support

All components are fully typed:

```typescript
import { Button, Card, Input } from '@/components';
import type { ButtonVariant, ButtonSize } from '@/components';

const variant: ButtonVariant = 'primary';
const size: ButtonSize = 'md';
```

## Performance Tips

1. **Code Splitting**: MUI components are automatically tree-shaken
2. **Theme Caching**: Theme is created once and reused
3. **sx Prop**: More performant than styled components for simple styles
4. **Icon Imports**: Import only icons you need

## Related Documentation

- [Material-UI Documentation](https://mui.com/material-ui/getting-started/)
- [Emotion Documentation](https://emotion.sh/docs/introduction)
- [MUI Icons](https://mui.com/material-ui/material-icons/)
- [MUI System](https://mui.com/system/getting-started/)
