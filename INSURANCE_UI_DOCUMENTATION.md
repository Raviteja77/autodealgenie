# Insurance Recommendation UI Documentation

## UI Integration in Evaluation Page

The insurance recommendations component is integrated into the evaluation page after the negotiation strategy section. Below is a visual representation of how the UI appears to users.

## Component Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                  Insurance Recommendations                       │
│                      3 Matches                                   │
├─────────────────────────────────────────────────────────────────┤
│  Top insurance providers matched to your vehicle and driving     │
│  profile                                                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐│
│  │ Sort By:         │ │ Coverage Type:   │ │ Driver Age:     ││
│  │ [Best Match ▼]   │ │ [Full Coverage ▼]│ │ [25-34 years ▼] ││
│  └──────────────────┘ └──────────────────┘ └─────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ⭐ Best Match                                                    │
│ 🛡️  Family First Insurance                       $300          │
│     Comprehensive coverage options • Rich feature set            │
│                                                    per month     │
├─────────────────────────────────────────────────────────────────┤
│ Annual Premium        Match Score              Rank             │
│ $3,600                72/100                   #1               │
├─────────────────────────────────────────────────────────────────┤
│                       View Details ▼                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [Expanded Details - Only shown when user clicks View Details]   │
│                                                                  │
│ Family-focused coverage with multi-vehicle and teen driver       │
│ programs                                                         │
│                                                                  │
│ Coverage Options:                                                │
│ [Liability] [Comprehensive] [Full]                              │
│                                                                  │
│ Features:                                                        │
│ ✓ Teen driver monitoring   ✓ Multi-vehicle discounts           │
│ ✓ Good student discounts                                        │
│                                                                  │
│ Benefits:                                                        │
│ ℹ️ Family claim assistance  ℹ️ Educational resources           │
│ ℹ️ Safe driving rewards                                         │
│                                                                  │
│ Provider Details:                                                │
│ Premium Range: $80 - $300                                       │
│ Vehicle Value Range: $5,000 - $100,000                          │
│ Driver Age Range: 16 - 95 years                                 │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│              [Get Quote]        [Select Provider]                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🛡️  SafeGuard Auto Insurance                    $300           │
│     Competitive pricing • Rich feature set        per month     │
├─────────────────────────────────────────────────────────────────┤
│ Annual Premium        Match Score              Rank             │
│ $3,600                71/100                   #2               │
├─────────────────────────────────────────────────────────────────┤
│                       View Details ▼                             │
├─────────────────────────────────────────────────────────────────┤
│              [Get Quote]        [Select Provider]                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🛡️  Green Driver Insurance                      $320           │
│     Eco-friendly options • Rich feature set       per month     │
├─────────────────────────────────────────────────────────────────┤
│ Annual Premium        Match Score              Rank             │
│ $3,840                68/100                   #3               │
├─────────────────────────────────────────────────────────────────┤
│                       View Details ▼                             │
├─────────────────────────────────────────────────────────────────┤
│              [Get Quote]        [Select Provider]                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ℹ️ Note: Premiums shown are estimates based on vehicle value,   │
│ age, and driver age. Actual rates depend on your complete       │
│ driving history and may vary. Get quotes directly from          │
│ providers for accurate pricing.                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Interactive Features

### 1. Sorting Options
Users can sort recommendations by:
- **Best Match** (default): Based on scoring algorithm
- **Lowest Premium**: Ascending by monthly premium
- **Most Coverage Options**: Providers with broadest coverage

### 2. Coverage Type Filter
Three coverage types available:
- **Liability Only**: Minimum required coverage
- **Comprehensive**: Theft, vandalism, natural disasters
- **Full Coverage**: Comprehensive + collision

### 3. Driver Age Filter
Age brackets for more accurate premiums:
- 18-20 years (highest risk)
- 21-24 years (high risk)
- 25-34 years (standard)
- 35-49 years (experienced)
- 50-64 years (lowest risk)
- 65+ years (senior drivers)

### 4. Expandable Provider Cards
Each provider card can be expanded to show:
- Full description
- Available coverage types
- Feature list with checkmarks
- Benefit list with info icons
- Provider detail ranges
- Call-to-action buttons

### 5. Responsive Design
- **Mobile**: Single column, full-width cards
- **Tablet**: Two columns with stacked controls
- **Desktop**: Three-column controls, single column cards

## Color Scheme

### Provider Cards
- **Top Match**: Primary blue border (2px), elevation 4
- **Other Matches**: Light gray border (1px), elevation 2
- **Hover State**: Elevation increases to 4

### Match Score Chips
- **Best Match**: Gold star icon, primary color
- **Match Score**: Neutral gray
- **Rank**: Numbered badge

### Action Buttons
- **Get Quote**: Primary blue, opens in new tab
- **Select Provider**: Outlined gray, emits event to parent

## Accessibility

### ARIA Labels
- All interactive elements have descriptive ARIA labels
- Expand/collapse buttons announce state changes
- Links indicate they open in new tabs

### Keyboard Navigation
- Tab through controls and provider cards
- Enter/Space to expand/collapse details
- Arrow keys in dropdown menus

### Screen Reader Support
- Semantic HTML structure
- Descriptive text for all icons
- Proper heading hierarchy

## Error States

### Network Error
```
┌─────────────────────────────────────────────────────────┐
│ ❌ Network error: Unable to connect to insurance        │
│    service. Please check your connection.               │
└─────────────────────────────────────────────────────────┘
```

### No Matches
```
┌─────────────────────────────────────────────────────────┐
│ ℹ️ No insurance providers available for your criteria.  │
│   Try adjusting your coverage type or driver age.       │
└─────────────────────────────────────────────────────────┘
```

### Authentication Required
```
┌─────────────────────────────────────────────────────────┐
│ ❌ Authentication error: Please log in to view          │
│    insurance recommendations.                            │
└─────────────────────────────────────────────────────────┘
```

## Loading State

```
┌─────────────────────────────────────────────────────────┐
│                    🔄 Loading...                         │
│                                                          │
│       Finding the best insurance providers for you...   │
│                                                          │
│              ████████████████████                       │
└─────────────────────────────────────────────────────────┘
```

## Real-World Example

### Scenario: 30-year-old buying a 2021 Toyota Camry ($25,000)

**Input Parameters:**
- Vehicle Value: $25,000
- Vehicle Age: 3 years
- Vehicle Make: Toyota
- Vehicle Model: Camry
- Driver Age: 30
- Coverage Type: Full

**Expected Results:**
1. **Family First Insurance** - $300/month (Match Score: 72)
   - Reason: Comprehensive coverage • Rich features • Family-focused
2. **SafeGuard Auto Insurance** - $300/month (Match Score: 71)
   - Reason: Competitive pricing • Rich features
3. **Green Driver Insurance** - $320/month (Match Score: 68)
   - Reason: Eco-friendly options • Rich features

### Scenario: 18-year-old buying a 2018 Honda Civic ($15,000)

**Input Parameters:**
- Vehicle Value: $15,000
- Vehicle Age: 6 years
- Vehicle Make: Honda
- Vehicle Model: Civic
- Driver Age: 18
- Coverage Type: Liability

**Expected Results:**
1. **Value Coverage Insurance** - $200/month (Match Score: 75)
   - Reason: Excellent rates • Budget-friendly
2. **Family First Insurance** - $280/month (Match Score: 68)
   - Reason: Young driver programs • Teen monitoring
3. **SafeGuard Auto Insurance** - $260/month (Match Score: 65)
   - Reason: All credit scores accepted

**Note:** Young drivers see significantly higher premiums (2-2.5x multiplier)

## Integration in Evaluation Flow

The insurance recommendations component appears at the following point in the evaluation workflow:

```
1. Vehicle Summary
   ├── VIN, Make, Model, Year
   ├── Mileage, Price
   └── Condition

2. Overall Score
   ├── Deal Score (0-10)
   ├── Recommendation (Buy/Consider/Pass)
   └── Score Badge

3. Price Analysis
   ├── Asking Price
   ├── Fair Market Value
   └── Price Difference

4. Key Insights
   └── Market analysis points

5. Negotiation Strategy
   └── Numbered talking points

6. 🆕 Insurance Recommendations  ← NEW SECTION
   ├── Provider list
   ├── Premium estimates
   └── Interactive filters

7. Action Buttons
   ├── Go Back
   ├── Skip This Deal / View More Options
   └── Proceed with This Deal / Search More Vehicles
```

## Performance Metrics

### Load Time
- Initial component render: <100ms
- API call to backend: 200-500ms
- Total time to interactive: <1 second

### API Response Size
- Typical response: 5-15 KB
- With 5 providers: ~12 KB
- Gzipped: ~3 KB

### Caching Strategy
- No client-side caching by default
- Refetch on parameter changes
- Consider adding 5-minute cache for identical requests

## Future Enhancements

### Phase 1
- [ ] Save favorite providers
- [ ] Email quote comparison
- [ ] Share recommendations

### Phase 2
- [ ] Provider ratings display
- [ ] User reviews integration
- [ ] Multi-vehicle quotes

### Phase 3
- [ ] Real-time quote updates
- [ ] Chat with insurance agents
- [ ] Policy comparison tools
