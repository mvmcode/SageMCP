# Slack Connector

The Slack connector provides comprehensive integration with Slack's API, enabling Claude Desktop to read and send messages, manage channels, interact with users, and more through OAuth 2.0 authentication.

## Features

- **11 comprehensive tools** for Slack workspace operations
- **Full OAuth 2.0 authentication** with workspace access
- **Real-time messaging** - read and send messages
- **Thread support** - interact with conversation threads
- **User and channel management**
- **Emoji reactions** and rich message formatting

## OAuth Setup

### Prerequisites

- A Slack workspace with admin permissions (to create apps)
- Access to Slack App Management

### Step-by-Step Configuration

1. **Create Slack App**
   - Go to https://api.slack.com/apps
   - Click "Create New App"
   - Choose "From scratch"
   - Enter app name (e.g., "SageMCP")
   - Select your workspace
   - Click "Create App"

2. **Configure OAuth & Permissions**
   - In the app settings, go to "OAuth & Permissions"
   - Under "Redirect URLs", add:
     ```
     http://localhost:8000/api/v1/oauth/callback/slack
     ```
     (Update with your deployment URL for production)

3. **Add OAuth Scopes**

   Under "Bot Token Scopes", add the following:
   - `channels:history` - View messages in public channels
   - `channels:read` - View basic channel information
   - `chat:write` - Send messages
   - `groups:history` - View messages in private channels
   - `groups:read` - View basic private channel information
   - `im:history` - View messages in direct messages
   - `im:read` - View direct message information
   - `mpim:history` - View messages in group direct messages
   - `mpim:read` - View group direct message information
   - `reactions:read` - View emoji reactions
   - `reactions:write` - Add and edit emoji reactions
   - `search:read` - Search workspace content
   - `users:read` - View people in workspace
   - `users:read.email` - View email addresses of people in workspace

4. **Get Credentials**
   - Note the **Client ID** (found in "Basic Information")
   - Note the **Client Secret** (found in "Basic Information")
   - Save both credentials securely

5. **Configure SageMCP**
   - Add to your `.env` file:
     ```env
     SLACK_CLIENT_ID=your_client_id_here
     SLACK_CLIENT_SECRET=your_client_secret_here
     ```

6. **Install App to Workspace**
   - In "OAuth & Permissions", click "Install to Workspace"
   - Authorize the app
   - You'll receive a Bot User OAuth Token (this is managed by SageMCP)

7. **Add Connector in SageMCP**
   - Open SageMCP web interface
   - Create or select a tenant
   - Add Slack connector
   - Complete OAuth authorization flow

## Available Tools

### Messages & Conversations

#### `slack_conversations_history`
Get messages from a channel or direct message.

**Parameters:**
- `channel_id` (required): Channel ID to fetch history from
- `limit` (optional): Number of messages to return (1-1000, default: 100)
- `cursor` (optional): Pagination cursor for next page
- `oldest` (optional): Start of time range (Unix timestamp)
- `latest` (optional): End of time range (Unix timestamp)
- `include_all_metadata` (optional): Include all metadata (default: false)

#### `slack_conversations_replies`
Get a thread of messages posted to a conversation.

**Parameters:**
- `channel_id` (required): Channel ID containing the thread
- `thread_ts` (required): Timestamp of the parent message
- `limit` (optional): Number of messages to return (1-1000, default: 100)
- `cursor` (optional): Pagination cursor for next page
- `oldest` (optional): Start of time range (Unix timestamp)
- `latest` (optional): End of time range (Unix timestamp)

#### `slack_conversations_add_message`
Post a message to a channel, private channel, or direct message.

**Parameters:**
- `channel_id` (required): Channel ID to post message to
- `text` (required): Message text content
- `thread_ts` (optional): Thread timestamp to reply to
- `blocks` (optional): Structured blocks for rich formatting
- `attachments` (optional): Message attachments

#### `slack_conversations_search_messages`
Search messages in channels, threads, and DMs.

**Parameters:**
- `query` (required): Search query string
- `count` (optional): Results per page (1-100, default: 20)
- `page` (optional): Page number (default: 1)
- `sort` (optional): Sort order - `score`, `timestamp` (default: `score`)
- `sort_dir` (optional): Sort direction - `asc`, `desc` (default: `desc`)

### Channel Management

#### `slack_conversations_list`
List channels available in the workspace.

**Parameters:**
- `types` (optional): Comma-separated types - `public_channel`, `private_channel`, `mpim`, `im` (default: `public_channel`)
- `limit` (optional): Number of channels to return (1-1000, default: 100)
- `cursor` (optional): Pagination cursor for next page
- `exclude_archived` (optional): Exclude archived channels (default: false)

#### `slack_conversations_info`
Get information about a specific channel.

**Parameters:**
- `channel_id` (required): Channel ID to get information about
- `include_locale` (optional): Include locale information (default: false)
- `include_num_members` (optional): Include number of members (default: false)

### User Management

#### `slack_users_list`
List all users in the workspace.

**Parameters:**
- `limit` (optional): Number of users to return (1-1000, default: 100)
- `cursor` (optional): Pagination cursor for next page
- `include_locale` (optional): Include locale information (default: false)

#### `slack_users_info`
Get information about a specific user.

**Parameters:**
- `user_id` (required): User ID to get information about
- `include_locale` (optional): Include locale information (default: false)

### Reactions

#### `slack_reactions_add`
Add an emoji reaction to a message.

**Parameters:**
- `channel_id` (required): Channel ID containing the message
- `timestamp` (required): Message timestamp
- `name` (required): Emoji name (without colons, e.g., `thumbsup`)

#### `slack_reactions_remove`
Remove an emoji reaction from a message.

**Parameters:**
- `channel_id` (required): Channel ID containing the message
- `timestamp` (required): Message timestamp
- `name` (required): Emoji name (without colons)

### Authentication

#### `slack_auth_test`
Check authentication and get workspace/user information.

**Parameters:** None

## Resource URIs

The connector exposes these resource types:

- **Workspace**: `slack://{workspace_id}`
  - Returns workspace information

- **Channels**: `slack://{workspace_id}/channel/{channel_id}`
  - Returns recent channel messages (last 50)

## Usage Examples

### Example 1: Read Recent Messages

```typescript
// Using Claude Desktop
"Show me recent messages from the #general channel"

// First, get channel list to find channel_id
// Then call slack_conversations_history with:
{
  "channel_id": "C1234567890",
  "limit": 50
}
```

### Example 2: Post a Message

```typescript
"Post 'Hello team!' to the #announcements channel"

// This will call slack_conversations_add_message with:
{
  "channel_id": "C1234567890",
  "text": "Hello team!"
}
```

### Example 3: Search Messages

```typescript
"Search for messages containing 'deployment' in the last week"

// This will call slack_conversations_search_messages with:
{
  "query": "deployment after:7d",
  "count": 20,
  "sort": "timestamp",
  "sort_dir": "desc"
}
```

### Example 4: Get Thread Conversation

```typescript
"Show me the thread replies for this message"

// This will call slack_conversations_replies with:
{
  "channel_id": "C1234567890",
  "thread_ts": "1234567890.123456"
}
```

### Example 5: React to a Message

```typescript
"Add a thumbs up reaction to the message"

// This will call slack_reactions_add with:
{
  "channel_id": "C1234567890",
  "timestamp": "1234567890.123456",
  "name": "thumbsup"
}
```

## Understanding Channel IDs

Slack uses IDs instead of channel names for API calls. To get a channel ID:

1. Use `slack_conversations_list` to see all channels
2. Find the channel you want and note its `id` field
3. Use that ID in subsequent calls

Channel IDs look like: `C1234567890`

## Understanding Message Timestamps

Slack uses special timestamps for messages that look like: `1234567890.123456`

These timestamps are:
- Used to identify specific messages
- Required for thread replies and reactions
- Returned in the `ts` field of messages

## Slack Message Formatting

Slack supports rich text formatting:

### Basic Formatting
- `*bold*` - **bold**
- `_italic_` - *italic*
- `~strikethrough~` - ~~strikethrough~~
- `` `code` `` - `code`
- ` ```code block``` ` - code block

### Mentions
- `<@U1234567890>` - Mention a user
- `<#C1234567890>` - Mention a channel
- `<!here>` - Notify active members
- `<!channel>` - Notify all members

### Links
- `<https://example.com>` - Link
- `<https://example.com|Example>` - Link with text

## Troubleshooting

### Common Issues

**Issue**: "Invalid or expired Slack credentials"
- **Solution**: Re-authorize the connector through the SageMCP web interface

**Issue**: "channel_not_found" error
- **Solution**: Verify the channel ID is correct and the bot is invited to the channel
- For private channels, you must explicitly invite the bot

**Issue**: "not_in_channel" error
- **Solution**: Invite the bot to the channel by typing `/invite @SageMCP` in the channel

**Issue**: "missing_scope" error
- **Solution**: Ensure all required OAuth scopes are added in the Slack app configuration

### Inviting the Bot to Channels

For private channels and direct messages:
1. Open the channel in Slack
2. Type `/invite @YourBotName` (replace with your app name)
3. The bot will now have access to that channel

## Rate Limiting

Slack has rate limits on API calls:
- **Tier 1**: 1+ requests per minute
- **Tier 2**: 20+ requests per minute
- **Tier 3**: 50+ requests per minute
- **Tier 4**: 100+ requests per minute

The connector handles rate limiting automatically, but be mindful when making many rapid requests.

## API Reference

- **Slack API Documentation**: https://api.slack.com/methods
- **Message Formatting**: https://api.slack.com/reference/surfaces/formatting
- **OAuth Scopes**: https://api.slack.com/scopes
- **Block Kit**: https://api.slack.com/block-kit (for rich message formatting)

## Source Code

Implementation: `src/sage_mcp/connectors/slack.py`
