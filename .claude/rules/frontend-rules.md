---
paths: frontend/**/*.{ts,tsx}
---

# Frontend Coding Principles (auto-loaded for TypeScript files)

You are writing production TypeScript for AutoDealGenie's Next.js frontend.
These principles exist so the UI doesn't become a tangled mess that breaks
when someone changes a component or adds a feature.

---

## Component Design Principles

### Single Responsibility — One Job Per Component
```tsx
// ❌ Wrong: one component fetching data, formatting it, AND rendering it
function VehicleCard({ vehicleId }: { vehicleId: string }) {
  const [vehicle, setVehicle] = useState(null)
  useEffect(() => { fetch(`/api/vehicles/${vehicleId}`).then(...) }, [])
  const formattedPrice = `$${vehicle?.price.toLocaleString()}`
  // ...rendering
}

// ✅ Right: separate concerns
// Fetching  → useVehicle hook (lib/hooks/useVehicle.ts)
// Formatting → formatCurrency util (lib/utils/format.ts)
// Rendering  → VehicleCard component (components/search/VehicleCard.tsx)

function VehicleCard({ vehicle }: { vehicle: Vehicle }) {
  return (
    <Card>
      <p>{vehicle.year} {vehicle.make} {vehicle.model}</p>
      <p>{formatCurrency(vehicle.price)}</p>
    </Card>
  )
}
```

### Open/Closed — Extend via Props and Composition
```tsx
// ❌ Wrong: adding a variant by modifying internals with if/else chains
function Button({ type }: { type: "primary" | "danger" | "ghost" | "loading" }) {
  if (type === "primary") return <button className="bg-blue-600">
  if (type === "danger") return <button className="bg-red-600">
  // keeps growing forever
}

// ✅ Right: shadcn/ui Button uses variants via class-variance-authority
// Adding a new variant = add one entry to the variants object. Nothing else changes.
// components/ui/Button.tsx is the single source of truth.
```

### Dependency Inversion — Components Depend on Contracts, Not Implementations
```tsx
// ❌ Wrong: component knows HOW data is fetched
function SearchResults() {
  useEffect(() => {
    fetch('/api/v1/cars/search', { method: 'POST', ... })
  }, [])
}

// ✅ Right: component depends on the hook's contract, not the fetch details
function SearchResults() {
  const { results, loading, error } = useVehicleSearch()
  // component doesn't care if data comes from API, cache, or mock
}
```

---

## Clean Code for TypeScript

### Naming — Be Honest and Specific
```typescript
// ❌ Vague names
const data = await apiClient.get('/deals')
const handleClick = () => { ... }
const x = price * 0.85

// ✅ Honest names
const userDeals = await apiClient.getDeals()
const handleSaveFavoriteVehicle = () => { ... }
const discountedPrice = price * DEALER_DISCOUNT_RATE  // constant, not magic number
```

### Small Functions — One Sentence Summaries
```typescript
// If you can't describe what a function does in one sentence, split it.

// ✅ Each is one clear sentence
function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(amount)
}

function isVehicleAffordable(price: number, maxBudget: number): boolean {
  return price <= maxBudget
}

function getVehicleDisplayName(vehicle: Vehicle): string {
  return `${vehicle.year} ${vehicle.make} ${vehicle.model}`
}
```

### Comments — WHY not WHAT
```typescript
// ❌ Comment repeats the code
// Get the vehicle price
const price = vehicle.asking_price

// ✅ Comment explains non-obvious reasoning
// WebSocket negotiation falls back to HTTP polling after 5 failed reconnect attempts.
// We track attempt count in ref (not state) to avoid triggering re-renders.
const reconnectAttempts = useRef(0)

// ✅ Comment explains a business rule
// Lenders require a minimum 580 credit score. Below this, show
// a "improve your credit" message instead of empty recommendations.
const MIN_LENDER_CREDIT_SCORE = 580
```

---

## TypeScript Type Safety

### No `any` — Ever
```typescript
// ❌ any disables type checking — defeats the purpose
const handleResponse = (data: any) => { data.whatever() }

// ✅ Use unknown and narrow it
const handleResponse = (data: unknown) => {
  if (typeof data === 'object' && data !== null && 'score' in data) {
    console.log((data as DealScore).score)
  }
}

// ✅ Or better — define the type and use Zod to validate at runtime
const dealScoreSchema = z.object({ score: z.number().min(1).max(10) })
const dealScore = dealScoreSchema.parse(data)  // throws if wrong shape
```

### Prefer Explicit Types at Module Boundaries
```typescript
// At module boundaries (API calls, props, hook returns) — always explicit types
// Inside a function, TypeScript can infer — no need to annotate everything

// ✅ Explicit at boundary
export async function getVehicleDeals(userId: string): Promise<Deal[]> {
  const response = await apiClient.getDeals()
  return response.data
}

// ✅ Inferred inside function — fine
const total = deals.reduce((sum, deal) => sum + deal.asking_price, 0)
```

### Discriminated Unions for State
```typescript
// ❌ Booleans for mutually exclusive states — combinations become invalid
interface LoadState {
  isLoading: boolean
  isError: boolean
  isSuccess: boolean
  data?: Deal[]
  error?: string
}
// isLoading=true AND isError=true — impossible state, but TypeScript allows it

// ✅ Discriminated union — impossible states become impossible types
type LoadState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: Deal[] }
  | { status: 'error'; message: string }
```

---

## Defensive UI Programming

### Every Async Action Needs Three States
```tsx
// Loading, error, and success are all required. Never skip error or loading.
function EvaluationButton({ dealId }: { dealId: string }) {
  const { startEvaluation, status } = useEvaluation(dealId)

  return (
    <Button
      onClick={startEvaluation}
      disabled={status === 'loading'}  // prevent double-submit
      aria-busy={status === 'loading'}
    >
      {status === 'loading' ? <Spinner /> : 'Evaluate Deal'}
    </Button>
  )
}

// The error state must be visible to the user — never swallow it
{status === 'error' && (
  <Alert variant="destructive">
    <p>Evaluation failed. Please try again.</p>  {/* user-friendly, not "TypeError" */}
  </Alert>
)}
```

### Validate at the Form Boundary — Before the Network Call
```typescript
// lib/validation/searchSchema.ts
export const vehicleSearchSchema = z.object({
  make: z.string().min(1, 'Vehicle make is required'),
  yearMin: z.number().int().min(1990).max(new Date().getFullYear()),
  yearMax: z.number().int().min(1990).max(new Date().getFullYear() + 1),
  budgetMax: z.number().positive('Budget must be a positive number'),
}).refine(
  (data) => data.yearMin <= data.yearMax,
  { message: 'Min year must be ≤ max year', path: ['yearMin'] }
)
// Zod validates BEFORE the API call. Users see errors immediately, not after a round trip.
```

### Never Show Technical Errors to Users
```typescript
// ❌ Raw error to user
catch (error) {
  setError(error.message)  // "Cannot read properties of undefined (reading 'price')"
}

// ✅ Friendly message, technical details in logs
catch (error) {
  logger.error('Vehicle search failed', { error, query })
  setError('Vehicle search is temporarily unavailable. Please try again.')
}
```

---

## DRY with Nuance

**Extract logic into a hook when the same stateful pattern appears in 2+ components.**
**Extract a utility function when the same pure transformation appears in 2+ places.**
**Don't extract just because code looks similar — check if it's the same concept.**

```typescript
// ✅ Extract: same stateful pattern in 2+ places → custom hook
function useAsyncAction<T>(action: () => Promise<T>) {
  const [status, setStatus] = useState<'idle'|'loading'|'success'|'error'>('idle')
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)

  const execute = async () => {
    setStatus('loading')
    try {
      const result = await action()
      setData(result)
      setStatus('success')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong')
      setStatus('error')
    }
  }
  return { status, data, error, execute }
}
```

---

## Component Checklist Before Done
- [ ] Handles loading state (button disabled, spinner visible)
- [ ] Handles error state (friendly message, not stack trace)
- [ ] Handles empty state (no results, no data)
- [ ] Works at 375px mobile viewport
- [ ] All interactive elements keyboard-accessible (Tab key works)
- [ ] No `any` types
- [ ] No raw `fetch()` — uses `apiClient`
- [ ] No raw HTML button/input — uses `components/ui/`
- [ ] `data-testid` on elements that need testing
