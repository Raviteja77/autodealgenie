# Negotiation Feature Documentation

## Overview

The Negotiation Feature provides an interactive, AI-powered negotiation experience for car buyers. Users can engage in multi-round negotiations with an AI assistant that helps them secure the best deal on their chosen vehicle.

## Architecture

### Frontend Components

**Location**: `frontend/app/dashboard/negotiation/page.tsx`

The negotiation page is organized into three main panels:

1. **Price Tracking Panel (Left Sidebar)**
   - Vehicle details and specifications
   - Price metrics (asking price, target price, current offer)
   - Visual progress indicators
   - Round progression tracker

2. **Chat Interface (Center)**
   - Message display with role-based styling
   - Collapsible round-based grouping
   - Typing indicators
   - Action buttons (Accept, Counter, Reject)

3. **AI Assistant Panel (Right Sidebar)**
   - Confidence score visualization
   - Real-time recommendations
   - Strategy tips
   - Market insights

### Backend Services

**Location**: `backend/app/api/v1/endpoints/negotiation.py`

#### Endpoints

1. **POST `/api/v1/negotiations/`**
   - Creates a new negotiation session
   - Seeds round 1 with user's initial message
   - Returns AI agent's initial response
   - **Authentication Required**: Yes

2. **POST `/api/v1/negotiations/{session_id}/next`**
   - Processes the next negotiation round
   - Handles user actions: `confirm`, `reject`, `counter`
   - Generates AI responses using LLM
   - **Authentication Required**: Yes

3. **GET `/api/v1/negotiations/{session_id}`**
   - Retrieves full negotiation session with message history
   - **Authentication Required**: Yes

### Database Schema

**Tables**:
- `negotiation_sessions` - Session metadata (status, rounds, timestamps)
- `negotiation_messages` - Individual messages with metadata
- `deals` - Associated deal information

**See**: `backend/app/models/negotiation.py` for model definitions

## User Flow

### 1. Initialization

```typescript
// User navigates to negotiation page with vehicle details in URL params
// Example: /dashboard/negotiation?make=Toyota&model=Camry&year=2023&price=25000...

// System automatically:
1. Creates a Deal record
2. Initializes a NegotiationSession
3. Sends user's target price to backend
4. Receives AI's initial response
```

### 2. Active Negotiation

Users can take three actions each round:

**Accept Current Offer**
- Marks session as "completed"
- Shows success screen with deal summary
- Allows user to proceed to evaluation

**Make Counter Offer**
- Opens modal for price input
- Validates counter offer
- Increments round number
- AI generates counter-counter offer

**Reject/Exit**
- Marks session as "cancelled"
- Shows cancellation screen
- Provides navigation to other pages

### 3. Deal Outcomes

**Successful Completion**
- Displays congratulations screen
- Shows price comparison (original vs. final)
- Calculates savings
- Provides options to evaluate deal or search more vehicles

**Cancellation**
- Displays cancellation notice
- Offers navigation to search or results pages

## State Management

### NegotiationState Interface

```typescript
interface NegotiationState {
  sessionId: number | null;           // Current session ID
  status: "idle" | "active" | "completed" | "cancelled";
  dealId: number | null;              // Associated deal ID
  vehicleData: VehicleInfo | null;    // Vehicle details
  targetPrice: number | null;         // User's target price
  currentRound: number;               // Current negotiation round
  maxRounds: number;                  // Maximum allowed rounds (default: 10)
  messages: NegotiationMessage[];     // Conversation history
  suggestedPrice: number | null;      // AI's current suggested price
  confidence: number | null;          // Deal confidence score (0-1)
  isLoading: boolean;                 // Loading state
  error: string | null;               // Error message
  isTyping: boolean;                  // AI typing indicator
}
```

## AI Integration

The negotiation feature uses LangChain with OpenAI for intelligent responses:

**Prompts Used**:
- `negotiation_initial` - First response to user's interest
- `negotiation_counter` - Response to user's counter offers

**Prompt Templates**: `backend/app/llm/prompts.py`

### Price Convergence Algorithm

The AI uses a convergence strategy to move negotiations toward a middle ground:

```python
# Calculate new suggested price
price_difference = asking_price - counter_offer
convergence_rate = 1 - (current_round / max_rounds)
new_suggested_price = counter_offer + (price_difference * convergence_rate * 0.6)
```

This ensures:
- Offers gradually converge toward asking price
- Faster convergence as rounds progress
- Realistic negotiation dynamics

## UI Components

### Custom Components Used

All UI components follow the project's component library pattern:

- **Button** (`components/ui/Button.tsx`) - Primary, secondary, success, danger, outline variants
- **Card** (`components/ui/Card.tsx`) - Container with header, body, footer sections
- **Modal** (`components/ui/Modal.tsx`) - Dialog overlays for confirmations
- **Spinner** (`components/ui/Spinner.tsx`) - Loading indicators

### Material-UI Components

- Layout: Grid, Box, Container, Stack
- Display: Typography, Divider, Chip, Avatar
- Feedback: Alert, LinearProgress, Collapse
- Input: TextField, IconButton

## Error Handling

### Frontend Error States

1. **Invalid Vehicle Data**
   - Shows error alert with navigation back to results
   - Prevents session initialization

2. **API Failures**
   - Catches and displays user-friendly error messages
   - Maintains UI state for recovery

3. **Authentication Issues**
   - Redirects to login if unauthenticated
   - Uses AuthProvider context

### Backend Error Responses

- **404**: Session or deal not found
- **403**: User doesn't own the session
- **400**: Invalid actions (max rounds, invalid counter offer)
- **500**: Server errors (LLM failures use fallback responses)

## Mock Services

For testing without a backend, mock endpoints are available:

**Enable Mock Mode**:
```bash
# Set in .env
NEXT_PUBLIC_USE_MOCK=true
```

**Mock Endpoints**:
- `/mock/negotiation/create` - Create session
- `/mock/negotiation/{session_id}/next` - Next round
- `/mock/negotiation/{session_id}` - Get session

**Location**: `backend/app/api/mock/mock_services.py`

## Testing

### Manual Testing Checklist

- [ ] Navigate to negotiation page with valid vehicle params
- [ ] Verify session initialization and first AI message
- [ ] Test counter offer submission
- [ ] Verify round progression and message history
- [ ] Test accept offer flow
- [ ] Test reject/cancel flow
- [ ] Verify price progress indicators update correctly
- [ ] Check responsive design on mobile devices
- [ ] Test error states (invalid data, network failures)
- [ ] Verify collapsible round sections work
- [ ] Test modal dialogs (counter offer, confirmations)
- [ ] Verify notifications appear and auto-dismiss

### Integration Testing

1. **Backend Tests**: `backend/tests/test_negotiation.py`
2. **API Client**: Test negotiation API methods in `lib/api.ts`
3. **UI Components**: Test button actions and state updates

## Configuration

### Environment Variables

**Frontend** (`.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_USE_MOCK=false  # Set to true for mock mode
```

**Backend** (`.env`):
```bash
USE_MOCK_SERVICES=false  # Enable mock services
OPENAI_API_KEY=your_key_here  # Required for LLM integration
```

### Customization Options

**Max Rounds**: Adjust in negotiation service
```python
# backend/app/repositories/negotiation_repository.py
max_rounds=10  # Change default max rounds
```

**Target Price Calculation**: Adjust in frontend
```typescript
// frontend/app/dashboard/negotiation/page.tsx
const targetPrice = vehicleData.price * 0.9;  // 10% below asking
```

**Confidence Score**: Customize in AI insights panel
```typescript
// Current: 0.85 default, updates based on deal quality
confidence: 0.85  // Adjust initial confidence
```

## Performance Considerations

### Optimizations

1. **Auto-scroll**: Uses `useCallback` to prevent unnecessary re-renders
2. **Round Expansion**: Controlled by Set for efficient lookups
3. **Message Grouping**: Computed with `useMemo` for performance
4. **Notification Timeout**: Auto-dismisses after 5 seconds

### Best Practices

- Session initialization happens once on mount
- API calls use proper error boundaries
- Loading states prevent duplicate requests
- Messages are batched by round for better UX

## Future Enhancements

### Planned Features

1. **Voice Input**: Allow users to speak counter offers
2. **Document Upload**: Attach inspection reports or service records
3. **Multiple Dealers**: Compare offers from different dealers
4. **Negotiation Templates**: Pre-built strategies for different scenarios
5. **Historical Analytics**: Track negotiation success rates
6. **Real-time Notifications**: WebSocket updates for dealer responses
7. **Mobile App**: Native mobile experience

### Technical Improvements

1. **Conversation Persistence**: Save drafts and resume sessions
2. **Advanced Analytics**: Deal quality scoring with more factors
3. **A/B Testing**: Test different negotiation strategies
4. **Performance Monitoring**: Track API response times
5. **Internationalization**: Support multiple languages

## Troubleshooting

### Common Issues

**Issue**: Session initialization fails
- **Solution**: Check authentication status and vehicle data in URL params

**Issue**: AI responses are slow
- **Solution**: Verify OPENAI_API_KEY is set and valid. Check LLM service logs.

**Issue**: Counter offers don't update price
- **Solution**: Ensure backend is processing metadata correctly. Check network tab for response.

**Issue**: Messages not displaying
- **Solution**: Verify session ID is valid and messages array is populated.

### Debug Mode

Enable detailed logging:
```typescript
// Add to negotiation page
useEffect(() => {
  console.log("Negotiation State:", state);
}, [state]);
```

## Contributing

When extending the negotiation feature:

1. Follow existing TypeScript patterns
2. Use custom UI components from `components/ui/`
3. Add proper error handling for all API calls
4. Update this documentation with new features
5. Test in both real and mock modes
6. Ensure responsive design works on mobile

## Related Documentation

- [Authentication Documentation](AUTHENTICATION.md)
- [UI Components Guide](UI_COMPONENTS_MUI.md)
- [LLM Module Usage](backend/LLM_MODULE_USAGE.md)
- [Error Handling](ERROR_HANDLING.md)
- [Mock Services Guide](MOCK_SERVICES_GUIDE.md)
