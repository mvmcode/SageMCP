# Notion Connector

The Notion connector provides comprehensive integration with Notion API, enabling access to Notion databases, pages, and blocks through OAuth 2.0 authentication.

## Features

- **10 comprehensive tools** covering page, database, and block management
- **Full OAuth 2.0 authentication** with Notion
- **Dynamic resource discovery** of pages and databases
- **Real-time access** to content and metadata
- **Support for creating and updating content**

## OAuth Setup

### Prerequisites

- A Notion account
- Access to create Notion integrations

### Step-by-Step Configuration

1. **Create Notion Integration**
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Click "New integration"
   - Fill in the basic information:
     - **Name**: `SageMCP` (or your preferred name)
     - **Associated workspace**: Select your workspace
     - **Logo**: Optional
   - Click "Submit"

2. **Configure Integration Capabilities**
   - Under "Capabilities", ensure the following are enabled:
     - **Read content**: ✓
     - **Update content**: ✓
     - **Insert content**: ✓
   - Under "User Capabilities", enable:
     - **Read user information including email addresses**: ✓

3. **Get Integration Credentials**
   - After creating the integration, you'll see the **Integration Token**
   - Copy the **Internal Integration Token** (starts with `secret_`)
   - Note: For OAuth 2.0 flow, you'll need:
     - **OAuth client ID**
     - **OAuth client secret**
   - These are found under "Distribution" → "OAuth Domain & URIs"

4. **Configure OAuth Settings**
   - Under "Distribution" → "OAuth Domain & URIs":
     - **Redirect URIs**: Add `http://localhost:8000/api/v1/oauth/callback/notion`
     - **Configuration URL**: Optional
   - Click "Submit"

5. **Update Environment Variables**

   Add the following to your `.env` file:

   ```env
   NOTION_CLIENT_ID=your_oauth_client_id_here
   NOTION_CLIENT_SECRET=your_oauth_client_secret_here
   ```

6. **Connect Pages and Databases**
   - In Notion, navigate to the page or database you want to access
   - Click the "..." menu in the top right
   - Select "Add connections"
   - Search for and select your integration name (e.g., "SageMCP")
   - Click "Confirm"

### Required Scopes

The Notion connector requires the following OAuth scopes:

- No explicit scopes needed - Notion uses integration capabilities instead
- The integration needs to be explicitly connected to pages/databases

## Available Tools

### 1. notion_list_databases

List all Notion databases accessible to the integration.

**Parameters:**
- `page_size` (optional, integer, default: 20): Number of databases to return (max 100)

**Example:**
```json
{
  "page_size": 50
}
```

**Response:**
```json
{
  "databases": [
    {
      "id": "database-id",
      "title": "My Database",
      "created_time": "2024-01-01T00:00:00Z",
      "last_edited_time": "2024-01-02T00:00:00Z",
      "url": "https://notion.so/database-id"
    }
  ],
  "count": 1,
  "has_more": false
}
```

### 2. notion_search

Search for pages and databases by title.

**Parameters:**
- `query` (required, string): Search query to match against titles
- `filter` (optional, enum: "page" | "database"): Filter results by type
- `page_size` (optional, integer, default: 20): Number of results to return (max 100)

**Example:**
```json
{
  "query": "project notes",
  "filter": "page",
  "page_size": 20
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "page-id",
      "type": "page",
      "title": "Project Notes 2024",
      "created_time": "2024-01-01T00:00:00Z",
      "last_edited_time": "2024-01-02T00:00:00Z",
      "url": "https://notion.so/page-id"
    }
  ],
  "count": 1,
  "has_more": false
}
```

### 3. notion_get_page

Get a Notion page by ID, including metadata and properties.

**Parameters:**
- `page_id` (required, string): The ID of the page to retrieve

**Example:**
```json
{
  "page_id": "abc123-def456-ghi789"
}
```

**Response:**
```json
{
  "id": "abc123-def456-ghi789",
  "created_time": "2024-01-01T00:00:00Z",
  "last_edited_time": "2024-01-02T00:00:00Z",
  "archived": false,
  "url": "https://notion.so/abc123-def456-ghi789",
  "properties": {
    "title": { ... }
  }
}
```

### 4. notion_get_page_content

Get the content blocks of a Notion page.

**Parameters:**
- `page_id` (required, string): The ID of the page to retrieve content from
- `format` (optional, enum: "plain_text" | "structured", default: "plain_text"): Format of the output

**Example:**
```json
{
  "page_id": "abc123-def456-ghi789",
  "format": "plain_text"
}
```

**Response (plain_text):**
```
Title: My Page Title

This is the first paragraph of content.

This is a heading

More content here.
```

**Response (structured):**
```json
{
  "title": "My Page Title",
  "page_id": "abc123-def456-ghi789",
  "blocks": [
    {
      "type": "paragraph",
      "paragraph": {
        "rich_text": [
          {
            "type": "text",
            "text": { "content": "This is the first paragraph of content." }
          }
        ]
      }
    }
  ]
}
```

### 5. notion_get_database

Get a Notion database by ID, including schema and properties.

**Parameters:**
- `database_id` (required, string): The ID of the database to retrieve

**Example:**
```json
{
  "database_id": "xyz789-abc123-def456"
}
```

**Response:**
```json
{
  "id": "xyz789-abc123-def456",
  "title": "My Database",
  "created_time": "2024-01-01T00:00:00Z",
  "last_edited_time": "2024-01-02T00:00:00Z",
  "url": "https://notion.so/xyz789-abc123-def456",
  "properties": {
    "Name": { "type": "title" },
    "Status": { "type": "select" },
    "Due Date": { "type": "date" }
  }
}
```

### 6. notion_query_database

Query a Notion database to retrieve pages/entries.

**Parameters:**
- `database_id` (required, string): The ID of the database to query
- `page_size` (optional, integer, default: 20): Number of results to return (max 100)

**Example:**
```json
{
  "database_id": "xyz789-abc123-def456",
  "page_size": 50
}
```

**Response:**
```json
{
  "pages": [
    {
      "id": "page-id",
      "title": "Task 1",
      "created_time": "2024-01-01T00:00:00Z",
      "last_edited_time": "2024-01-02T00:00:00Z",
      "url": "https://notion.so/page-id",
      "properties": {
        "Name": { ... },
        "Status": { ... }
      }
    }
  ],
  "count": 1,
  "has_more": false
}
```

### 7. notion_create_page

Create a new page in a Notion database or as a child of another page.

**Parameters:**
- `parent_id` (required, string): The ID of the parent database or page
- `parent_type` (optional, enum: "database_id" | "page_id", default: "database_id"): Type of parent
- `title` (required, string): Title of the new page
- `content` (optional, string): Optional plain text content to add to the page

**Example:**
```json
{
  "parent_id": "xyz789-abc123-def456",
  "parent_type": "database_id",
  "title": "New Task",
  "content": "This is the initial content of the task."
}
```

**Response:**
```json
{
  "id": "new-page-id",
  "url": "https://notion.so/new-page-id",
  "created_time": "2024-01-03T00:00:00Z"
}
```

### 8. notion_append_block_children

Append blocks (content) to a page.

**Parameters:**
- `page_id` (required, string): The ID of the page to append content to
- `content` (required, string): Plain text content to append to the page

**Example:**
```json
{
  "page_id": "abc123-def456-ghi789",
  "content": "This is additional content to append to the page."
}
```

**Response:**
```json
{
  "status": "success",
  "blocks_added": 1
}
```

### 9. notion_update_page

Update a page's properties (title, metadata).

**Parameters:**
- `page_id` (required, string): The ID of the page to update
- `title` (required, string): New title for the page

**Example:**
```json
{
  "page_id": "abc123-def456-ghi789",
  "title": "Updated Page Title"
}
```

**Response:**
```json
{
  "id": "abc123-def456-ghi789",
  "url": "https://notion.so/abc123-def456-ghi789",
  "last_edited_time": "2024-01-03T12:00:00Z"
}
```

### 10. notion_get_block

Get a specific block by ID.

**Parameters:**
- `block_id` (required, string): The ID of the block to retrieve

**Example:**
```json
{
  "block_id": "block-id-123"
}
```

**Response:**
```json
{
  "object": "block",
  "id": "block-id-123",
  "type": "paragraph",
  "paragraph": {
    "rich_text": [
      {
        "type": "text",
        "text": { "content": "Block content" }
      }
    ]
  }
}
```

## Common Use Cases

### 1. List All Databases

```json
{
  "tool": "notion_list_databases",
  "arguments": {
    "page_size": 100
  }
}
```

### 2. Search for Specific Pages

```json
{
  "tool": "notion_search",
  "arguments": {
    "query": "meeting notes",
    "filter": "page"
  }
}
```

### 3. Read Page Content

```json
{
  "tool": "notion_get_page_content",
  "arguments": {
    "page_id": "your-page-id",
    "format": "plain_text"
  }
}
```

### 4. Query Database Entries

```json
{
  "tool": "notion_query_database",
  "arguments": {
    "database_id": "your-database-id",
    "page_size": 50
  }
}
```

### 5. Create a New Page in Database

```json
{
  "tool": "notion_create_page",
  "arguments": {
    "parent_id": "database-id",
    "parent_type": "database_id",
    "title": "New Entry",
    "content": "Initial content here"
  }
}
```

### 6. Append Content to Existing Page

```json
{
  "tool": "notion_append_block_children",
  "arguments": {
    "page_id": "page-id",
    "content": "Additional notes to append"
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

**Solution:** Re-authenticate with Notion through the OAuth flow.

### HTTP Errors

**Error:**
```json
{
  "error": "HTTP error: 404",
  "message": "Page not found"
}
```

**Common HTTP Status Codes:**
- `400`: Bad request - Invalid parameters
- `401`: Unauthorized - Invalid or expired token
- `403`: Forbidden - Integration doesn't have access to the resource
- `404`: Not found - Resource doesn't exist
- `429`: Rate limit exceeded

**Solution:** Check the error message and ensure:
1. The page/database ID is correct
2. The integration has been connected to the resource
3. You're not exceeding rate limits

### Resource Not Connected

**Error:**
```json
{
  "error": "HTTP error: 403",
  "message": "The integration doesn't have access to this resource"
}
```

**Solution:** Connect the integration to the page/database:
1. Open the page/database in Notion
2. Click "..." → "Add connections"
3. Select your integration
4. Click "Confirm"

## Limitations

1. **Integration Access**: The integration must be explicitly connected to pages and databases before they can be accessed.

2. **Rate Limits**: Notion API has rate limits:
   - 3 requests per second
   - Burst limit for short-term spikes

3. **Content Types**: The connector currently supports basic block types:
   - Paragraphs
   - Headings (1, 2, 3)
   - Lists (bulleted, numbered)
   - To-do items
   - Quotes
   - Code blocks

4. **Advanced Properties**: Complex database properties (formulas, rollups) are returned as-is in structured format but may not be fully parsed.

5. **Pagination**: Large result sets require multiple requests using pagination cursors (not fully exposed in current implementation).

## Tips and Best Practices

### 1. Use Search Before Getting

Instead of trying to guess page IDs, use `notion_search` to find pages first:

```json
{
  "tool": "notion_search",
  "arguments": {
    "query": "quarterly report"
  }
}
```

### 2. Connect Your Integration

Always remember to connect your integration to the pages/databases you want to access in Notion's UI.

### 3. Use Plain Text Format for Reading

For most reading use cases, `plain_text` format is easier to work with:

```json
{
  "tool": "notion_get_page_content",
  "arguments": {
    "page_id": "page-id",
    "format": "plain_text"
  }
}
```

### 4. Query Databases for Structured Data

Use `notion_query_database` to get all entries from a database with their properties:

```json
{
  "tool": "notion_query_database",
  "arguments": {
    "database_id": "database-id"
  }
}
```

### 5. Handle Rate Limits

Implement exponential backoff when encountering rate limits (429 errors).

## Troubleshooting

### Can't Find My Pages/Databases

**Problem:** `notion_list_databases` or `notion_search` returns empty results.

**Solution:**
1. Verify the integration is connected to the pages/databases in Notion
2. Check that OAuth credentials are valid
3. Ensure the integration has the correct capabilities enabled

### Page Content is Empty

**Problem:** `notion_get_page_content` returns empty content.

**Solution:**
1. The page might actually be empty
2. Try using `format: "structured"` to see the raw block structure
3. Check if the page has access restrictions

### Can't Create Pages

**Problem:** `notion_create_page` fails with 403 error.

**Solution:**
1. Verify the parent_id is correct
2. Ensure the integration has "Insert content" capability
3. Check that the integration is connected to the parent database/page

## Additional Resources

- [Notion API Documentation](https://developers.notion.com/)
- [Notion API Reference](https://developers.notion.com/reference)
- [Notion Integration Guide](https://developers.notion.com/docs/getting-started)
- [Notion OAuth Guide](https://developers.notion.com/docs/authorization)

## Support

For issues or questions:
1. Check the error message and this documentation
2. Verify your OAuth setup is correct
3. Ensure integrations are connected to resources
4. Review Notion API documentation for additional details
