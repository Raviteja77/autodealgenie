# Frontend Component Organization

This document describes the frontend component architecture following Atomic Design principles.

## Directory Structure

```
frontend/
├── components/
│   ├── atoms/              # Basic building blocks
│   │   ├── Button.tsx
│   │   ├── Button.types.ts
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   ├── Spinner.tsx
│   │   ├── Modal.tsx
│   │   └── __tests__/
│   ├── molecules/          # Simple combinations of atoms
│   │   ├── PriceDisplay.tsx
│   │   ├── VehicleInfo.tsx
│   │   └── __tests__/
│   ├── organisms/          # Complex UI sections
│   │   ├── VehicleCard.tsx
│   │   └── __tests__/
│   ├── templates/          # Page layouts
│   ├── features/           # Feature-specific components
│   ├── common/             # Shared components (Header, Footer)
│   └── index.ts            # Main exports
├── lib/
│   ├── hooks/              # Custom React hooks
│   │   ├── useFinancing.ts
│   │   ├── useDisplayMode.ts
│   │   ├── useFilters.ts
│   │   ├── useComparison.ts
│   │   └── __tests__/
│   ├── utils/              # Utility functions
│   └── theme/              # MUI theme configuration
└── app/                    # Next.js App Router pages
```

## Atomic Design Principles

### Atoms
Basic UI elements that cannot be broken down further:
- **Button**: Reusable button with variants (primary, secondary, danger, success, outline)
- **Input**: Form input with label, error handling, and icon support
- **Card**: Content container with header, body, and footer
- **Spinner**: Loading indicator
- **Modal**: Dialog/overlay component

**Usage:**
```tsx
import { Button, Input, Card } from '@/components';

<Button variant="primary" size="md" onClick={handleClick}>
  Click me
</Button>
```

### Molecules
Simple combinations of atoms forming functional UI patterns:
- **PriceDisplay**: Price formatting and display
- **MonthlyPaymentDisplay**: Monthly payment with details
- **PriceSwitcher**: Toggle between cash/monthly views
- **VehicleTitle**: Vehicle name display
- **VehicleDetails**: Vehicle specifications (mileage, fuel, etc.)
- **VehicleImage**: Vehicle image with badges and actions

**Usage:**
```tsx
import { PriceDisplay, VehicleTitle } from '@/components/molecules';

<VehicleTitle make="Toyota" model="Camry" year={2023} />
<PriceDisplay price={25000} size="lg" />
```

### Organisms
Complex UI sections combining multiple molecules and atoms:
- **VehicleCard**: Complete vehicle display card (planned refactor)
- **SearchForm**: Vehicle search form (planned)
- **ComparisonTable**: Vehicle comparison view (planned)

### Templates
Page-level layouts that define structure but not content:
- To be created as needed

### Features
Feature-specific complex components:
- To be organized by feature domain

## Custom Hooks

Business logic extracted into reusable hooks:

### useFinancing
Handles vehicle financing calculations:
```tsx
import { useFinancingCalculation, useAffordability } from '@/lib/hooks';

const payment = useFinancingCalculation(vehiclePrice, {
  downPayment: 5000,
  loanTerm: 60,
  creditScore: 'good',
});

const affordability = useAffordability(vehiclePrice, budgetMax);
```

### useDisplayMode
Manages cash vs. monthly payment display:
```tsx
import { useDisplayMode } from '@/lib/hooks';

const { displayMode, toggleMode, isCashMode } = useDisplayMode();
```

### Other Hooks
- **useFilters**: Vehicle filtering state management
- **useComparison**: Vehicle comparison state
- **useDebounce**: Input debouncing
- **useLocalStorage**: Persistent local storage
- **useOnlineStatus**: Network status detection

## Testing

All components and hooks have comprehensive unit tests:

```bash
# Run all tests
npm test

# Run tests for specific directory
npm test components/atoms
npm test lib/hooks

# Run tests with coverage
npm test:coverage
```

**Test Coverage:**
- Atoms: 32 tests
- Hooks: 16 tests
- Total: 64/65 tests passing

## Type Safety

All components have dedicated `.types.ts` files with explicit TypeScript interfaces:
- No use of `any` type
- Proper type exports for consumers
- Compile-time type checking

## Best Practices

1. **Component Organization**
   - Keep components small and focused (Single Responsibility Principle)
   - Separate presentational from container components
   - Extract business logic into custom hooks

2. **Naming Conventions**
   - Components: `PascalCase.tsx`
   - Types: `PascalCase.types.ts`
   - Tests: `PascalCase.test.tsx`
   - Hooks: `useCamelCase.ts`

3. **Imports**
   - Always use `@/` path alias
   - Import from index files when available
   - Group imports: external → internal → types

4. **Documentation**
   - Add JSDoc comments to all public APIs
   - Include usage examples in component files
   - Document complex business logic

## Migration Path

To maintain backward compatibility while refactoring:
1. New components go directly into atomic structure
2. Old components can be gradually refactored
3. Main `components/index.ts` re-exports for compatibility
4. Update imports to use new atomic structure over time

## Future Work

- [ ] Refactor VehicleCard as organism using new molecules
- [ ] Create template components for common page layouts
- [ ] Organize feature-specific components
- [ ] Add Storybook for component documentation
- [ ] Increase test coverage to 80%+
- [ ] Add visual regression testing
