# Form Context Providers Documentation

## Overview

The AutoDealGenie frontend implements two React context providers for managing form state with built-in Zod validation:

1. **FormProvider** - General purpose form state management
2. **CarFormProvider** - Car search form state management

Both providers implement session state management using React Context, eliminating the need for localStorage.

## FormProvider

### Purpose
Manages general form data (contact forms, feedback, etc.) with validation.

### Installation

```tsx
import { FormProvider, useForm } from '@/app/context';

// Wrap your component tree with the provider
function App() {
  return (
    <FormProvider>
      <YourComponents />
    </FormProvider>
  );
}
```

### Usage

```tsx
'use client';

import { useForm } from '@/app/context';

export function ContactForm() {
  const { state, updateField, submitForm } = useForm();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitForm(async (data) => {
      // Submit to API
      await apiClient.submitContact(data);
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={state.data.email || ''}
        onChange={(e) => updateField('email', e.target.value)}
      />
      {state.errors.email && <span>{state.errors.email}</span>}
      
      <input
        type="text"
        value={state.data.name || ''}
        onChange={(e) => updateField('name', e.target.value)}
      />
      {state.errors.name && <span>{state.errors.name}</span>}
      
      <textarea
        value={state.data.message || ''}
        onChange={(e) => updateField('message', e.target.value)}
      />
      {state.errors.message && <span>{state.errors.message}</span>}
      
      <button type="submit" disabled={state.isSubmitting}>
        {state.isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

### API Reference

#### State Properties
- `state.data: Partial<FormData>` - Current form data
- `state.errors: Record<string, string>` - Validation errors by field
- `state.isSubmitting: boolean` - Whether form is being submitted
- `state.isValid: boolean` - Whether form passed validation

#### Methods
- `updateField(field, value)` - Update a single field
- `validateField(field)` - Validate a single field, returns boolean
- `validateForm()` - Validate entire form, returns boolean
- `resetForm()` - Reset form to initial state
- `submitForm(onSubmit)` - Validate and submit form
- `setFormData(data)` - Set multiple fields at once

#### Validation Schema
```typescript
{
  email: string (valid email),
  name: string (1-255 chars),
  phone: string (optional),
  message: string (1-1000 chars)
}
```

## CarFormProvider

### Purpose
Manages car search form state with comprehensive validation matching backend schemas.

### Installation

```tsx
import { CarFormProvider, useCarForm } from '@/app/context';

// Wrap your component tree with the provider
function App() {
  return (
    <CarFormProvider>
      <YourComponents />
    </CarFormProvider>
  );
}
```

### Usage

```tsx
'use client';

import { useCarForm } from '@/app/context';
import { apiClient } from '@/lib/api';

export function CarSearchForm() {
  const { state, updateField, searchCars } = useCarForm();
  const [results, setResults] = useState(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    await searchCars(async (data) => {
      const response = await apiClient.searchCars(data);
      setResults(response);
    });
  };

  return (
    <form onSubmit={handleSearch}>
      <input
        type="text"
        placeholder="Make"
        value={state.data.make || ''}
        onChange={(e) => updateField('make', e.target.value)}
      />
      {state.errors.make && <span>{state.errors.make}</span>}
      
      <input
        type="number"
        placeholder="Min Budget"
        value={state.data.budget_min || ''}
        onChange={(e) => updateField('budget_min', Number(e.target.value))}
      />
      
      <input
        type="number"
        placeholder="Max Budget"
        value={state.data.budget_max || ''}
        onChange={(e) => updateField('budget_max', Number(e.target.value))}
      />
      {state.errors.budget_max && <span>{state.errors.budget_max}</span>}
      
      <select
        value={state.data.car_type || ''}
        onChange={(e) => updateField('car_type', e.target.value)}
      >
        <option value="">Select Type</option>
        <option value="sedan">Sedan</option>
        <option value="suv">SUV</option>
        <option value="truck">Truck</option>
        {/* ... more options */}
      </select>
      
      <button type="submit" disabled={state.isSearching}>
        {state.isSearching ? 'Searching...' : 'Search'}
      </button>
    </form>
  );
}
```

### API Reference

#### State Properties
- `state.data: Partial<CarSearchFormData>` - Current search criteria
- `state.errors: Record<string, string>` - Validation errors by field
- `state.isSearching: boolean` - Whether search is in progress
- `state.isValid: boolean` - Whether form passed validation

#### Methods
- `updateField(field, value)` - Update a single field
- `validateField(field)` - Validate a single field, returns boolean
- `validateForm()` - Validate entire form, returns boolean
- `resetForm()` - Reset form to initial state
- `searchCars(onSearch)` - Validate and execute search
- `setFormData(data)` - Set multiple fields at once
- `loadSavedSearch(data)` - Load saved search criteria

#### Validation Schema
```typescript
{
  make?: string (1-100 chars),
  model?: string (1-100 chars),
  budget_min?: number (>= 0),
  budget_max?: number (>= 0, must be > budget_min),
  car_type?: 'sedan' | 'suv' | 'truck' | 'coupe' | 'hatchback' | 'convertible' | 'wagon' | 'van' | 'other',
  year_min?: number (1900-2100),
  year_max?: number (1900-2100, must be >= year_min),
  mileage_max?: number (>= 0),
  fuel_type?: 'gasoline' | 'diesel' | 'electric' | 'hybrid' | 'plug_in_hybrid',
  transmission?: 'automatic' | 'manual' | 'cvt',
  user_priorities?: string (max 500 chars)
}
```

## Validation

Both providers use [Zod](https://github.com/colinhacks/zod) for schema validation, providing:

- **Type Safety** - Full TypeScript integration
- **Runtime Validation** - Catch errors before API calls
- **Custom Error Messages** - User-friendly validation feedback
- **Refine Rules** - Cross-field validation (e.g., max > min)

### Custom Validation Example

```tsx
import { z } from 'zod';

// Extend the schema with custom validation
const CustomFormSchema = FormSchema.extend({
  age: z.number().min(18, 'Must be 18 or older')
});
```

## Session State Management

Both providers use React Context to manage session state:

- **No localStorage** - All state in React Context
- **Component Scoped** - State isolated to provider tree
- **SSR Compatible** - Works with Next.js server components
- **Type Safe** - Full TypeScript support

### State Persistence

If you need to persist form state across page reloads, wrap the provider with your own persistence logic:

```tsx
function PersistedCarFormProvider({ children }: { children: ReactNode }) {
  const [initialData, setInitialData] = useState(null);

  useEffect(() => {
    // Load from session storage on mount
    const saved = sessionStorage.getItem('carSearchForm');
    if (saved) setInitialData(JSON.parse(saved));
  }, []);

  return (
    <CarFormProvider>
      <FormPersistence initialData={initialData} />
      {children}
    </CarFormProvider>
  );
}
```

## Best Practices

1. **Single Provider Per Form** - Don't nest same provider types
2. **Validate Early** - Use `validateField` on blur for better UX
3. **Clear Errors** - Errors clear automatically on field update
4. **Handle Submission Errors** - Wrap `submitForm` in try-catch
5. **Reset After Success** - Forms reset automatically after successful submit (except car search)

## Examples

### Complete Contact Form

```tsx
'use client';

import { useForm } from '@/app/context';
import { apiClient } from '@/lib/api';
import { useState } from 'react';

export function ContactForm() {
  const { state, updateField, validateField, submitForm } = useForm();
  const [success, setSuccess] = useState(false);

  const handleBlur = (field: keyof FormData) => {
    validateField(field);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await submitForm(async (data) => {
        await apiClient.submitContact(data);
      });
      setSuccess(true);
    } catch (error) {
      console.error('Submission failed:', error);
    }
  };

  if (success) {
    return <div>Thank you! We'll be in touch soon.</div>;
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={state.data.name || ''}
          onChange={(e) => updateField('name', e.target.value)}
          onBlur={() => handleBlur('name')}
        />
        {state.errors.name && (
          <span className="error">{state.errors.name}</span>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={state.data.email || ''}
          onChange={(e) => updateField('email', e.target.value)}
          onBlur={() => handleBlur('email')}
        />
        {state.errors.email && (
          <span className="error">{state.errors.email}</span>
        )}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          value={state.data.message || ''}
          onChange={(e) => updateField('message', e.target.value)}
          onBlur={() => handleBlur('message')}
        />
        {state.errors.message && (
          <span className="error">{state.errors.message}</span>
        )}
      </div>

      <button type="submit" disabled={state.isSubmitting}>
        {state.isSubmitting ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  );
}
```

### Complete Car Search Form

```tsx
'use client';

import { useCarForm } from '@/app/context';
import { apiClient } from '@/lib/api';
import { useState } from 'react';

export function CarSearchForm() {
  const { state, updateField, searchCars, loadSavedSearch } = useCarForm();
  const [results, setResults] = useState(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await searchCars(async (data) => {
        const response = await apiClient.searchCars(data);
        setResults(response);
      });
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const loadPreset = () => {
    loadSavedSearch({
      make: 'Toyota',
      car_type: 'sedan',
      budget_min: 20000,
      budget_max: 40000,
    });
  };

  return (
    <div>
      <form onSubmit={handleSearch}>
        <div>
          <input
            type="text"
            placeholder="Make (e.g., Toyota)"
            value={state.data.make || ''}
            onChange={(e) => updateField('make', e.target.value)}
          />
          {state.errors.make && <span>{state.errors.make}</span>}
        </div>

        <div>
          <input
            type="number"
            placeholder="Min Budget"
            value={state.data.budget_min || ''}
            onChange={(e) => updateField('budget_min', Number(e.target.value))}
          />
        </div>

        <div>
          <input
            type="number"
            placeholder="Max Budget"
            value={state.data.budget_max || ''}
            onChange={(e) => updateField('budget_max', Number(e.target.value))}
          />
          {state.errors.budget_max && <span>{state.errors.budget_max}</span>}
        </div>

        <button type="submit" disabled={state.isSearching}>
          {state.isSearching ? 'Searching...' : 'Search Cars'}
        </button>
        
        <button type="button" onClick={loadPreset}>
          Load Preset Search
        </button>
      </form>

      {results && (
        <div>
          <h2>Results</h2>
          {/* Display results */}
        </div>
      )}
    </div>
  );
}
```

## Migration from localStorage

If you previously used localStorage for form state:

**Before:**
```tsx
// ❌ Old approach with localStorage
const [formData, setFormData] = useState(() => {
  const saved = localStorage.getItem('formData');
  return saved ? JSON.parse(saved) : {};
});

useEffect(() => {
  localStorage.setItem('formData', JSON.stringify(formData));
}, [formData]);
```

**After:**
```tsx
// ✅ New approach with Context
import { useForm } from '@/app/context';

const { state, updateField } = useForm();
// State is automatically managed by context
// No need for localStorage or manual persistence
```

## TypeScript Support

All context providers are fully typed:

```typescript
import type {
  FormData,
  FormState,
  FormContextType,
  CarSearchFormData,
  CarFormState,
  CarFormContextType,
} from '@/app/context';

// Use types in your components
function MyComponent() {
  const form: FormContextType = useForm();
  const carForm: CarFormContextType = useCarForm();
  
  // TypeScript will enforce correct types
  form.updateField('email', 'test@example.com'); // ✅
  form.updateField('email', 123); // ❌ Type error
}
```

## Testing

Mock the context providers in tests:

```tsx
import { FormProvider } from '@/app/context';
import { render, screen } from '@testing-library/react';

test('renders contact form', () => {
  render(
    <FormProvider>
      <ContactForm />
    </FormProvider>
  );
  
  expect(screen.getByLabelText('Email')).toBeInTheDocument();
});
```

## Troubleshooting

### Error: "useForm must be used within a FormProvider"
**Solution:** Wrap your component tree with the provider:
```tsx
<FormProvider>
  <YourComponent />
</FormProvider>
```

### Validation not working
**Solution:** Ensure you're calling `validateField()` or `validateForm()` before accessing `state.isValid`

### Form not resetting
**Solution:** Call `resetForm()` explicitly, or use `submitForm()` which resets automatically on success

## Related Documentation

- [Zod Documentation](https://github.com/colinhacks/zod)
- [React Context API](https://react.dev/learn/passing-data-deeply-with-context)
- [Next.js Data Fetching](https://nextjs.org/docs/app/building-your-application/data-fetching)
- [Backend Schemas](../backend/app/schemas/user_preferences.py)
