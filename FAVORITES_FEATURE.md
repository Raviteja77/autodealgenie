# Favorites Feature

## Overview
The Favorites feature allows users to save vehicles they're interested in for quick access later. Users can add/remove vehicles from their favorites on the Results page and view all their saved favorites on a dedicated Favorites page.

## Backend Implementation

### API Endpoints
All endpoints are under `/api/v1/favorites` and require authentication.

#### GET `/api/v1/favorites/`
Get all favorites for the current user.

**Response:**
```json
[
  {
    "id": "1_1HGBH41JXMN109186",
    "user_id": 1,
    "vin": "1HGBH41JXMN109186",
    "make": "Toyota",
    "model": "Camry",
    "year": 2022,
    "price": 25000.00,
    "mileage": 15000,
    "fuel_type": "Gasoline",
    "location": "Los Angeles, CA",
    "color": "Silver",
    "condition": "Used",
    "image": "https://example.com/car.jpg",
    "created_at": "2024-12-19T12:00:00Z"
  }
]
```

#### POST `/api/v1/favorites/`
Add a vehicle to favorites.

**Request Body:**
```json
{
  "vin": "1HGBH41JXMN109186",
  "make": "Toyota",
  "model": "Camry",
  "year": 2022,
  "price": 25000.00,
  "mileage": 15000,
  "fuel_type": "Gasoline",
  "location": "Los Angeles, CA",
  "color": "Silver",
  "condition": "Used",
  "image": "https://example.com/car.jpg"
}
```

**Response:** 201 Created with the favorite object

#### DELETE `/api/v1/favorites/{vin}`
Remove a vehicle from favorites.

**Response:** 204 No Content

#### GET `/api/v1/favorites/{vin}`
Check if a specific vehicle is in favorites.

**Response:** 200 OK with the favorite object, or 404 Not Found

### Storage
Currently uses **in-memory Python dict** for temporary storage. This is suitable for development and testing but **should be replaced with persistent storage (PostgreSQL or MongoDB) for production**.

Structure: `{user_id: {vin: favorite_data}}`

### Testing
- 9 unit tests cover all endpoints
- Tests include authentication checks, duplicate prevention, and error handling
- Run tests: `cd backend && pytest tests/test_favorites.py -v`

## Frontend Implementation

### Pages

#### `/favorites` - Favorites Page
- Displays all saved vehicles in a grid layout
- Shows vehicle details (image, price, mileage, etc.)
- "Delete" button to remove from favorites
- "Negotiate" and "View Details" buttons for each vehicle
- Empty state when no favorites exist
- Server-side rendered with Next.js 14 App Router

### Navigation
- **Dashboard Search Page** (`/dashboard/search`): "My Favorites" button in the sidebar
- **Results Page** (`/dashboard/results`): "View Favorites" button in the header

### Favorites Toggle
On the Results page, each vehicle card has a heart icon:
- **Empty heart** (FavoriteBorderIcon): Not favorited
- **Filled red heart** (FavoriteIcon): Currently favorited
- Clicking toggles the favorite status via API calls
- Optimistic UI updates for smooth UX

### API Client
Added methods to `lib/api.ts`:
- `getFavorites()`: Fetch all favorites
- `addFavorite(favorite)`: Add to favorites
- `removeFavorite(vin)`: Remove from favorites
- `checkFavorite(vin)`: Check if favorited

### Error Handling
- Graceful fallbacks with user-friendly error messages
- Non-blocking errors for favorite sync issues
- Network error handling with retry suggestions

## UI Components Used
- **Custom Components**: Button, Card, Spinner (from `components/ui`)
- **Material-UI**: Grid, Box, Typography, IconButton, Alert, Divider
- **Icons**: FavoriteIcon, FavoriteBorderIcon, DeleteIcon, SpeedIcon, etc.

## Future Enhancements
1. **Persistent Storage**: Move from in-memory dict to PostgreSQL or MongoDB
2. **Favorite Notes**: Allow users to add personal notes to favorites
3. **Price Alerts**: Notify users when favorited vehicles drop in price
4. **Comparison View**: Side-by-side comparison of favorited vehicles
5. **Share Favorites**: Share favorite lists with friends/family
6. **Favorite Collections**: Organize favorites into custom collections
7. **Export Favorites**: Export as PDF or CSV for offline viewing

## Technical Details

### Type Safety
- Full TypeScript interfaces for frontend
- Pydantic schemas for backend validation
- Type-safe API client methods

### Authentication
- All endpoints require authentication via JWT tokens
- Favorites are user-specific (isolated by user_id)
- Proper 401 responses for unauthenticated requests

### Performance Considerations
- Frontend fetches favorites once on page load
- Optimistic updates for better UX
- Cached favorites state during navigation
- Minimal re-renders with proper React hooks

## Testing Checklist
- [x] Backend: Add favorite (POST)
- [x] Backend: Get all favorites (GET)
- [x] Backend: Get specific favorite (GET /{vin})
- [x] Backend: Remove favorite (DELETE)
- [x] Backend: Duplicate prevention
- [x] Backend: Authentication required
- [x] Frontend: Favorites page renders
- [x] Frontend: Heart icon toggles
- [x] Frontend: Navigation buttons work
- [x] Frontend: Error handling
- [ ] Manual: Full user flow testing
- [ ] Manual: UI screenshots

## Known Limitations
1. **In-Memory Storage**: Favorites are lost on server restart
2. **No Pagination**: All favorites loaded at once (may be slow with many favorites)
3. **No Sorting/Filtering**: Favorites displayed in insertion order only
4. **No Bulk Operations**: Cannot favorite/unfavorite multiple vehicles at once
