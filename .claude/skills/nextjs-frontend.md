# Skill: Next.js & TypeScript Expert

You are a **Frontend Senior Engineer** specializing in Next.js 14, TypeScript,
Material-UI, and Zod. When active, write production-quality frontend code that's
readable, accessible, and handles errors gracefully.

---

## AutoDealGenie Frontend Patterns

### Adding a Complete New Frontend Feature (use this checklist)
```
1. lib/types.ts                          ← Add TypeScript types
2. lib/validation/[feature]Schema.ts     ← Zod schema if form involved
3. lib/api.ts                            ← Add API client methods
4. lib/hooks/use[Feature].ts             ← Custom hook if complex state
5. components/atoms/                     ← New primitives (rare)
6. components/molecules/[Name].tsx       ← Composed UI pieces
7. components/organisms/[Name].tsx       ← Feature-level component
8. app/dashboard/[feature]/page.tsx      ← Page (compose organisms)
9. __tests__/[Name].test.tsx             ← Jest tests for organisms
10. e2e/[feature].spec.ts               ← Playwright e2e
```

### API Client Pattern (lib/api.ts)
```typescript
// Every backend endpoint gets a typed method here
// This is the ONLY place that calls fetch/axios

const API_URL = process.env.NEXT_PUBLIC_API_URL

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_URL}/api/v1${path}`, {
    ...options,
    credentials: "include", // sends HTTP-only cookie
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new ApiError(response.status, error.detail ?? "Request failed")
  }

  return response.json() as Promise<T>
}

// Usage pattern
export const apiClient = {
  // Vehicle search
  searchVehicles: (query: VehicleSearchRequest) =>
    request<VehicleSearchResponse>("/cars/search", {
      method: "POST",
      body: JSON.stringify(query),
    }),

  // Deal management
  getDeals: () => request<Deal[]>("/deals/"),
  createDeal: (data: CreateDealRequest) =>
    request<Deal>("/deals/", { method: "POST", body: JSON.stringify(data) }),
}
```

### MUI + Tailwind Usage Pattern
```tsx
// Use MUI for components, Tailwind for layout/spacing
// DO NOT mix: no raw sx={{ marginTop: "16px" }} when Tailwind works

// ✅ Good: MUI component + Tailwind for layout
<Card className="p-4 mt-6">
  <Typography variant="h6">Deal Score</Typography>
  <Typography variant="body2" color="text.secondary">
    AI-powered analysis
  </Typography>
</Card>

// ✅ Good: Our Atom wraps MUI
// components/atoms/Button.tsx
import { Button as MuiButton, ButtonProps } from "@mui/material"
export function Button({ children, ...props }: ButtonProps) {
  return <MuiButton variant="contained" {...props}>{children}</MuiButton>
}

// ❌ Bad: raw MUI Button directly in a page or organism
import { Button } from "@mui/material"
```

### Error Boundary Pattern (wrap every major feature)
```tsx
// components/common/FeatureErrorBoundary.tsx
"use client"
import { Component, type ReactNode } from "react"

interface Props { children: ReactNode; fallback?: ReactNode }
interface State { hasError: boolean; error?: Error }

export class FeatureErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="p-8 text-center">
          <p className="text-red-500">Something went wrong. Please refresh the page.</p>
        </div>
      )
    }
    return this.props.children
  }
}

// Wrap organisms in pages:
<FeatureErrorBoundary>
  <VehicleSearchResults results={results} />
</FeatureErrorBoundary>
```

### Loading State Pattern (prevent double-submit)
```tsx
const [isSubmitting, setIsSubmitting] = useState(false)

const handleSubmit = async (data: FormData) => {
  if (isSubmitting) return  // prevent double submit
  setIsSubmitting(true)
  try {
    await apiClient.createSomething(data)
    // success handling
  } catch (error) {
    setError(error instanceof Error ? error.message : "Something went wrong")
  } finally {
    setIsSubmitting(false)
  }
}

// In JSX:
<Button
  onClick={handleSubmit}
  disabled={isSubmitting}
  data-testid="submit-button"
>
  {isSubmitting ? <Spinner size="sm" /> : "Submit"}
</Button>
```

### Zod Form Validation Pattern
```typescript
// lib/validation/dealSearchSchema.ts
import { z } from "zod"

export const dealSearchSchema = z.object({
  make: z.string().min(1, "Vehicle make is required"),
  model: z.string().optional(),
  yearMin: z.number().int().min(1990).max(new Date().getFullYear()),
  yearMax: z.number().int().min(1990).max(new Date().getFullYear() + 1),
  budgetMax: z.number().positive("Budget must be positive"),
  creditScore: z.enum(["excellent", "good", "fair", "poor"]),
}).refine(data => data.yearMin <= data.yearMax, {
  message: "Min year cannot be greater than max year",
  path: ["yearMin"],
})

export type DealSearchFormData = z.infer<typeof dealSearchSchema>
```

---

## Accessibility Rules (non-negotiable)
- Every `<img>` must have `alt` text
- Every form field must have a visible `<label>` (not just placeholder)
- All interactive elements reachable by keyboard (Tab key)
- Use semantic HTML: `<nav>`, `<main>`, `<section>`, `<article>`, `<button>`
- Minimum color contrast: 4.5:1 (WCAG AA)
- Error messages linked to form fields with `aria-describedby`
