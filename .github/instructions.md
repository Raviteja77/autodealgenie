# Component Organization Guidelines

This document outlines the folder structure and organization principles for the AutoDealGenie frontend components, following Atomic Design methodology.

## Overview

The component architecture follows **Atomic Design principles** to create a scalable, maintainable, and consistent UI component library. Components are organized into hierarchical categories based on their complexity and composition.

## Directory Structure

```
frontend/components/
├── atoms/              # Basic building blocks (smallest reusable elements)
├── molecules/          # Simple combinations of atoms
├── organisms/          # Complex UI sections combining molecules and atoms
├── common/            # Shared layout and structural components
├── negotiation/       # Feature-specific negotiation components
├── examples/          # Example/demo components
└── index.ts           # Centralized exports
```

## Component Categories

### Atoms

**Definition:** The smallest, most basic building blocks of the UI. These are fundamental components that cannot be broken down further without losing their functionality.

**Characteristics:**
- Single responsibility
- Highly reusable across the application
- No dependencies on other custom components
- Minimal or no internal state
- Defined with TypeScript interfaces in `.types.ts` files
- Comprehensive unit tests required

**Examples:**
- `Button` - Interactive button with variants (primary, secondary, danger, success, outline)
- `Input` - Text input field with label, validation, and error handling
- `Card` - Content container with header, body, and footer sections
- `Modal` - Dialog/overlay component for displaying content
- `Spinner` - Loading indicator

**Location:** `components/atoms/`

**Testing:** All atoms must have unit tests in `components/atoms/__tests__/`

**Usage:**
```tsx
import { Button, Input, Card } from '@/components';

<Button variant="primary" size="md" onClick={handleClick}>
  Submit
</Button>
```

### Molecules

**Definition:** Simple combinations of atoms that form small, functional UI patterns. Molecules serve a specific purpose and are more complex than atoms but simpler than organisms.

**Characteristics:**
- Composed of 2-5 atoms or other molecules
- Single, well-defined purpose
- Reusable across multiple contexts
- May contain simple state management
- Should not depend on application-specific business logic

**Examples:**
- `PriceDisplay` - Formatted price display with currency symbol
- `VehicleTitle` - Vehicle name display (make, model, year)
- `VehicleDetails` - Vehicle specifications (mileage, fuel type, transmission)
- `ViewModeToggle` - Toggle between grid/list/compact views
- `SortDropdown` - Sorting options selector
- `SavedSearchesDropdown` - Dropdown for saved search selections
- `ConnectionStatusIndicator` - Network connection status display
- `SaveSearchModal` - Simple modal for saving searches

**Location:** `components/molecules/`

**Testing:** Molecules should have unit tests covering their isolated behavior

**Usage:**
```tsx
import { PriceDisplay, VehicleTitle } from '@/components';

<VehicleTitle make="Toyota" model="Camry" year={2023} />
<PriceDisplay price={25000} size="lg" />
```

### Organisms

**Definition:** Complex, substantial UI components that combine multiple molecules and atoms to form complete sections of the interface. These are feature-rich components that represent major functional areas.

**Characteristics:**
- Composed of multiple molecules and atoms
- Contains business logic and application-specific functionality
- May manage complex state
- Often connects to APIs or global state
- Represents a complete, self-contained UI section

**Examples:**
- `VehicleCard` - Complete vehicle display card with image, details, pricing, and actions
- `FilterPanel` - Comprehensive vehicle filtering interface
- `ComparisonModal` - Side-by-side vehicle comparison view
- `ComparisonBar` - Bottom bar for managing vehicle comparisons
- `ChatInput` - Complex chat input with attachment support and message types
- `FinancingComparisonModal` - Financing options comparison and calculator
- `InsuranceRecommendations` - Insurance provider recommendations with filtering
- `LenderRecommendations` - Lender options with filtering and comparison

**Location:** `components/organisms/`

**Testing:** Organisms should have integration tests covering their main functionality and interactions

**Usage:**
```tsx
import { VehicleCard, FilterPanel } from '@/components';

<FilterPanel 
  isOpen={isOpen} 
  onClose={handleClose} 
  vehicleCount={results.length} 
/>

<VehicleCard 
  vehicle={vehicleData}
  displayMode="monthly"
  onFavorite={handleFavorite}
/>
```

### Common Components

**Definition:** Shared structural and layout components that provide consistent framing and navigation across the application.

**Characteristics:**
- Used across multiple pages
- Provide consistent layout and structure
- May contain routing logic
- Often stateful and connected to global state

**Examples:**
- `Header` - Application header with navigation
- `Footer` - Application footer with links
- `ProgressStepper` - Multi-step form progress indicator
- `ErrorBoundary` - Error handling wrapper component

**Location:** `components/common/`

**Usage:**
```tsx
import { Header, Footer, ProgressStepper } from '@/components';

<Header />
<ProgressStepper currentStep={2} totalSteps={5} />
<Footer />
```

## Best Practices

### 1. Component Organization

- **Keep components focused:** Each component should have a single, well-defined responsibility
- **Favor composition:** Build complex components by composing simpler ones
- **Extract reusable logic:** Use custom hooks for business logic that can be shared across components
- **Separate concerns:** Keep presentation separate from data fetching and state management

### 2. Naming Conventions

- **Components:** `PascalCase.tsx` (e.g., `VehicleCard.tsx`)
- **Types:** `PascalCase.types.ts` (e.g., `VehicleCard.types.ts`)
- **Tests:** `PascalCase.test.tsx` (e.g., `VehicleCard.test.tsx`)
- **Hooks:** `useCamelCase.ts` (e.g., `useFinancing.ts`)
- **Utilities:** `camelCase.ts` (e.g., `formatting.ts`)

### 3. Import Standards

Always use the centralized export from `@/components`:

```tsx
// ✅ Good - Import from main components export
import { Button, Card, VehicleCard, PriceDisplay } from '@/components';

// ❌ Bad - Direct imports bypass the API
import { Button } from '@/components/atoms/Button';
import VehicleCard from '@/components/organisms/VehicleCard';
```

### 4. Type Safety

- All components must have explicit TypeScript interfaces
- Export types from `.types.ts` files for atoms and complex components
- No use of `any` type unless absolutely necessary and documented
- Use proper type exports for consumers

### 5. Testing Requirements

- **Atoms:** 100% test coverage (critical building blocks)
- **Molecules:** 80%+ test coverage
- **Organisms:** 70%+ test coverage with focus on integration
- **All components:** Tests should verify isolated behavior and props handling

### 6. Documentation

- Add JSDoc comments to all exported components and functions
- Include usage examples in component files or Storybook
- Document complex props and their expected values
- Keep this guide updated when adding new component categories

## Migration Guidelines

When adding new components or refactoring existing ones:

1. **Categorize correctly:** Determine if the component is an atom, molecule, or organism
2. **Start simple:** Begin with atoms, compose into molecules, then build organisms
3. **Update exports:** Add new components to the appropriate `index.ts` file
4. **Write tests first:** Create tests before or immediately after creating the component
5. **Document:** Add the component to this guide and include usage examples
6. **Review imports:** Ensure all imports use the centralized `@/components` export

## File Structure Example

```
components/atoms/Button/
├── Button.tsx              # Component implementation
├── Button.types.ts         # TypeScript interfaces
├── Button.test.tsx         # Unit tests
└── index.ts               # Local export

components/atoms/index.ts   # Barrel export for all atoms
components/index.ts         # Main export file
```

## Categorization Decision Tree

When uncertain about component categorization:

1. **Can it be broken down further?**
   - No → Likely an **atom**
   - Yes → Continue to #2

2. **Does it combine 2-5 simple components?**
   - Yes, and serves single purpose → **Molecule**
   - Yes, but complex/multi-purpose → Continue to #3

3. **Does it represent a complete UI section?**
   - Yes, with business logic → **Organism**
   - No, provides structure/layout → **Common**

4. **Is it feature-specific?**
   - Yes → Feature folder (e.g., `negotiation/`)
   - No → Re-evaluate from #1

## Resources

- [Atomic Design Methodology](https://bradfrost.com/blog/post/atomic-web-design/) by Brad Frost
- [Component Architecture Documentation](../frontend/COMPONENT_ARCHITECTURE.md)
- [Testing Guidelines](../frontend/README.md#testing)

## Maintenance

This document should be updated whenever:
- New component categories are added
- Categorization rules change
- New best practices are established
- Breaking changes are introduced to the component API

---

**Last Updated:** December 2024  
**Maintainers:** AutoDealGenie Development Team
