# User Preferences Service

This service manages user car search preferences using MongoDB for storage. It provides CRUD operations for storing, retrieving, updating, and cleaning up user preferences.

## Features

- **Save User Preferences**: Store user search criteria in MongoDB
- **Retrieve Preferences**: Fetch all saved searches for a specific user
- **Update Preferences**: Overwrite existing preferences with new definitions
- **Automatic Cleanup**: Delete preferences older than a specified number of days

## Service API

### Class: `UserPreferencesService`

#### Methods

##### `save_user_preferences(user_id: str, **kwargs) -> None`
Save user search criteria to MongoDB.

**Parameters:**
- `user_id` (str): User identifier
- `makes` (list[str] | None): List of preferred car makes
- `budget_range` (dict[str, int] | None): Budget range with `min` and `max` keys
- `year_range` (dict[str, int] | None): Year range with `min` and `max` keys
- `body_types` (list[str] | None): List of preferred body types
- `features` (list[str] | None): List of desired features

**Example:**
```python
await user_preferences_service.save_user_preferences(
    user_id="user123",
    makes=["Toyota", "Honda"],
    budget_range={"min": 20000, "max": 35000},
    year_range={"min": 2020, "max": 2024},
    body_types=["sedan", "suv"],
    features=["sunroof", "leather seats"]
)
```

##### `get_user_preferences(user_id: str) -> list[dict[str, Any]]`
Retrieve all saved searches for a specific user.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- List of user preference documents sorted by creation date (newest first)

**Example:**
```python
preferences = await user_preferences_service.get_user_preferences("user123")
for pref in preferences:
    print(f"Created: {pref['created_at']}")
    print(f"Makes: {pref['preferences']['makes']}")
```

##### `update_user_preferences(user_id: str, **kwargs) -> None`
Update existing preferences by creating a new document with updated timestamp.

**Parameters:**
- `user_id` (str): User identifier
- `makes` (list[str] | None): Updated list of preferred car makes
- `budget_range` (dict[str, int] | None): Updated budget range
- `year_range` (dict[str, int] | None): Updated year range
- `body_types` (list[str] | None): Updated list of preferred body types
- `features` (list[str] | None): Updated list of desired features

**Note:** Only provided fields will be updated; others will be preserved from the most recent preference.

**Example:**
```python
await user_preferences_service.update_user_preferences(
    user_id="user123",
    makes=["BMW", "Mercedes"],
    budget_range={"min": 30000, "max": 50000}
)
```

##### `delete_older_preferences(days: int = 30) -> int`
Delete preferences older than specified number of days.

**Parameters:**
- `days` (int): Number of days (default: 30)

**Returns:**
- Number of documents deleted

**Example:**
```python
deleted_count = await user_preferences_service.delete_older_preferences(days=60)
print(f"Deleted {deleted_count} old preferences")
```

## REST API Endpoints

### Base URL: `/api/v1/users`

#### POST `/preferences/{user_id}`
Save new user preferences.

**Request Body:**
```json
{
  "makes": ["Toyota", "Honda"],
  "budget_range": {"min": 20000, "max": 35000},
  "year_range": {"min": 2020, "max": 2024},
  "body_types": ["sedan", "suv"],
  "features": ["sunroof", "leather seats"]
}
```

**Response:**
```json
{
  "message": "Preferences saved successfully",
  "user_id": "user123"
}
```

#### GET `/preferences/{user_id}`
Retrieve all preferences for a user.

**Response:**
```json
{
  "user_id": "user123",
  "preferences": [
    {
      "user_id": "user123",
      "preferences": {
        "makes": ["Toyota", "Honda"],
        "budget_range": {"min": 20000, "max": 35000},
        "year_range": {"min": 2020, "max": 2024},
        "body_types": ["sedan", "suv"],
        "features": ["sunroof", "leather seats"]
      },
      "created_at": "2024-12-14T23:00:00Z",
      "updated_at": "2024-12-14T23:00:00Z"
    }
  ],
  "count": 1
}
```

#### PUT `/preferences/{user_id}`
Update existing preferences.

**Request Body:** (same as POST, but only provided fields will be updated)

**Response:**
```json
{
  "message": "Preferences updated successfully",
  "user_id": "user123"
}
```

#### DELETE `/preferences/cleanup?days=30`
Clean up old preferences.

**Query Parameters:**
- `days` (int, default: 30): Number of days

**Response:**
```json
{
  "message": "Cleanup completed",
  "deleted_count": 5,
  "days": 30
}
```

## MongoDB Schema

### Collection: `user_preferences`

```javascript
{
  "user_id": "string",
  "preferences": {
    "makes": ["string"],
    "budget_range": {
      "min": number,
      "max": number
    },
    "year_range": {
      "min": number,
      "max": number
    },
    "body_types": ["string"],
    "features": ["string"]
  },
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```

## Testing

The service includes comprehensive unit tests with 98% code coverage. Tests use mocked MongoDB operations to avoid external dependencies.

**Run tests:**
```bash
cd backend
pytest tests/test_user_preferences_service.py -v
```

**Test coverage:**
```bash
pytest tests/test_user_preferences_service.py --cov=app.services.user_preferences_service
```

## Integration

The service is exported as a singleton instance from `app.services`:

```python
from app.services import user_preferences_service

# Use the service
await user_preferences_service.save_user_preferences(...)
```

## Design Decisions

1. **Immutable History**: Updates create new documents rather than modifying existing ones, preserving user preference history.
2. **Singleton Pattern**: Service is instantiated once and shared across the application.
3. **Lazy Collection Loading**: MongoDB collection is loaded on first access via property.
4. **UTC Timestamps**: All timestamps use UTC timezone for consistency.
5. **Flexible Schema**: Optional parameters allow partial data storage and updates.

## Future Enhancements

- Add indexes on `user_id` and `created_at` for better query performance
- Implement pagination for `get_user_preferences` when users have many preference records
- Add search and filter capabilities for preference history
- Implement preference comparison to track how user preferences evolve over time
