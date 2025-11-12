# Zoom Connector

The Zoom connector provides comprehensive integration with Zoom API, enabling access to meetings, webinars, recordings, and user management through OAuth 2.0 authentication.

## Features

- **12 comprehensive tools** covering meetings, webinars, recordings, and user management
- **Full OAuth 2.0 authentication** with Zoom
- **Dynamic resource discovery** of upcoming meetings
- **Real-time access** to meeting details and recordings
- **Support for creating and managing meetings**

## OAuth Setup

### Prerequisites

- A Zoom account (Pro, Business, or Enterprise)
- Access to Zoom Marketplace

### Step-by-Step Configuration

1. **Create a Zoom App**
   - Go to [Zoom Marketplace](https://marketplace.zoom.us/)
   - Click "Develop" → "Build App"
   - Select "OAuth" app type
   - Click "Create"

2. **Configure App Information**
   - **App Name**: `SageMCP` (or your preferred name)
   - **Short Description**: Brief description of your app
   - **Long Description**: Detailed description
   - **Company Name**: Your company/organization name
   - **Developer Contact Information**: Your email and name

3. **Configure OAuth Settings**
   - Under "App Credentials":
     - Copy the **Client ID**
     - Copy the **Client Secret**
   - Under "Redirect URL for OAuth":
     - Add: `http://localhost:8000/api/v1/oauth/callback/zoom`
   - Under "OAuth allow list":
     - Add: `http://localhost:8000`

4. **Add Scopes**

   Navigate to "Scopes" and add the following permissions:

   **Meeting Scopes:**
   - `meeting:read:admin` - View all user meetings
   - `meeting:write:admin` - Create, update, and delete meetings
   - `meeting:read:meeting_invitation:admin` - View meeting invitations

   **Recording Scopes:**
   - `recording:read:admin` - View all user recordings
   - `recording:read:list_recording_files:admin` - List recording files

   **User Scopes:**
   - `user:read:admin` - View all user information

   **Webinar Scopes:**
   - `webinar:read:admin` - View all webinars
   - `webinar:write:admin` - Create, update, and delete webinars

   **Report Scopes:**
   - `report:read:admin` - View meeting participants

5. **Activation**
   - Complete all required information
   - Under "Activation", click "Activate your app"
   - If developing for yourself, you can deactivate the app after installation

6. **Update Environment Variables**

   Add the following to your `.env` file:

   ```env
   ZOOM_CLIENT_ID=your_client_id_here
   ZOOM_CLIENT_SECRET=your_client_secret_here
   ```

### Required Scopes

The Zoom connector requires the following OAuth scopes:

- `meeting:read:admin` - Read meeting information
- `meeting:write:admin` - Create and manage meetings
- `meeting:read:meeting_invitation:admin` - Read meeting invitations
- `recording:read:admin` - Read recording information
- `user:read:admin` - Read user information
- `webinar:read:admin` - Read webinar information
- `webinar:write:admin` - Manage webinars
- `report:read:admin` - Read meeting reports and participants

## Available Tools

### 1. zoom_list_meetings

List all scheduled meetings for the authenticated user.

**Parameters:**
- `type` (optional, enum: "scheduled" | "live" | "upcoming", default: "upcoming"): Meeting type filter
- `page_size` (optional, integer, default: 30): Number of meetings to return (max 300)

**Example:**
```json
{
  "type": "upcoming",
  "page_size": 50
}
```

**Response:**
```json
{
  "meetings": [
    {
      "id": "12345678",
      "topic": "Team Standup",
      "type": 2,
      "start_time": "2024-01-15T10:00:00Z",
      "duration": 30,
      "timezone": "America/New_York",
      "join_url": "https://zoom.us/j/12345678",
      "agenda": "Daily standup meeting"
    }
  ],
  "count": 1,
  "total_records": 1
}
```

### 2. zoom_get_meeting

Get details of a specific meeting by ID.

**Parameters:**
- `meeting_id` (required, string): The meeting ID or UUID

**Example:**
```json
{
  "meeting_id": "12345678"
}
```

**Response:**
```json
{
  "id": "12345678",
  "uuid": "abc-123-def-456",
  "host_id": "host123",
  "topic": "Team Standup",
  "type": 2,
  "status": "waiting",
  "start_time": "2024-01-15T10:00:00Z",
  "duration": 30,
  "timezone": "America/New_York",
  "agenda": "Daily standup meeting",
  "created_at": "2024-01-10T12:00:00Z",
  "join_url": "https://zoom.us/j/12345678",
  "password": "abc123",
  "settings": { ... }
}
```

### 3. zoom_create_meeting

Create a new scheduled meeting.

**Parameters:**
- `topic` (required, string): Meeting topic/title
- `type` (optional, integer, default: 2): Meeting type
  - 1 = Instant meeting
  - 2 = Scheduled meeting
  - 3 = Recurring meeting with no fixed time
  - 8 = Recurring meeting with fixed time
- `start_time` (optional, string): Meeting start time in ISO 8601 format
- `duration` (optional, integer, default: 60): Meeting duration in minutes
- `timezone` (optional, string, default: "UTC"): Timezone (e.g., "America/New_York")
- `agenda` (optional, string): Meeting agenda/description

**Example:**
```json
{
  "topic": "Project Kickoff Meeting",
  "type": 2,
  "start_time": "2024-01-20T14:00:00",
  "duration": 90,
  "timezone": "America/New_York",
  "agenda": "Discuss project goals and timeline"
}
```

**Response:**
```json
{
  "id": "87654321",
  "uuid": "new-uuid-123",
  "host_id": "host123",
  "topic": "Project Kickoff Meeting",
  "type": 2,
  "start_time": "2024-01-20T14:00:00Z",
  "duration": 90,
  "timezone": "America/New_York",
  "join_url": "https://zoom.us/j/87654321",
  "password": "xyz789",
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 4. zoom_update_meeting

Update an existing meeting.

**Parameters:**
- `meeting_id` (required, string): The meeting ID to update
- `topic` (optional, string): Updated meeting topic
- `start_time` (optional, string): Updated start time in ISO 8601 format
- `duration` (optional, integer): Updated duration in minutes
- `agenda` (optional, string): Updated meeting agenda

**Example:**
```json
{
  "meeting_id": "12345678",
  "topic": "Updated Meeting Title",
  "duration": 45
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Meeting 12345678 updated successfully"
}
```

### 5. zoom_delete_meeting

Delete a scheduled meeting.

**Parameters:**
- `meeting_id` (required, string): The meeting ID to delete

**Example:**
```json
{
  "meeting_id": "12345678"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Meeting 12345678 deleted successfully"
}
```

### 6. zoom_get_user

Get user profile information.

**Parameters:**
- `user_id` (optional, string, default: "me"): User ID or email address (use "me" for authenticated user)

**Example:**
```json
{
  "user_id": "me"
}
```

**Response:**
```json
{
  "id": "user123",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "type": 2,
  "pmi": 1234567890,
  "timezone": "America/New_York",
  "verified": 1,
  "created_at": "2020-01-01T00:00:00Z",
  "last_login_time": "2024-01-15T08:00:00Z",
  "pic_url": "https://example.com/pic.jpg",
  "account_id": "account123"
}
```

### 7. zoom_list_recordings

List cloud recordings for the authenticated user.

**Parameters:**
- `from_date` (optional, string): Start date in YYYY-MM-DD format (default: 30 days ago)
- `to_date` (optional, string): End date in YYYY-MM-DD format (default: today)
- `page_size` (optional, integer, default: 30): Number of recordings to return (max 300)

**Example:**
```json
{
  "from_date": "2024-01-01",
  "to_date": "2024-01-31",
  "page_size": 50
}
```

**Response:**
```json
{
  "recordings": [
    {
      "meeting_id": "rec123",
      "uuid": "rec-uuid-123",
      "topic": "Recorded Meeting",
      "start_time": "2024-01-10T10:00:00Z",
      "duration": 60,
      "total_size": 1024000,
      "recording_count": 2,
      "recording_files": [
        {
          "id": "file1",
          "file_type": "MP4",
          "file_size": 512000,
          "download_url": "https://zoom.us/rec/download/file1",
          "play_url": "https://zoom.us/rec/play/file1"
        }
      ]
    }
  ],
  "count": 1,
  "from": "2024-01-01",
  "to": "2024-01-31"
}
```

### 8. zoom_get_meeting_recordings

Get all recordings for a specific meeting.

**Parameters:**
- `meeting_id` (required, string): The meeting ID or UUID

**Example:**
```json
{
  "meeting_id": "meeting123"
}
```

**Response:**
```json
{
  "uuid": "meeting-uuid",
  "id": "meeting123",
  "account_id": "account123",
  "host_id": "host123",
  "topic": "Test Meeting",
  "start_time": "2024-01-10T10:00:00Z",
  "duration": 60,
  "total_size": 2048000,
  "recording_count": 3,
  "recording_files": [
    {
      "id": "file1",
      "meeting_id": "meeting123",
      "recording_start": "2024-01-10T10:00:00Z",
      "recording_end": "2024-01-10T11:00:00Z",
      "file_type": "MP4",
      "file_size": 1024000,
      "download_url": "https://zoom.us/rec/download/file1",
      "play_url": "https://zoom.us/rec/play/file1",
      "status": "completed"
    }
  ]
}
```

### 9. zoom_list_webinars

List all webinars for the authenticated user.

**Parameters:**
- `page_size` (optional, integer, default: 30): Number of webinars to return (max 300)

**Example:**
```json
{
  "page_size": 50
}
```

**Response:**
```json
{
  "webinars": [
    {
      "id": "web123",
      "uuid": "web-uuid-123",
      "topic": "Product Launch Webinar",
      "type": 5,
      "start_time": "2024-01-20T15:00:00Z",
      "duration": 120,
      "timezone": "UTC",
      "join_url": "https://zoom.us/w/web123",
      "agenda": "Product launch presentation"
    }
  ],
  "count": 1,
  "total_records": 1
}
```

### 10. zoom_get_webinar

Get details of a specific webinar by ID.

**Parameters:**
- `webinar_id` (required, string): The webinar ID

**Example:**
```json
{
  "webinar_id": "web123"
}
```

**Response:**
```json
{
  "id": "web123",
  "uuid": "web-uuid-123",
  "host_id": "host123",
  "topic": "Product Launch Webinar",
  "type": 5,
  "start_time": "2024-01-20T15:00:00Z",
  "duration": 120,
  "timezone": "UTC",
  "agenda": "Product launch presentation",
  "created_at": "2024-01-15T10:00:00Z",
  "join_url": "https://zoom.us/w/web123",
  "settings": { ... }
}
```

### 11. zoom_list_meeting_participants

Get participants for a past meeting instance.

**Parameters:**
- `meeting_id` (required, string): The meeting ID or UUID
- `page_size` (optional, integer, default: 30): Number of participants to return (max 300)

**Example:**
```json
{
  "meeting_id": "meeting123",
  "page_size": 100
}
```

**Response:**
```json
{
  "participants": [
    {
      "id": "part1",
      "user_id": "user123",
      "name": "John Doe",
      "user_email": "john@example.com",
      "join_time": "2024-01-10T10:00:00Z",
      "leave_time": "2024-01-10T11:00:00Z",
      "duration": 60,
      "status": "in_meeting"
    }
  ],
  "count": 1,
  "total_records": 1
}
```

### 12. zoom_get_meeting_invitation

Get the meeting invitation text/HTML.

**Parameters:**
- `meeting_id` (required, string): The meeting ID

**Example:**
```json
{
  "meeting_id": "12345678"
}
```

**Response:**
```json
{
  "invitation": "You are invited to join:\nTeam Standup\nTime: Jan 15, 2024 10:00 AM\nJoin URL: https://zoom.us/j/12345678"
}
```

## Common Use Cases

### 1. List Upcoming Meetings

```json
{
  "tool": "zoom_list_meetings",
  "arguments": {
    "type": "upcoming",
    "page_size": 50
  }
}
```

### 2. Create a New Meeting

```json
{
  "tool": "zoom_create_meeting",
  "arguments": {
    "topic": "Weekly Team Sync",
    "type": 2,
    "start_time": "2024-01-22T15:00:00",
    "duration": 60,
    "timezone": "America/New_York",
    "agenda": "Discuss weekly progress and blockers"
  }
}
```

### 3. Get Meeting Details

```json
{
  "tool": "zoom_get_meeting",
  "arguments": {
    "meeting_id": "12345678"
  }
}
```

### 4. List Recent Recordings

```json
{
  "tool": "zoom_list_recordings",
  "arguments": {
    "from_date": "2024-01-01",
    "to_date": "2024-01-15"
  }
}
```

### 5. Get User Profile

```json
{
  "tool": "zoom_get_user",
  "arguments": {
    "user_id": "me"
  }
}
```

### 6. Update Meeting Time

```json
{
  "tool": "zoom_update_meeting",
  "arguments": {
    "meeting_id": "12345678",
    "start_time": "2024-01-22T16:00:00",
    "duration": 45
  }
}
```

## Error Handling

The connector handles various error scenarios:

### Invalid OAuth Credentials

**Error:**
```json
{
  "error": "Invalid or expired OAuth credentials"
}
```

**Solution:** Re-authenticate with Zoom through the OAuth flow.

### HTTP Errors

**Error:**
```json
{
  "error": "HTTP error: 404",
  "message": "Meeting not found"
}
```

**Common HTTP Status Codes:**
- `400`: Bad request - Invalid parameters
- `401`: Unauthorized - Invalid or expired token
- `403`: Forbidden - Insufficient permissions
- `404`: Not found - Meeting/resource doesn't exist
- `429`: Rate limit exceeded

**Solution:** Check the error message and ensure:
1. The meeting ID is correct
2. You have the required permissions (scopes)
3. The OAuth token is valid
4. You're not exceeding rate limits

### Meeting Not Found

**Error:**
```json
{
  "error": "HTTP error: 404",
  "message": "Meeting not found"
}
```

**Solution:** Verify the meeting ID is correct and the meeting hasn't been deleted.

### Insufficient Permissions

**Error:**
```json
{
  "error": "HTTP error: 403",
  "message": "Insufficient permissions"
}
```

**Solution:** Ensure your OAuth app has the required scopes enabled in the Zoom Marketplace.

## Limitations

1. **Rate Limits**: Zoom API has rate limits:
   - Light: 30 requests per second
   - Medium: 10 requests per second
   - Heavy: 5 requests per second

2. **Account Types**: Some features require specific Zoom account types:
   - Webinars require a Webinar plan
   - Cloud recordings require a Pro account or higher

3. **Meeting Types**: The connector supports:
   - Instant meetings (type 1)
   - Scheduled meetings (type 2)
   - Recurring meetings (types 3, 8)
   - Webinars (types 5, 6, 9)

4. **Participant Reports**: Only available for past meetings, not live or upcoming meetings.

5. **Recording Access**: Only cloud recordings are accessible via API. Local recordings are not available.

## Tips and Best Practices

### 1. Use Meeting IDs Consistently

Zoom uses both numeric Meeting IDs and UUIDs. Most endpoints accept both, but UUIDs are more reliable for specific meeting instances.

### 2. Handle Timezones Properly

Always specify timezones when creating meetings to avoid confusion:

```json
{
  "topic": "Meeting",
  "start_time": "2024-01-20T14:00:00",
  "timezone": "America/New_York"
}
```

### 3. Check Recording Availability

Recordings may not be immediately available after a meeting ends. Check the `status` field.

### 4. Use Pagination for Large Results

For large datasets, use pagination with `page_size`:

```json
{
  "tool": "zoom_list_meetings",
  "arguments": {
    "type": "upcoming",
    "page_size": 300
  }
}
```

### 5. Handle Rate Limits Gracefully

Implement exponential backoff when encountering 429 errors.

### 6. Validate Meeting Times

Ensure meeting start times are in the future when creating scheduled meetings.

## Troubleshooting

### Can't Create Meetings

**Problem:** `zoom_create_meeting` fails with permission error.

**Solution:**
1. Verify `meeting:write:admin` scope is enabled
2. Ensure the account has permission to schedule meetings
3. Check that start_time is in the future for scheduled meetings

### Can't Access Recordings

**Problem:** `zoom_list_recordings` returns empty or error.

**Solution:**
1. Verify `recording:read:admin` scope is enabled
2. Ensure cloud recording is enabled in Zoom account settings
3. Check the date range - recordings may have expired

### Participant List is Empty

**Problem:** `zoom_list_meeting_participants` returns empty.

**Solution:**
1. Ensure the meeting has already occurred (past meeting)
2. Verify `report:read:admin` scope is enabled
3. Check that participant tracking is enabled for the meeting

### Invalid Timezone Error

**Problem:** Meeting creation fails with timezone error.

**Solution:**
Use valid timezone identifiers from the [IANA timezone database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), e.g.:
- `America/New_York`
- `Europe/London`
- `Asia/Tokyo`
- `UTC`

## Additional Resources

- [Zoom API Documentation](https://developers.zoom.us/docs/api/)
- [Zoom OAuth Guide](https://developers.zoom.us/docs/integrations/oauth/)
- [Zoom API Reference](https://developers.zoom.us/docs/api/rest/)
- [Zoom Marketplace](https://marketplace.zoom.us/)
- [IANA Timezone Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

## Support

For issues or questions:
1. Check the error message and this documentation
2. Verify your OAuth setup and scopes
3. Review Zoom API documentation for additional details
4. Check Zoom Marketplace for app status and configuration
