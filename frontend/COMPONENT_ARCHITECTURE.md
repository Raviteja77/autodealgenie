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
│   │   └── __tests__/      # Unit tests for atoms
│   ├── molecules/          # Simple combinations of atoms
│   │   ├── PriceDisplay.tsx
│   │   ├── VehicleInfo.tsx
│   │   ├── ViewModeToggle.tsx
│   │   ├── SortDropdown.tsx
│   │   ├── SavedSearchesDropdown.tsx
│   │   ├── ConnectionStatusIndicator.tsx
│   │   ├── SaveSearchModal.tsx
│   │   └── __tests__/      # Unit tests for molecules (planned)
│   ├── organisms/          # Complex UI sections
│   │   ├── VehicleCard.tsx
│   │   ├── FilterPanel.tsx
│   │   ├── ComparisonModal.tsx
│   │   ├── ComparisonBar.tsx
│   │   ├── ChatInput.tsx
│   │   ├── FinancingComparisonModal.tsx
│   │   ├── InsuranceRecommendations.tsx
│   │   ├── LenderRecommendations.tsx
│   │   └── __tests__/      # Integration tests for organisms (planned)
│   ├── common/             # Shared components (Header, Footer, etc.)
│   ├── negotiation/        # Feature-specific negotiation components
│   ├── examples/           # Example/demo components
│   └── index.ts            # Main exports
├── lib/
│   ├── hooks/              # Custom React hooks
│   │   ├── useFinancing.ts
│   │   ├── useDisplayMode.ts
│   │   ├── useFilters.ts
│   │   ├── useComparison.ts
│   │   ├── useViewMode.ts
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
- **PriceDisplay**: Price formatting and display with size variants
- **MonthlyPaymentDisplay**: Monthly payment with details
- **PriceSwitcher**: Toggle between cash/monthly views
- **VehicleTitle**: Vehicle name display (make, model, year)
- **VehicleDetails**: Vehicle specifications (mileage, fuel, transmission)
- **VehicleImage**: Vehicle image with badges and actions
- **ViewModeToggle**: Toggle between grid/list/compact views
- **SortDropdown**: Sorting options selector with icons
- **SavedSearchesDropdown**: Dropdown for saved search selections
- **ConnectionStatusIndicator**: Real-time connection status display
- **SaveSearchModal**: Simple modal form for saving searches

**Usage:**
```tsx
import { PriceDisplay, VehicleTitle, SortDropdown } from '@/components';

<VehicleTitle make="Toyota" model="Camry" year={2023} />
<PriceDisplay price={25000} size="lg" />
<SortDropdown value="price_low" onChange={handleSort} />
```

### Organisms
Complex UI sections combining multiple molecules and atoms:
- **VehicleCard**: Complete vehicle display card with all details and actions
- **FilterPanel**: Comprehensive vehicle filtering interface with drawer
- **ComparisonModal**: Side-by-side vehicle comparison table
- **ComparisonBar**: Bottom bar for managing comparison selections
- **ChatInput**: Complex chat input with dealer info and attachments
- **FinancingComparisonModal**: Full financing comparison with calculators
- **InsuranceRecommendations**: Insurance provider recommendations with filters
- **LenderRecommendations**: Lender matching and comparison interface

**Usage:**
```tsx
import { VehicleCard, FilterPanel, ChatInput } from '@/components';

<VehicleCard 
  vehicle={vehicleData}
  displayMode="monthly"
  financingParams={financingOptions}
  onFavorite={handleFavorite}
/>

<FilterPanel 
  isOpen={filterOpen} 
  onClose={closeFilters} 
  vehicleCount={results.length} 
/>
```

### Common Components
Shared structural and layout components:
- **Header**: Application header with navigation
- **Footer**: Application footer with links
- **ProgressStepper**: Multi-step form progress indicator
- **ErrorBoundary**: Error handling wrapper

### Feature-Specific
- **negotiation/**: Components specific to negotiation feature (CurrentOfferStatus, etc.)

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
- Atoms: 5 components with comprehensive unit tests (32 tests passing)
- Molecules: 10 components (tests needed for 5 new molecules)
- Organisms: 8 components (tests needed)
- Hooks: 16 tests passing
- Total: 48 passing tests, ~20 additional tests needed

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

Component reorganization completed:
1. ✅ All atoms consolidated in `components/atoms/` with tests
2. ✅ Molecules organized in `components/molecules/` (10 components)
3. ✅ Organisms created in `components/organisms/` (8 complex components)
4. ✅ Duplicate `components/ui/` directory removed
5. ✅ All imports updated to use centralized `@/components` export
6. ✅ Main `components/index.ts` provides clean API
7. 🔄 Tests needed for new molecules and organisms (in progress)

## Future Work

- [ ] Add unit tests for all molecules (5 components need tests)
- [ ] Add integration tests for organisms (8 components need tests)
- [ ] Create template components for common page layouts
- [ ] Add Storybook for component documentation and visual testing
- [ ] Increase overall test coverage to 80%+
- [ ] Add visual regression testing with Playwright
- [ ] Consider extracting feature folders for domain-specific components
