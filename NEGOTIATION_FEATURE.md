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

2. **Chat Interface (Center)** - **REDESIGNED**
   - Tabbed interface with two modes:
     - **Actions Tab**: Traditional negotiation actions (Accept, Counter, Reject)
     - **Chat Tab**: Free-form chat with AI expert for questions and advice
   - Message display with role-based styling
   - Collapsible round-based grouping
   - Enhanced typing indicators
   - Support for dealer-provided information analysis
   - Real-time message validation
   - Error boundaries with user-friendly messages

3. **AI Assistant Panel (Right Sidebar)**
   - Confidence score visualization
   - Real-time recommendations
   - Strategy tips
   - Market insights
   - Financing options display

### Backend Services

**Location**: `backend/app/api/v1/endpoints/negotiation.py`

#### Endpoints

1. **POST `/api/v1/negotiations/`**
   - Creates a new negotiation session
   - Seeds round 1 with user's initial message
   - Returns AI agent's initial response
   - Broadcasts initial messages via WebSocket
   - **Authentication Required**: Yes

2. **POST `/api/v1/negotiations/{session_id}/next`**
   - Processes the next negotiation round
   - Handles user actions: `confirm`, `reject`, `counter`
   - Generates AI responses using LLM
   - Broadcasts messages in real-time via WebSocket
   - **Authentication Required**: Yes

3. **GET `/api/v1/negotiations/{session_id}`**
   - Retrieves full negotiation session with message history
   - **Authentication Required**: Yes

4. **POST `/api/v1/negotiations/{session_id}/chat`**
   - Sends free-form chat messages during negotiation
   - Allows users to ask questions without committing to actions
   - Provides strategic advice and guidance
   - Broadcasts messages via WebSocket for instant delivery
   - **Authentication Required**: Yes

5. **POST `/api/v1/negotiations/{session_id}/dealer-info`**
   - Submits dealer-provided information for AI analysis
   - Supports quotes, inspection reports, and additional offers
   - Provides recommendations on how to respond
   - **Authentication Required**: Yes

6. **WebSocket `/api/v1/negotiations/{session_id}/ws`** - **NEW**
   - Real-time bidirectional communication channel
   - Instant message delivery (< 100ms)
   - Typing indicators during AI response generation
   - Automatic reconnection with exponential backoff
   - Keep-alive ping/pong mechanism (30s interval)
   - **Message Types**:
     - Server → Client:
       - `new_message`: New negotiation message
       - `typing_indicator`: AI typing status
       - `error`: Error notification
       - `pong`: Keep-alive response
       - `subscribed`: Subscription confirmation
     - Client → Server:
       - `ping`: Keep-alive ping
       - `subscribe`: Subscribe to updates
   - **Authentication**: User-based (JWT) authentication via cookies. The authenticated user must own the session or the connection is rejected.

### Database Schema

**Tables**:
- `negotiation_sessions` - Session metadata (status, rounds, timestamps)
- `negotiation_messages` - Individual messages with metadata (including chat messages and dealer info)
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

Users can interact with the negotiation in multiple ways:

**Traditional Actions (Actions Tab)**

**Accept Current Offer**
- Marks session as "completed"
- Shows success screen with deal summary
- Displays financing options and lender recommendations
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

**Free-Form Chat (Chat Tab)** - **NEW**

Users can now engage in open conversation with the AI negotiation expert:

**Ask Questions**
- Get strategic advice about the negotiation
- Understand market conditions
- Learn about negotiation tactics
- Clarify pricing or vehicle details

**Share Dealer Information**
- Submit price quotes from dealers
- Share inspection reports
- Provide additional offers or counteroffers
- Get AI analysis and recommendations on how to respond

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

### Chat Context Provider - **NEW**

**Location**: `frontend/app/context/NegotiationChatProvider.tsx`

The `NegotiationChatProvider` manages the state for free-form chat messages and WebSocket connection:

```typescript
interface ChatContextType {
  messages: NegotiationMessage[];     // Chat messages (separate from negotiation actions)
  isTyping: boolean;                  // AI typing indicator
  isSending: boolean;                 // Message sending state
  error: string | null;               // Error message
  sessionId: number | null;           // Associated session
  wsConnected: boolean;               // WebSocket connection status
  
  // Methods
  setSessionId: (id: number) => void;
  setMessages: (messages: NegotiationMessage[]) => void;
  sendChatMessage: (message: string, messageType?: string) => Promise<void>;
  sendDealerInfo: (type: string, content: string, price?: number) => Promise<void>;
  clearError: () => void;
  resetChat: () => void;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;
}
```

**Usage**:
```typescript
import { useNegotiationChat } from "@/app/context";

const { sendChatMessage, sendDealerInfo, isTyping, error, wsConnected } = useNegotiationChat();
```

**WebSocket Features**:
- **Auto-connect**: Automatically connects when session ID is set
- **Auto-reconnect**: Exponential backoff (max 5 attempts) on disconnect
- **Message Deduplication**: Prevents duplicate messages from API + WebSocket
- **Keep-alive**: Ping/pong every 30 seconds to maintain connection
- **Real-time Updates**: Messages appear instantly (< 100ms)
- **Typing Indicators**: Shows when AI is generating response
- **Connection Status**: Visible indicator in chat header

## Real-Time Communication

### WebSocket Architecture

**Backend Components:**
- `websocket_manager.py`: Connection manager for WebSocket clients
  - Maintains pool of active connections per session
  - Handles broadcasting to all connected clients
  - Manages cleanup of disconnected clients
- `negotiation_service.py`: Integrates WebSocket broadcasting
  - Broadcasts messages after saving to database
  - Sends typing indicators during AI generation
  - Handles errors gracefully (WebSocket failures don't break API)

**Frontend Components:**
- `NegotiationChatProvider.tsx`: WebSocket client implementation
  - Establishes connection on session creation
  - Handles incoming messages and updates state
  - Implements reconnection logic with exponential backoff
  - Provides connection status to UI

### Message Flow

1. **User Sends Message**:
   ```
   User types message → API call to backend → Save to DB
   → Broadcast via WebSocket → All clients receive instantly
   → Update UI
   ```

2. **AI Generates Response**:
   ```
   API processes message → Show typing indicator (WebSocket)
   → AI generates response → Hide typing indicator (WebSocket)
   → Save response to DB → Broadcast via WebSocket
   → Update UI
   ```

3. **Connection Handling**:
   ```
   Page loads → Auto-connect WebSocket
   → Connection drops → Exponential backoff reconnection
   → Max attempts reached → Show error, suggest refresh
   ```

### Reliability Features

- **Dual Delivery**: Messages sent via both API and WebSocket
  - API provides reliability (always works)
  - WebSocket provides speed (instant delivery)
  - Deduplication prevents showing same message twice
- **Automatic Reconnection**: Up to 5 attempts with exponential backoff
- **Graceful Degradation**: App works without WebSocket (just slower)
- **Keep-alive**: Prevents proxy/firewall timeouts
- **Error Handling**: Connection errors shown to user with retry options

## AI Integration

The negotiation feature uses LangChain with OpenAI for intelligent, **user-centric** responses:

**Prompts Used**:
- `negotiation_initial` - First response to user's interest (favors user, suggests starting low)
- `negotiation_counter` - Response to user's counter offers (encourages aggressive negotiation)
- `negotiation_chat` - Responses to free-form chat messages (provides tactical advice)
- `dealer_info_analysis` - Analysis of dealer-provided information

**Prompt Templates**: `backend/app/llm/prompts.py`

**Key AI Principles**:
1. **User Advocacy**: AI explicitly works for the buyer, not the dealer
2. **Aggressive Negotiation**: Encourages users to push for lower prices
3. **Strategic Advice**: Provides specific tactics and talking points
4. **Market Context**: References vehicle condition, age, mileage in recommendations

### User-Centric Pricing Strategy

The AI uses a **buyer-focused pricing algorithm** that prioritizes getting the best deal for the user:

**Initial Offer Strategy:**
```python
# Start significantly BELOW user's target price to maximize negotiating room
suggested_price = user_target_price * 0.87  # 13% below target
```

**Counter Offer Strategy (based on current discount):**
```python
discount_percent = ((asking_price - counter_offer) / asking_price) * 100

if discount_percent >= 10:
    # User already getting 10%+ off - hold firm
    new_suggested_price = counter_offer * 1.01  # Only 1% increase
elif discount_percent >= 5:
    # User getting 5-10% off - minimal increase
    new_suggested_price = counter_offer * 1.02  # 2% increase
else:
    # User not getting good deal yet - go LOWER
    new_suggested_price = counter_offer * 0.98  # 2% DECREASE
```

**Benefits of This Approach:**
- **Aggressive Start**: User starts low with room to negotiate up
- **Reward Good Deals**: When user gets significant discount, AI encourages holding position
- **Pressure Dealers**: When discount is low, AI suggests going even lower
- **User Empowerment**: Never suggests meeting in the middle or favoring dealer

**Old vs New Comparison:**
- **Old**: Initial offer = middle ground (50% between target and asking)
- **New**: Initial offer = 13% below target price
- **Old**: Counter = converge toward asking price
- **New**: Counter = hold firm or go lower based on discount achieved

This ensures:
- Users always get strategic advice that benefits them
- Negotiations favor the buyer, not the seller
- AI acts as user's advocate throughout the process

## UI Components

### Custom Components Used

All UI components follow the project's component library pattern:

- **Button** (`components/ui/Button.tsx`) - Primary, secondary, success, danger, outline variants
- **Card** (`components/ui/Card.tsx`) - Container with header, body, footer sections
- **Modal** (`components/ui/Modal.tsx`) - Dialog overlays for confirmations
- **Spinner** (`components/ui/Spinner.tsx`) - Loading indicators
- **ChatInput** (`components/ChatInput.tsx`) - **NEW** - Text input with dealer info support

### ChatInput Component - **NEW**

**Location**: `frontend/components/ChatInput.tsx`

A specialized input component for the negotiation chat:

**Features**:
- Multiline text input with character counter
- Support for regular messages and dealer information
- Dealer info mode with type selector and price input
- Validation (1-2000 characters for messages, 1-5000 for dealer info)
- Loading states and error handling
- Keyboard shortcuts (Enter to send, Shift+Enter for newline)

**Props**:
```typescript
interface ChatInputProps {
  onSendMessage: (message: string, type?: string) => Promise<void>;
  onSendDealerInfo?: (type: string, content: string, price?: number) => Promise<void>;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}
```

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
