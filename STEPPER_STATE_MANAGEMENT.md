# Stepper State Management Documentation

## Overview

The AutoDealGenie application implements a multi-step workflow for the car buying process. The stepper state management system provides:

- **Dynamic step tracking** based on user navigation
- **Navigation guards** to prevent skipping required steps
- **Step completion tracking** to enable free navigation for completed steps
- **Data persistence** using sessionStorage for seamless user experience
- **API call optimization** through caching of completed step results

## Architecture

### StepperProvider Context

The `StepperProvider` is a React Context Provider that manages the entire stepper state across the application. It is wrapped around the entire app in `app/layout.tsx`.

**Location**: `/frontend/app/context/StepperProvider.tsx`

### Step Configuration

Steps are defined in the `STEPS` constant:

```typescript
export const STEPS: Step[] = [
  { id: 0, label: "Search", path: "/dashboard/search", requiresPrevious: false },
  { id: 1, label: "Results", path: "/dashboard/results", requiresPrevious: true },
  { id: 2, label: "Negotiate", path: "/negotiation", requiresPrevious: true },
  { id: 3, label: "Evaluate", path: "/evaluation", requiresPrevious: true },
  { id: 4, label: "Finalize", path: "/deals", requiresPrevious: true },
];
```

Each step has:
- `id`: Unique identifier (0-indexed)
- `label`: Display name shown in the stepper UI
- `path`: URL route for the step
- `requiresPrevious`: Whether this step requires the previous step to be completed

## State Management

### State Structure

```typescript
interface StepperState {
  currentStep: number;              // Active step based on current route
  completedSteps: Set<number>;      // Set of completed step IDs
  stepData: Record<number, unknown>; // Data stored for each step
  isNavigating: boolean;            // Navigation state flag
}
```

### Persistence

State is persisted to `sessionStorage` with the following keys:
- `stepper_completed_steps`: Array of completed step IDs
- `stepper_step_data`: Object containing data for each step
- `stepper_current_step`: Current active step number

This ensures the user's progress is maintained across page refreshes within the same session.

## Navigation Rules

### Forward Navigation
- Users can **only** navigate to the next step if the current step is completed
- Steps with `requiresPrevious: true` enforce this rule
- The first step (Search) is always accessible

### Backward Navigation
- Users can **freely** navigate to any completed step
- This allows refinement of search criteria or review of previous selections
- No restrictions on backward navigation to completed steps

### Direct URL Access
- Attempting to access a step without completing prerequisites redirects to the first incomplete step
- This is enforced through the `canNavigateToStep()` function
- Each page component checks navigation permission in a `useEffect` hook

## API Call Optimization

### Caching Strategy

The Results page implements API call caching:

```typescript
// Check if we have cached results for this exact query
const cachedData = getStepData<CachedResultsData>(1);
if (cachedData && cachedData.queryString === currentQueryString && isStepCompleted(1)) {
  // Use cached data - no API call needed
  setVehicles(cachedData.vehicles);
  return;
}

// Otherwise, fetch fresh data
const response = await apiClient.searchCars(searchRequest);

// Cache the results
completeStep(1, {
  queryString: currentQueryString,
  vehicles: transformedVehicles,
  message: response.message,
});
```

### Benefits
- **Avoids redundant API calls** when navigating back to Results from Negotiation/Evaluation
- **Improves performance** by reducing server load
- **Faster navigation** between completed steps
- **Query-specific caching** ensures fresh data when search parameters change

## Usage Guide

### Using the useStepper Hook

```typescript
import { useStepper } from "@/app/context";

function MyComponent() {
  const {
    currentStep,           // Current step number
    completedSteps,        // Set of completed step IDs
    steps,                 // Array of step configurations
    isStepCompleted,       // Check if a step is completed
    canNavigateToStep,     // Check if navigation is allowed
    completeStep,          // Mark a step as completed
    navigateToStep,        // Navigate to a specific step
    getStepData,           // Retrieve stored step data
    setStepData,           // Store data for a step
    goToNextStep,          // Navigate to next step
    goToPreviousStep,      // Navigate to previous step
    resetStepper,          // Reset all state
  } = useStepper();
  
  // Your component logic
}
```

### Marking a Step as Completed

When a user completes an action that should mark a step as done:

```typescript
const handleSearch = () => {
  // Perform search action
  const searchParams = buildSearchParams();
  
  // Mark step as completed and store data
  completeStep(0, { searchParams });
  
  // Navigate to next step
  goToNextStep();
};
```

### Checking Navigation Permission

Each protected page should check navigation permission:

```typescript
useEffect(() => {
  if (!canNavigateToStep(2)) {
    // Redirect to first incomplete step
    router.push("/dashboard/search");
  }
}, [canNavigateToStep, router]);
```

### Storing and Retrieving Step Data

```typescript
// Store data
setStepData(1, {
  selectedVehicle: vehicle,
  searchCriteria: criteria,
});

// Retrieve data
const stepOneData = getStepData<StepOneData>(1);
if (stepOneData) {
  console.log(stepOneData.selectedVehicle);
}
```

## Integration Points

### Dashboard Layout

The dashboard layout reads the stepper state and passes it to the `ProgressStepper` component:

```typescript
const { currentStep, steps } = useStepper();

<ProgressStepper
  activeStep={currentStep}
  steps={steps.map(step => step.label)}
/>
```

### Search Page (Step 0)

- User inputs search criteria
- On search submission, step is marked complete
- Search parameters are stored for potential refinement
- Navigation to Results page

### Results Page (Step 1)

- Checks if search step is completed
- Caches vehicle results to avoid redundant API calls
- Stores selected vehicle when user clicks "Negotiate" or "View Details"
- Marks step as complete when results are loaded

### Negotiation Page (Step 2)

- Checks if results step is completed
- Displays negotiation interface
- "Complete Negotiation" button marks step complete and navigates to Evaluation

### Evaluation Page (Step 3)

- Checks if negotiation step is completed
- Displays deal evaluation
- "Accept & Finalize" button marks step complete and navigates to Deals

### Deals Page (Step 4)

- Final step - displays completed deals
- No stepper shown (could be added if needed)

## Edge Cases Handled

### Direct URL Access
If a user tries to access `/evaluation` directly without completing previous steps:
- Navigation guard redirects to `/dashboard/search`
- User must complete the flow in order

### Page Refresh
- State is restored from sessionStorage
- User can continue from where they left off
- Completed steps remain accessible

### Browser Back Button
- Current step updates automatically based on URL
- Backward navigation to completed steps is allowed
- Forward navigation still requires completion

### Multiple Search Refinements
- User can navigate back to search page from results
- Modifying search and re-executing updates cached data
- Query-specific caching ensures correct results are shown

## Testing Recommendations

### Unit Tests

1. **StepperProvider**
   - Test initial state
   - Test step completion
   - Test navigation guards
   - Test data storage/retrieval
   - Test state persistence

2. **Navigation Rules**
   - Test forward navigation blocked for incomplete steps
   - Test backward navigation allowed for completed steps
   - Test first step always accessible

3. **Caching Logic**
   - Test API call made for new query
   - Test cached data used for same query
   - Test cache invalidation on query change

### Integration Tests

1. **Complete User Flow**
   - Navigate through all steps in order
   - Verify each step marks as completed
   - Verify data is passed between steps

2. **Back Navigation**
   - Complete steps 0-2
   - Navigate back to step 0
   - Modify search criteria
   - Verify new search results are fetched
   - Continue to step 2 and verify no redundant API calls

3. **Direct URL Access**
   - Clear sessionStorage
   - Attempt to access `/evaluation` directly
   - Verify redirect to `/dashboard/search`

### E2E Tests (Playwright)

```typescript
test('should prevent skipping steps', async ({ page }) => {
  await page.goto('/evaluation');
  await expect(page).toHaveURL('/dashboard/search');
});

test('should allow back navigation to completed steps', async ({ page }) => {
  // Complete search
  await page.goto('/dashboard/search');
  await page.fill('input[name="make"]', 'Toyota');
  await page.click('button:has-text("Search Cars")');
  
  // Verify on results
  await expect(page).toHaveURL(/\/dashboard\/results/);
  
  // Go back to search
  await page.goto('/dashboard/search');
  
  // Should not be redirected
  await expect(page).toHaveURL('/dashboard/search');
});
```

## Troubleshooting

### State Not Persisting
- Check browser's sessionStorage is enabled
- Verify no errors in console related to JSON serialization
- Ensure data being stored is serializable

### Navigation Guards Not Working
- Verify `StepperProvider` is wrapped around the entire app
- Check that `useEffect` hooks are calling `canNavigateToStep`
- Ensure router is being used correctly for redirects

### API Calls Not Caching
- Verify query string comparison is exact
- Check that `completeStep` is called after successful API response
- Ensure `isStepCompleted` check is before the API call

## Future Enhancements

1. **Step Validation**
   - Add validation rules for each step
   - Prevent completion if validation fails

2. **Analytics Integration**
   - Track time spent on each step
   - Monitor completion rates
   - Identify drop-off points

3. **Server-Side State Sync**
   - Sync completed steps to user's account
   - Enable cross-device continuation
   - Recover abandoned flows

4. **Conditional Steps**
   - Add logic for optional steps
   - Branch flows based on user choices

5. **Progress Persistence**
   - Store incomplete flows in database
   - Send reminder emails for abandoned searches
   - Pre-populate forms from saved progress

## References

- `StepperProvider`: `/frontend/app/context/StepperProvider.tsx`
- `ProgressStepper`: `/frontend/components/common/ProgressStepper.tsx`
- Dashboard Layout: `/frontend/app/dashboard/layout.tsx`
- Search Page: `/frontend/app/dashboard/search/page.tsx`
- Results Page: `/frontend/app/dashboard/results/page.tsx`
- Negotiation Page: `/frontend/app/negotiation/page.tsx`
- Evaluation Page: `/frontend/app/evaluation/page.tsx`
