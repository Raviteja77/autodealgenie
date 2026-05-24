---
paths: frontend/**/*.{ts,tsx}
---

# Frontend Rules (Auto-loaded for TypeScript files)

You are working in the **Next.js 14 frontend** of AutoDealGenie.

## Component Hierarchy — ALWAYS follow this
```
Atoms     → primitives: Button, Input, Card, Modal, Spinner
Molecules → composed from atoms: PriceDisplay, VehicleTitle, BudgetSlider
Organisms → feature-level: VehicleCard, FilterPanel, NegotiationChat
Pages     → compose organisms + call apiClient
```
**Rule**: Atoms don't import Molecules. Molecules don't import Organisms.
Data flows DOWN via props. Global state via Context hooks.

## Server vs Client Components
```tsx
// Default — Server Component (no directive needed)
// Good for: static content, DB reads, API calls on load

// "use client" — only when you need:
// useState, useEffect, onClick handlers, browser APIs (window, localStorage)
"use client"
```
Start server-side. Only add `"use client"` when you actually need it.

## Component Template
```tsx
// components/organisms/MyFeature.tsx
"use client" // only if needed

import { Button, Card } from "@/components/atoms"
import { useMyHook } from "@/lib/hooks/useMyHook"
import { apiClient } from "@/lib/api"
import type { MyDataType } from "@/lib/types"

// Props interface ABOVE the component, always
interface MyFeatureProps {
  vehicleId: string
  onComplete: (result: MyDataType) => void
}

export function MyFeature({ vehicleId, onComplete }: MyFeatureProps) {
  // hooks first
  // derived values
  // handlers
  // return JSX
}
```

## Hooks Template
```ts
// lib/hooks/useMyFeature.ts
import { useState, useCallback } from "react"
import { apiClient } from "@/lib/api"
import type { MyDataType } from "@/lib/types"

export function useMyFeature(id: string) {
  const [data, setData] = useState<MyDataType | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiClient.getMyThing(id)
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong")
    } finally {
      setLoading(false)
    }
  }, [id])

  return { data, loading, error, fetchData }
}
```

## Form Validation (Zod)
```ts
// lib/validation/myFormSchema.ts
import { z } from "zod"

export const myFormSchema = z.object({
  name: z.string().min(1, "Name is required"),
  price: z.number().positive("Price must be positive"),
})

export type MyFormData = z.infer<typeof myFormSchema>
```

## Rules
- No `any` types — use `unknown` and narrow, or define the type properly
- Named exports only — no default exports (makes refactoring easier)
- Keep components under 200 lines — extract sub-components if larger
- Error states must show user-friendly messages, never stack traces
- Loading states must disable form submissions (no double-submit)
- All text visible to users must work at mobile viewport (375px min)
- Use `data-testid` attributes for elements you want to test with Playwright
