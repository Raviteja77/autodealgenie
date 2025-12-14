# UI Components Documentation

## Overview

AutoDealGenie's frontend includes a comprehensive library of reusable UI components built with Tailwind CSS and TypeScript. All components are designed following React and Next.js 14 best practices.

## Table of Contents

- [Installation](#installation)
- [Components](#components)
  - [ErrorBoundary](#errorboundary)
  - [Button](#button)
  - [Input](#input)
  - [Card](#card)
  - [Modal](#modal)
  - [Spinner](#spinner)
- [Error Handling](#error-handling)
- [Custom Hooks](#custom-hooks)
- [Best Practices](#best-practices)

## Installation

All components are available through the centralized export:

```tsx
import { Button, Input, Card, Modal, Spinner, ErrorBoundary } from '@/components';
```

## Components

### ErrorBoundary

React Error Boundary component to catch and handle errors gracefully.

**Features:**
- Catches JavaScript errors anywhere in the child component tree
- Logs errors in development
- Displays fallback UI
- Supports custom fallback components
- Optional error callback handler

**Usage:**

```tsx
import { ErrorBoundary } from '@/components';

// Basic usage
<ErrorBoundary>
  <YourComponent />
</ErrorBoundary>

// With custom fallback
<ErrorBoundary fallback={<CustomErrorUI />}>
  <YourComponent />
</ErrorBoundary>

// With error handler
<ErrorBoundary onError={(error, errorInfo) => {
  // Log to error tracking service
  logErrorToService(error, errorInfo);
}}>
  <YourComponent />
</ErrorBoundary>
```

**Props:**
- `children: ReactNode` - Child components to wrap
- `fallback?: ReactNode` - Custom fallback UI
- `onError?: (error: Error, errorInfo: ErrorInfo) => void` - Error callback

### Button

Reusable button component with multiple variants and sizes.

**Features:**
- 5 variants: primary, secondary, danger, success, outline
- 3 sizes: sm, md, lg
- Loading state with spinner
- Left/right icon support
- Full width option
- Fully accessible

**Usage:**

```tsx
import { Button } from '@/components';

// Basic button
<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>

// Loading state
<Button variant="danger" isLoading>
  Deleting...
</Button>

// With icons
<Button 
  leftIcon={<TrashIcon />}
  variant="danger"
  onClick={handleDelete}
>
  Delete
</Button>

// Full width
<Button fullWidth variant="primary">
  Submit
</Button>
```

**Props:**
- `variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'outline'` - Button style (default: 'primary')
- `size?: 'sm' | 'md' | 'lg'` - Button size (default: 'md')
- `isLoading?: boolean` - Show loading spinner (default: false)
- `leftIcon?: ReactNode` - Icon before text
- `rightIcon?: ReactNode` - Icon after text
- `fullWidth?: boolean` - Full width button (default: false)
- All standard button HTML attributes

### Input

Form input component with label, error, and helper text support.

**Features:**
- Label support
- Error state with error message
- Helper text
- Left/right icon support
- Full width option
- Accessible with proper ARIA attributes

**Usage:**

```tsx
import { Input } from '@/components';

// Basic input
<Input
  label="Email"
  type="email"
  placeholder="Enter your email"
/>

// With error
<Input
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={errors.email}
/>

// With helper text
<Input
  label="Password"
  type="password"
  helperText="Must be at least 8 characters"
/>

// With icon
<Input
  label="Search"
  type="text"
  leftIcon={<SearchIcon />}
/>

// Full width
<Input
  label="Email"
  type="email"
  fullWidth
/>
```

**Props:**
- `label?: string` - Input label
- `error?: string` - Error message
- `helperText?: string` - Helper text below input
- `leftIcon?: ReactNode` - Icon on the left
- `rightIcon?: ReactNode` - Icon on the right
- `fullWidth?: boolean` - Full width input (default: false)
- All standard input HTML attributes

### Card

Container component for content with header, body, and footer sections.

**Features:**
- Configurable padding
- Configurable shadow
- Hover effect option
- Compound components (Header, Body, Footer)
- Responsive design

**Usage:**

```tsx
import { Card } from '@/components';

// Basic card
<Card padding="md" shadow="md">
  <p>Card content</p>
</Card>

// With sections
<Card padding="md" shadow="md" hover>
  <Card.Header>
    <h2 className="text-xl font-semibold">Card Title</h2>
  </Card.Header>
  <Card.Body>
    <p>Main content goes here</p>
  </Card.Body>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>

// No padding (for images)
<Card padding="none" shadow="lg">
  <img src="..." alt="..." />
  <div className="p-4">
    <h3>Title</h3>
    <p>Description</p>
  </div>
</Card>
```

**Props:**
- `padding?: 'none' | 'sm' | 'md' | 'lg'` - Card padding (default: 'md')
- `shadow?: 'none' | 'sm' | 'md' | 'lg'` - Card shadow (default: 'md')
- `hover?: boolean` - Hover effect (default: false)
- All standard div HTML attributes

### Modal

Modal dialog component with overlay.

**Features:**
- Configurable size
- Close on overlay click (optional)
- Close button (optional)
- Keyboard support (ESC to close)
- Body scroll lock when open
- Accessible with ARIA attributes

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
        <p>Are you sure you want to continue?</p>
        <div className="flex justify-end gap-2 mt-4">
          <Button variant="outline" onClick={() => setIsOpen(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleConfirm}>
            Confirm
          </Button>
        </div>
      </Modal>
    </>
  );
}
```

**Props:**
- `isOpen: boolean` - Modal open state
- `onClose: () => void` - Close callback
- `title?: string` - Modal title
- `size?: 'sm' | 'md' | 'lg' | 'xl'` - Modal size (default: 'md')
- `closeOnOverlayClick?: boolean` - Close on overlay click (default: true)
- `showCloseButton?: boolean` - Show close button (default: true)

### Spinner

Loading spinner component.

**Features:**
- 3 sizes: sm, md, lg
- 3 colors: primary, secondary, white
- Full screen option
- Optional loading text

**Usage:**

```tsx
import { Spinner } from '@/components';

// Inline spinner
<Spinner size="sm" color="primary" />

// Full screen loading
<Spinner fullScreen text="Loading..." />

// In button
<Button disabled>
  <Spinner size="sm" color="white" />
  <span className="ml-2">Loading...</span>
</Button>
```

**Props:**
- `size?: 'sm' | 'md' | 'lg'` - Spinner size (default: 'md')
- `color?: 'primary' | 'secondary' | 'white'` - Spinner color (default: 'primary')
- `fullScreen?: boolean` - Full screen overlay (default: false)
- `text?: string` - Optional loading text

## Error Handling

### Structured Error Classes

The application uses structured error classes for better error handling:

```tsx
import {
  ApiError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  ValidationError,
  ServerError,
  NetworkError,
  isApiError,
  isValidationError,
  getUserFriendlyErrorMessage,
} from '@/lib/errors';
```

**Error Classes:**
- `ApiError` - Base API error (custom status code)
- `AuthenticationError` - 401 Unauthorized
- `AuthorizationError` - 403 Forbidden
- `NotFoundError` - 404 Not Found
- `ValidationError` - 422 Validation Error
- `ServerError` - 500 Server Error
- `NetworkError` - Network/Connection Error

**Usage:**

```tsx
import { apiClient } from '@/lib/api';
import { isValidationError, getUserFriendlyErrorMessage } from '@/lib/errors';

try {
  const data = await apiClient.getDeals();
} catch (error) {
  if (isValidationError(error)) {
    // Handle validation errors
    console.log(error.validationErrors);
  }
  
  // Get user-friendly message
  const message = getUserFriendlyErrorMessage(error);
  alert(message);
}
```

## Custom Hooks

### useApi

Hook for handling API requests with loading and error states.

```tsx
import { useApi } from '@/lib/hooks';
import { apiClient } from '@/lib/api';

function MyComponent() {
  const { data, isLoading, error, execute } = useApi({
    onSuccess: (data) => console.log('Success!', data),
    onError: (error) => console.error('Error:', error),
  });

  const handleFetch = async () => {
    await execute(() => apiClient.getDeals());
  };

  if (isLoading) return <Spinner />;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>{/* Render data */}</div>;
}
```

### useDebounce

Hook to debounce a value (useful for search inputs).

```tsx
import { useState, useEffect } from 'react';
import { useDebounce } from '@/lib/hooks';

function SearchComponent() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, { delay: 500 });

  useEffect(() => {
    if (debouncedSearchTerm) {
      // Perform search
      searchApi(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  return (
    <Input
      value={searchTerm}
      onChange={(e) => setSearchTerm(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

### useLocalStorage

Hook for localStorage with TypeScript support.

```tsx
import { useLocalStorage } from '@/lib/hooks';

function PreferencesComponent() {
  const [preferences, setPreferences, removePreferences] = useLocalStorage(
    'user-preferences',
    { theme: 'light', language: 'en' }
  );

  return (
    <div>
      <Button onClick={() => setPreferences({ ...preferences, theme: 'dark' })}>
        Toggle Theme
      </Button>
      <Button onClick={removePreferences}>
        Reset Preferences
      </Button>
    </div>
  );
}
```

### useOnlineStatus

Hook to track browser online/offline status.

```tsx
import { useOnlineStatus } from '@/lib/hooks';

function AppHeader() {
  const isOnline = useOnlineStatus();

  return (
    <div>
      {!isOnline && (
        <div className="bg-yellow-100 p-2 text-center">
          You are currently offline
        </div>
      )}
    </div>
  );
}
```

## Best Practices

### Component Usage

1. **Always use TypeScript** - All components are fully typed
2. **Use semantic HTML** - Components render semantic HTML elements
3. **Accessibility** - All components include proper ARIA attributes
4. **Responsive design** - Components work on all screen sizes
5. **Error boundaries** - Wrap components in ErrorBoundary for resilience

### Error Handling

1. **Use structured errors** - Import error classes from `@/lib/errors`
2. **User-friendly messages** - Use `getUserFriendlyErrorMessage()`
3. **Type guards** - Use `isApiError()`, `isValidationError()`, etc.
4. **Centralized handling** - Handle errors in API client

### State Management

1. **Use custom hooks** - Leverage `useApi`, `useDebounce`, etc.
2. **Context providers** - Use FormProvider and CarFormProvider
3. **Local storage** - Use `useLocalStorage` hook for persistence

### Styling

1. **Tailwind CSS** - All components use Tailwind classes
2. **Customization** - Pass `className` prop to extend styles
3. **Consistent spacing** - Use Tailwind spacing scale
4. **Dark mode ready** - Components support dark mode (when enabled)

## Examples

### Complete Form with Error Handling

```tsx
'use client';

import { useState } from 'react';
import { Button, Input, Card } from '@/components';
import { useApi } from '@/lib/hooks';
import { apiClient } from '@/lib/api';
import { getUserFriendlyErrorMessage } from '@/lib/errors';

export function ContactForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
  });
  
  const { isLoading, error, execute } = useApi({
    onSuccess: () => {
      alert('Message sent successfully!');
      setFormData({ name: '', email: '', message: '' });
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await execute(() => apiClient.submitContact(formData));
  };

  return (
    <Card padding="lg" shadow="md">
      <Card.Header>
        <h2 className="text-2xl font-bold">Contact Us</h2>
      </Card.Header>
      <Card.Body>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Name"
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            fullWidth
            required
          />
          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            fullWidth
            required
          />
          <div>
            <label className="block text-sm font-medium mb-1">Message</label>
            <textarea
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              className="w-full p-3 border rounded-lg"
              rows={4}
              required
            />
          </div>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 p-3 rounded-lg">
              {getUserFriendlyErrorMessage(error)}
            </div>
          )}
          <Button
            type="submit"
            variant="primary"
            fullWidth
            isLoading={isLoading}
          >
            Send Message
          </Button>
        </form>
      </Card.Body>
    </Card>
  );
}
```

## Testing

Components can be tested using React Testing Library:

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    fireEvent.click(screen.getByText('Click Me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button isLoading>Click Me</Button>);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
```

## Support

For issues or questions:
- Check the [main README](../README.md)
- Review the [Authentication documentation](../AUTHENTICATION.md)
- See [Form Context Providers](../FORM_CONTEXT_PROVIDERS.md)
