# UI Changes Visualization

## Accept Offer Dialog Changes

### Before
```
┌─────────────────────────────────────┐
│        Accept Offer?                │
├─────────────────────────────────────┤
│                                     │
│ Are you sure you want to accept    │
│ the current offer of $25,000?      │
│                                     │
│ This will complete the negotiation │
│ and move forward with the deal.    │
│                                     │
│  [Cancel]        [Yes, Accept]     │
└─────────────────────────────────────┘
```

### After
```
┌─────────────────────────────────────┐
│        Accept Offer?                │
├─────────────────────────────────────┤
│                                     │
│ Are you sure you want to accept    │
│ the current offer?                 │
│                                     │
│ ┌─────────────────────────────────┐│
│ │  $25,000        [AI Suggested]  ││
│ │  From Round 3 • Jan 15, 02:30 PM││
│ │  ───────────────────────────────││
│ │  Original Price      $30,000    ││
│ │  You Save           $5,000      ││
│ └─────────────────────────────────┘│
│                                     │
│ This will complete the negotiation │
│ and move forward with the deal.    │
│                                     │
│  [Cancel]        [Yes, Accept]     │
└─────────────────────────────────────┘
```

**Key Improvements:**
- Shows actual price being accepted with formatting
- Visual indicator for price source (AI/Dealer/Counter)
- Timestamp and round information
- Price comparison showing original price and savings
- More context for user decision-making

## Price Tracking Panel Changes

### Before
```
┌────────────────────────────┐
│  Price Tracking            │
├────────────────────────────┤
│  Asking Price    $30,000   │
│  Your Target     $27,000   │
│  Current Offer   $25,000   │
└────────────────────────────┘
```

### After
```
┌────────────────────────────┐
│  Price Tracking            │
├────────────────────────────┤
│  Asking Price    $30,000   │
│  Your Target     $27,000   │
│  Current Offer [AI] $25,000│
└────────────────────────────┘

or with dealer price:
┌────────────────────────────┐
│  Price Tracking            │
├────────────────────────────┤
│  Asking Price    $30,000   │
│  Your Target     $27,000   │
│  Current Offer [Dealer] $26,500│
└────────────────────────────┘

or with user counter:
┌────────────────────────────┐
│  Price Tracking            │
├────────────────────────────┤
│  Asking Price    $30,000   │
│  Your Target     $27,000   │
│  Current Offer [You] $24,000│
└────────────────────────────┘
```

**Key Improvements:**
- Visual badge showing price source
- Color-coded chips (AI: primary, Dealer: secondary, You: info)
- Always shows the most recent price from message history

## Dealer Info Form Changes

### Before
```
┌─────────────────────────────────────┐
│  [Price Quote ▼]  [Price: ____]    │
│  [Cancel]                           │
└─────────────────────────────────────┘

Regular chat input below
```

### After

#### Counter Offer Selected
```
┌─────────────────────────────────────┐
│  Submit Dealer Information          │
├─────────────────────────────────────┤
│  Information Type                   │
│  [Counter Offer          ▼]        │
│                                     │
│  Dealer's Counter Offer *           │
│  $ [_____________]                  │
│                                     │
│  ℹ Price is required for counter   │
│     offers                          │
│                                     │
│  [Enter details about the dealer's │
│   counter offer...                 │
│   __________________________________│
│   __________________________________│
│   __________________________________]│
│  0/2000                            │
│                                     │
│         [Cancel]  [Submit]          │
└─────────────────────────────────────┘
```

#### Quote Selected
```
┌─────────────────────────────────────┐
│  Submit Dealer Information          │
├─────────────────────────────────────┤
│  Information Type                   │
│  [Price Quote            ▼]        │
│                                     │
│  Quoted Price (if mentioned)        │
│  $ [_____________]                  │
│                                     │
│  ℹ Include the quoted price if     │
│     mentioned                       │
│                                     │
│  [Enter details about the price    │
│   quote...                         │
│   __________________________________│
│   __________________________________│
│   __________________________________]│
│  0/2000                            │
│                                     │
│         [Cancel]  [Submit]          │
└─────────────────────────────────────┘
```

#### Inspection Report Selected
```
┌─────────────────────────────────────┐
│  Submit Dealer Information          │
├─────────────────────────────────────┤
│  Information Type                   │
│  [Inspection Report      ▼]        │
│                                     │
│  ℹ Provide details from the        │
│     inspection report               │
│                                     │
│  [Enter inspection report details..│
│   __________________________________│
│   __________________________________│
│   __________________________________]│
│  0/2000                            │
│                                     │
│         [Cancel]  [Submit]          │
└─────────────────────────────────────┘
```

**Key Improvements:**
- Section title for clarity
- Full-width form with proper spacing
- Dynamic label changes based on info type
- Price field shows/hides based on type
- Required indicator (*) for mandatory fields
- Context-specific helper text
- Context-specific placeholders
- Validation error display
- Better visual hierarchy
- Right-aligned action buttons

## Validation Examples

### Price Validation Errors

#### Undefined Price
```
┌─────────────────────────────────────┐
│        Accept Offer?                │
├─────────────────────────────────────┤
│  ⚠ Cannot accept offer             │
│                                     │
│  No negotiated price found         │
│                                     │
│  [Close]                           │
└─────────────────────────────────────┘

Accept button is disabled
```

#### Price Above Asking
```
┌─────────────────────────────────────┐
│        Accept Offer?                │
├─────────────────────────────────────┤
│  ⚠ Cannot accept offer             │
│                                     │
│  Price ($35,000) exceeds asking    │
│  price ($30,000)                   │
│                                     │
│  [Close]                           │
└─────────────────────────────────────┘

Accept button is disabled
```

#### Price Too Low
```
┌─────────────────────────────────────┐
│        Accept Offer?                │
├─────────────────────────────────────┤
│  ⚠ Cannot accept offer             │
│                                     │
│  Price ($10,000) is unreasonably   │
│  low (less than 50% of asking      │
│  price)                            │
│                                     │
│  [Close]                           │
└─────────────────────────────────────┘

Accept button is disabled
```

#### Price Above Target (Warning)
```
┌─────────────────────────────────────┐
│  Browser Confirmation Dialog        │
├─────────────────────────────────────┤
│  ⚠ Warning: Price ($29,000) is 7% │
│     above your target ($27,000)    │
│                                     │
│  Do you want to continue with      │
│  accepting this offer?             │
│                                     │
│  [Cancel]        [OK]              │
└─────────────────────────────────────┘
```

### Dealer Info Validation Errors

#### Missing Required Price (Counter Offer)
```
┌─────────────────────────────────────┐
│  Submit Dealer Information          │
├─────────────────────────────────────┤
│  Information Type                   │
│  [Counter Offer          ▼]        │
│                                     │
│  Dealer's Counter Offer *           │
│  $ [_____________] ← Red border    │
│                                     │
│  [Content filled in...]            │
│                                     │
│  ❌ Dealer's Counter Offer is      │
│     required                        │
│                                     │
│         [Cancel]  [Submit]          │
└─────────────────────────────────────┘
```

#### Invalid Price Format
```
┌─────────────────────────────────────┐
│  Submit Dealer Information          │
├─────────────────────────────────────┤
│  Information Type                   │
│  [Counter Offer          ▼]        │
│                                     │
│  Dealer's Counter Offer *           │
│  $ [-500_________] ← Red border    │
│                                     │
│  [Content filled in...]            │
│                                     │
│  ❌ Please enter a valid price     │
│     greater than 0                  │
│                                     │
│         [Cancel]  [Submit]          │
└─────────────────────────────────────┘
```

#### Missing Content
```
┌─────────────────────────────────────┐
│  Submit Dealer Information          │
├─────────────────────────────────────┤
│  Information Type                   │
│  [Quote                  ▼]        │
│                                     │
│  Quoted Price (if mentioned)        │
│  $ [25000_________]                │
│                                     │
│  [__________________] ← Red border │
│   __________________________________│
│   __________________________________]│
│                                     │
│  ❌ Please enter information       │
│     content                         │
│                                     │
│         [Cancel]  [Submit]          │
└─────────────────────────────────────┘
```

## State Machine - Accept Button

```
┌─────────────────────────────────────┐
│  Accept Button State Machine        │
├─────────────────────────────────────┤
│                                     │
│  Enabled when:                      │
│  ✓ latestPrice exists               │
│  ✓ latestPrice.price is valid      │
│  ✓ price ≤ askingPrice              │
│  ✓ price ≥ 50% of askingPrice       │
│  ✓ not loading                      │
│                                     │
│  Disabled when:                     │
│  ✗ No latestPrice found             │
│  ✗ latestPrice.price is null        │
│  ✗ price > askingPrice              │
│  ✗ price < 50% of askingPrice       │
│  ✗ Loading state active             │
│                                     │
│  Warning shown when:                │
│  ⚠ price > 120% of targetPrice      │
│    (but still enabled)              │
└─────────────────────────────────────┘
```

## Flow Diagram - Price Extraction

```
Message History (newest first)
       │
       ▼
┌─────────────────────────────────────┐
│  getLatestNegotiatedPrice()         │
├─────────────────────────────────────┤
│  Loop through messages:             │
│                                     │
│  1. Check metadata.suggested_price  │
│     → Found? Return {price, "ai"}  │
│                                     │
│  2. Check message_type=dealer_info  │
│     AND metadata.price_mentioned    │
│     → Found? Return {price,"dealer"}│
│                                     │
│  3. Check role=user AND             │
│     metadata.counter_offer          │
│     → Found? Return {price,"counter"}│
│                                     │
│  4. Continue to next message        │
│                                     │
│  No price found? → Return null      │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  validateNegotiatedPrice()          │
├─────────────────────────────────────┤
│  1. Check if price exists           │
│     → No? Invalid                   │
│                                     │
│  2. Check if price > 0              │
│     → No? Invalid                   │
│                                     │
│  3. Check if price ≤ askingPrice    │
│     → No? Invalid                   │
│                                     │
│  4. Check if price ≥ 50% of asking  │
│     → No? Invalid                   │
│                                     │
│  5. Check if price > 120% of target │
│     → Yes? Warning (but valid)     │
│                                     │
│  All checks pass? → Valid           │
└─────────────────────────────────────┘
       │
       ▼
Display in UI with formatting
```

## Flow Diagram - Dealer Info Submission

```
User clicks "Attach" button
       │
       ▼
┌─────────────────────────────────────┐
│  Dealer Info Form Opens             │
├─────────────────────────────────────┤
│  Default: "Counter Offer"           │
│  Main chat input disabled           │
└─────────────────────────────────────┘
       │
       ▼
User selects info type
       │
       ▼
┌─────────────────────────────────────┐
│  Form Updates Dynamically           │
├─────────────────────────────────────┤
│  - Labels change                    │
│  - Price field show/hide            │
│  - Required status updates          │
│  - Placeholder text updates         │
│  - Helper text updates              │
└─────────────────────────────────────┘
       │
       ▼
User fills in content and price
       │
       ▼
User clicks "Submit"
       │
       ▼
┌─────────────────────────────────────┐
│  validateDealerInfo()               │
├─────────────────────────────────────┤
│  1. Check content exists            │
│     → No? Show error, return        │
│                                     │
│  2. If priceRequired, check price   │
│     → Missing? Show error, return   │
│                                     │
│  3. If price provided, validate     │
│     → Invalid? Show error, return   │
│                                     │
│  All valid? → Continue              │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  API Call to Backend                │
├─────────────────────────────────────┤
│  POST /negotiations/{id}/dealer-info│
│  {                                  │
│    info_type: "counteroffer",      │
│    content: "...",                 │
│    price_mentioned: 25000          │
│  }                                  │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Success                            │
├─────────────────────────────────────┤
│  - Form closes                      │
│  - Fields reset                     │
│  - Main chat re-enabled             │
│  - Message appears in chat          │
└─────────────────────────────────────┘
```

## Info Type Configuration Matrix

| Info Type          | Price Label                      | Price Required | Price Shown | Content Placeholder                        |
|-------------------|----------------------------------|----------------|-------------|-------------------------------------------|
| counteroffer      | Dealer's Counter Offer           | ✓ Yes          | ✓ Yes       | Enter details about counter offer...      |
| quote             | Quoted Price (if mentioned)      | ✗ No           | ✓ Yes       | Enter details about price quote...        |
| inspection_report | -                                | ✗ No           | ✗ No        | Enter inspection report details...        |
| additional_offer  | Offer Amount                     | ✗ No           | ✓ Yes       | Enter details about additional offer...   |
| other             | Price (optional)                 | ✗ No           | ✓ Yes       | Enter other dealer information...         |
