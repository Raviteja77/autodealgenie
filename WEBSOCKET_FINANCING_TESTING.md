# WebSocket Reliability & Financing Options - Testing Guide

## Overview
This document provides comprehensive testing guidelines for the WebSocket reliability improvements and financing comparison modal features implemented in this PR.

## WebSocket Reliability Features

### 1. Connection Status Indicator

#### Test Scenario 1: Normal Connection
**Steps:**
1. Navigate to the negotiation page
2. Observe the connection status indicator in the chat header

**Expected Results:**
- Status chip shows "Connected" with a green WiFi icon
- No reconnection attempts displayed
- No queued messages shown

#### Test Scenario 2: Connection Loss
**Steps:**
1. Start a negotiation session
2. Disconnect network or stop the backend server
3. Observe the connection status changes

**Expected Results:**
- Status changes from "Connected" → "Disconnected"
- Status then changes to "Reconnecting (1/5)" → "Reconnecting (2/5)" etc.
- Progress bar shows reconnection attempts
- Manual reconnect button appears after connection loss

#### Test Scenario 3: Manual Reconnect
**Steps:**
1. While disconnected, click the manual reconnect button (circular arrow icon)
2. Observe the reconnection process

**Expected Results:**
- Reconnection attempts reset to 0
- Status changes to "Connecting"
- Connection re-established successfully if server is available

### 2. Offline Message Queuing

#### Test Scenario 1: Queue Messages While Offline
**Steps:**
1. Start a negotiation session
2. Disconnect network or stop backend
3. Type and send 2-3 messages using the chat input
4. Observe the queue indicator

**Expected Results:**
- Messages are added to the queue
- Queue indicator chip appears showing message count (e.g., "2")
- Messages show as "queued" status
- No error messages displayed

#### Test Scenario 2: Automatic Message Retry
**Steps:**
1. Queue messages while offline (as above)
2. Restore network connection or restart backend
3. Wait for automatic reconnection

**Expected Results:**
- WebSocket reconnects automatically
- Queued messages are sent automatically in order
- Queue indicator count decreases as messages are sent
- Messages appear in chat history
- AI responses received for each message

#### Test Scenario 3: Queue Size Limit
**Steps:**
1. While disconnected, attempt to send more than 50 messages

**Expected Results:**
- Error message displayed: "Message queue is full. Please wait for connection to restore."
- Additional messages not added to queue
- Existing queued messages remain intact

### 3. HTTP Fallback Mode

#### Test Scenario 1: Fallback Activation
**Steps:**
1. Start a negotiation session
2. Block WebSocket connection (but allow HTTP)
3. Wait for max reconnection attempts (5)

**Expected Results:**
- After 5 failed reconnection attempts, status changes to "Fallback Mode"
- Error chip shows "Fallback Mode" instead of "Connection Error"
- Messages can still be sent via HTTP API
- No real-time updates, but messages work via polling

#### Test Scenario 2: Fallback Message Sending
**Steps:**
1. In fallback mode, send messages via chat
2. Observe message delivery

**Expected Results:**
- Messages sent via HTTP POST
- User and AI messages appear in chat
- Slight delay compared to WebSocket
- No connection errors shown

### 4. Message Synchronization

#### Test Scenario 1: Sync Missed Messages
**Steps:**
1. Start negotiation session
2. Disconnect for 2 minutes
3. During disconnect, have another user/session send messages
4. Reconnect

**Expected Results:**
- On reconnection, all missed messages are fetched from server
- Messages appear in correct chronological order
- No duplicate messages
- Message history is complete

## Financing Comparison Modal Features

### 1. Modal Display

#### Test Scenario 1: Open Modal
**Steps:**
1. Navigate to negotiation page with financing options
2. Click "Compare All Options" button in the financing panel

**Expected Results:**
- Modal opens with full-screen overlay
- Title: "Financing Comparison & Calculator"
- All financing options displayed
- Cash savings alert shown prominently at top

#### Test Scenario 2: Modal Tabs
**Steps:**
1. Open financing comparison modal
2. Click through all three tabs

**Expected Results:**
- Tab 1: "Side-by-Side" - Shows cards for each financing option
- Tab 2: "Payment Chart" - Shows horizontal bar chart with monthly payments
- Tab 3: "Cost Breakdown" - Shows detailed table with all costs
- Smooth transition between tabs
- Data consistent across all views

### 2. Interactive Calculator

#### Test Scenario 1: Price Adjustment
**Steps:**
1. Open modal
2. Change purchase price in the calculator
3. Observe payment updates

**Expected Results:**
- Monthly payments recalculated immediately
- Total costs updated
- Interest amounts adjusted
- Best option may change based on new price
- All three tabs reflect new calculations

#### Test Scenario 2: Down Payment Slider
**Steps:**
1. Open modal
2. Adjust down payment slider from 0% to 50%
3. Observe changes

**Expected Results:**
- Down payment amount updates in real-time
- Loan amounts decrease as down payment increases
- Monthly payments decrease
- Total interest decreases
- All values update smoothly

### 3. Cash Savings Highlight

#### Test Scenario 1: Cash Savings Display
**Steps:**
1. Open modal with vehicle that has financing options
2. Observe cash savings alert at top

**Expected Results:**
- Green success alert prominently displayed
- Shows exact savings amount (e.g., "$2,500")
- Contextual message: "Save $X by paying cash instead of financing!"
- "Best Option: Pay Cash" chip displayed
- Alert includes icon (💰)

#### Test Scenario 2: Cash vs Financing Table
**Steps:**
1. Navigate to "Cost Breakdown" tab
2. Scroll to bottom of table

**Expected Results:**
- Last row shows "Cash" option
- Highlighted in light green
- Shows $0 interest
- Total cost equals purchase price only
- Clearly identified as best value option

### 4. Best Option Highlighting

#### Test Scenario 1: Best Financing Option
**Steps:**
1. Open modal
2. View "Side-by-Side" tab

**Expected Results:**
- One financing option has blue border (primary color)
- "Best Value" chip displayed on that option
- Option with lowest total cost is highlighted
- Highlighting persists across tab changes

#### Test Scenario 2: Dynamic Best Option
**Steps:**
1. Open modal
2. Adjust price or down payment
3. Observe best option changes

**Expected Results:**
- Best option recalculated based on new total cost
- Highlighting moves to new best option
- Updates immediately on slider/input change

### 5. Visual Comparison Charts

#### Test Scenario 1: Payment Chart
**Steps:**
1. Navigate to "Payment Chart" tab
2. Observe bar chart

**Expected Results:**
- Horizontal bars showing monthly payment amounts
- Bar length proportional to payment amount
- Best option bar in blue, others in gray
- APR rate displayed on each bar
- Exact payment amount shown on right

#### Test Scenario 2: Cost Breakdown Table
**Steps:**
1. Navigate to "Cost Breakdown" tab
2. Review table data

**Expected Results:**
- Columns: Term, Loan Amount, Down Payment, Monthly, Total Interest, Total Cost
- All values formatted with $ and commas
- Interest shown in warning color (orange/yellow)
- Best option row highlighted
- Cash row at bottom in success color

## Integration Testing

### Test Scenario 1: End-to-End Negotiation with Financing
**Steps:**
1. Start vehicle search
2. Select a vehicle
3. Begin negotiation
4. Accept an offer
5. View financing options
6. Open comparison modal
7. Compare options
8. Continue with selected option

**Expected Results:**
- Smooth flow through entire process
- WebSocket maintains connection throughout
- Financing options appear after deal acceptance
- Modal displays all calculated options correctly
- No errors or broken functionality

### Test Scenario 2: Connection Recovery During Financing
**Steps:**
1. Open financing modal
2. Disconnect network
3. Adjust calculator values
4. Reconnect network
5. Close modal and send negotiation message

**Expected Results:**
- Modal continues to work offline (calculations only)
- No server calls made while offline
- WebSocket reconnects on network restore
- Subsequent messages sent successfully
- No data loss or corruption

## Performance Testing

### Test Scenario 1: Message Queue Performance
**Steps:**
1. Queue 50 messages while offline
2. Reconnect
3. Observe message processing

**Expected Results:**
- Messages processed within 30 seconds
- No browser freeze or lag
- UI remains responsive
- All messages delivered successfully

### Test Scenario 2: Modal Responsiveness
**Steps:**
1. Open modal with multiple financing options
2. Rapidly adjust price slider
3. Switch between tabs quickly

**Expected Results:**
- Calculations update smoothly (<100ms)
- No lag or stuttering
- Tab transitions are smooth
- No visual glitches

## Accessibility Testing

### Test Scenario 1: Keyboard Navigation
**Steps:**
1. Use Tab key to navigate through connection status
2. Use Tab to navigate through modal
3. Use Enter to activate buttons

**Expected Results:**
- All interactive elements focusable
- Focus indicators visible
- Tab order logical
- Enter key activates buttons
- Escape closes modal

### Test Scenario 2: Screen Reader Support
**Steps:**
1. Use screen reader to navigate connection status
2. Use screen reader in modal

**Expected Results:**
- Connection status announces current state
- Modal title read correctly
- All labels and values announced
- Alerts read immediately on change

## Browser Compatibility

Test all scenarios in:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Mobile Testing

Test responsive behavior on:
- Mobile portrait mode (320px - 480px)
- Mobile landscape mode (480px - 768px)
- Tablet mode (768px - 1024px)

**Expected Results:**
- Modal stacks vertically on mobile
- Calculator controls remain usable
- Connection status indicator readable
- Touch targets adequately sized (44px min)

## Error Scenarios

### Test Scenario 1: Server Error During Send
**Steps:**
1. Connected state
2. Send message that causes 500 error
3. Observe error handling

**Expected Results:**
- Error message displayed
- Message not lost
- User can retry
- Connection remains stable

### Test Scenario 2: Network Timeout
**Steps:**
1. Simulate slow network (high latency)
2. Send messages
3. Observe behavior

**Expected Results:**
- Timeout handled gracefully
- Messages queued if timeout occurs
- User informed of delay
- Automatic retry on timeout

## Notes for Manual Testing

1. **Backend Required**: WebSocket features require running FastAPI backend
2. **Environment Variables**: Ensure `NEXT_PUBLIC_API_URL` is set correctly
3. **Console Logs**: Check browser console for detailed connection logs
4. **Network Tab**: Use browser DevTools Network tab to observe WebSocket frames
5. **State Persistence**: Test page refresh to ensure state is not lost unexpectedly

## Known Limitations

1. Message queue limited to 50 messages to prevent memory issues
2. WebSocket reconnection limited to 5 attempts before fallback
3. Financing calculations assume simple interest (not compound)
4. Modal requires minimum 3 financing options for best display
5. Connection status updates may have slight delay (polling interval)

## Success Criteria

All features are considered successfully implemented when:
- ✅ All test scenarios pass
- ✅ No console errors during normal operation
- ✅ Connection recovers automatically from brief disconnects
- ✅ Messages are never lost
- ✅ Financing calculations are accurate
- ✅ Modal is responsive and performant
- ✅ User experience is smooth and intuitive
