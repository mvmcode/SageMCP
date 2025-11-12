# Google Docs Connector

The Google Docs connector provides comprehensive integration with Google Docs API, enabling Claude Desktop to create, read, update, and export Google Docs documents through OAuth 2.0 authentication.

## Features

- **10 comprehensive tools** covering document management and collaboration
- **Full OAuth 2.0 authentication** with Google Workspace
- **Dynamic resource discovery** of documents
- **Real-time access** to document content and metadata

## OAuth Setup

### Prerequisites

- A Google account
- Access to Google Cloud Console

### Step-by-Step Configuration

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the following APIs:
     - Google Docs API
     - Google Drive API

2. **Configure OAuth Consent Screen**
   - Navigate to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in the application details:
     - **App name**: `SageMCP` (or your preferred name)
     - **User support email**: Your email address
     - **Developer contact email**: Your email address
   - Add the following scopes:
     - `https://www.googleapis.com/auth/documents`
     - `https://www.googleapis.com/auth/drive.file`
     - `https://www.googleapis.com/auth/drive.readonly`

3. **Create OAuth Credentials**
   - Navigate to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application" as application type
   - Fill in the details:
     - **Name**: `SageMCP Web Client`
     - **Authorized redirect URIs**: `http://localhost:8000/api/v1/oauth/callback/google_docs`
   - Click "Create"

4. **Get Credentials**
   - Note the **Client ID**
   - Note the **Client Secret**
   - Save both credentials securely

5. **Configure SageMCP**
   - Add to your `.env` file:
     ```env
     GOOGLE_DOCS_CLIENT_ID=your_client_id_here
     GOOGLE_DOCS_CLIENT_SECRET=your_client_secret_here
     ```

6. **Add Connector in SageMCP**
   - Open SageMCP web interface
   - Create or select a tenant
   - Add Google Docs connector
   - Complete OAuth authorization flow

### Required OAuth Scopes

The Google Docs connector automatically requests these scopes:
- `https://www.googleapis.com/auth/documents` - Read and write Google Docs
- `https://www.googleapis.com/auth/drive.file` - Access files created by the app
- `https://www.googleapis.com/auth/drive.readonly` - Read-only access to Drive

## Available Tools

### Document Discovery

#### `google_docs_list_documents`
List Google Docs documents accessible to the user.

**Parameters:**
- `page_size` (optional): Number of documents to return (1-100, default: 20)
- `order_by` (optional): Sort order - `modifiedTime`, `name`, `createdTime` (default: `modifiedTime desc`)

**Example:**
```json
{
  "page_size": 10,
  "order_by": "modifiedTime desc"
}
```

#### `google_docs_search_documents`
Search for Google Docs by title.

**Parameters:**
- `query` (required): Search query (searches in document name)
- `page_size` (optional): Number of results to return (1-100, default: 20)

**Example:**
```json
{
  "query": "project proposal",
  "page_size": 10
}
```

#### `google_docs_list_shared_documents`
List Google Docs that have been shared with the user.

**Parameters:**
- `page_size` (optional): Number of documents to return (1-100, default: 20)

**Example:**
```json
{
  "page_size": 20
}
```

### Document Reading

#### `google_docs_get_document`
Get detailed metadata about a specific Google Doc.

**Parameters:**
- `document_id` (required): The ID of the Google Doc

**Example:**
```json
{
  "document_id": "1abc123def456"
}
```

#### `google_docs_read_document_content`
Read the full content of a Google Doc as structured text.

**Parameters:**
- `document_id` (required): The ID of the Google Doc
- `format` (optional): Format of the returned content - `structured`, `plain_text` (default: `plain_text`)

**Example:**
```json
{
  "document_id": "1abc123def456",
  "format": "plain_text"
}
```

### Document Creation & Editing

#### `google_docs_create_document`
Create a new Google Doc with optional initial content.

**Parameters:**
- `title` (required): Title of the new document
- `initial_content` (optional): Optional initial text content

**Example:**
```json
{
  "title": "Project Meeting Notes",
  "initial_content": "Meeting Agenda:\n1. Project updates\n2. Timeline review\n3. Action items"
}
```

#### `google_docs_append_text`
Append text to the end of a Google Doc.

**Parameters:**
- `document_id` (required): The ID of the Google Doc
- `text` (required): Text to append to the document

**Example:**
```json
{
  "document_id": "1abc123def456",
  "text": "\n\nAdditional notes from the meeting..."
}
```

#### `google_docs_insert_text`
Insert text at a specific position in a Google Doc.

**Parameters:**
- `document_id` (required): The ID of the Google Doc
- `text` (required): Text to insert
- `index` (required): Position to insert text (1-based index)

**Example:**
```json
{
  "document_id": "1abc123def456",
  "text": "Important: ",
  "index": 1
}
```

### Document Export & Permissions

#### `google_docs_export_document`
Export a Google Doc in various formats (PDF, TXT, HTML, DOCX).

**Parameters:**
- `document_id` (required): The ID of the Google Doc
- `mime_type` (optional): Export format MIME type (default: `application/pdf`)
  - `application/pdf` - PDF format
  - `text/plain` - Plain text
  - `text/html` - HTML format
  - `application/vnd.openxmlformats-officedocument.wordprocessingml.document` - DOCX format

**Example:**
```json
{
  "document_id": "1abc123def456",
  "mime_type": "application/pdf"
}
```

#### `google_docs_get_permissions`
Get sharing permissions for a Google Doc.

**Parameters:**
- `document_id` (required): The ID of the Google Doc

**Example:**
```json
{
  "document_id": "1abc123def456"
}
```

## Common Use Cases

### Reading Meeting Notes
1. Use `google_docs_search_documents` to find the document
2. Use `google_docs_read_document_content` to read the content
3. Analyze or summarize the content

### Creating and Updating Documentation
1. Use `google_docs_create_document` to create a new document
2. Use `google_docs_append_text` or `google_docs_insert_text` to add content
3. Use `google_docs_get_document` to verify the changes

### Exporting Reports
1. Use `google_docs_list_documents` to find the document
2. Use `google_docs_export_document` to export as PDF or other formats

### Collaborative Document Management
1. Use `google_docs_list_shared_documents` to see shared documents
2. Use `google_docs_get_permissions` to check access levels
3. Use `google_docs_append_text` to contribute to shared documents

## Resources

The Google Docs connector provides MCP resources for all accessible documents:

- **URI Format**: `google-docs://document/{document_id}`
- **MIME Type**: `application/vnd.google-apps.document`
- **Resource Content**: Document title and metadata

Resources are automatically discovered when you connect the Google Docs connector and can be referenced in Claude Desktop conversations.

## Error Handling

Common errors and their solutions:

### Authentication Errors
- **Error**: `Invalid or expired Google OAuth credentials`
- **Solution**: Re-authenticate through the SageMCP web interface

### Permission Errors
- **Error**: `Insufficient permissions to access document`
- **Solution**: Ensure the OAuth scopes include document access and the user has permission to the document

### Document Not Found
- **Error**: `Document not found`
- **Solution**: Verify the document ID is correct and the document hasn't been deleted

### Rate Limiting
- **Error**: `Rate limit exceeded`
- **Solution**: Wait a moment and retry. Consider reducing the frequency of requests.

## Limitations

- Document formatting (bold, italics, etc.) is simplified when reading as plain text
- Binary exports (PDF, DOCX) provide export URLs rather than direct content
- Content search is limited to document titles (not full-text search within documents)
- Batch operations are not currently supported

## Tips & Best Practices

1. **Use Plain Text Format**: For content analysis, use `plain_text` format in `google_docs_read_document_content`
2. **Document IDs**: You can find document IDs in the Google Docs URL: `https://docs.google.com/document/d/{DOCUMENT_ID}/edit`
3. **Search Efficiently**: Use specific keywords in `google_docs_search_documents` for better results
4. **Incremental Updates**: Use `google_docs_append_text` for adding new content without replacing existing content
5. **Export Formats**: Choose the right export format based on your needs:
   - PDF for sharing and printing
   - Plain text for analysis
   - HTML for web publishing
   - DOCX for further editing in Microsoft Word

## Support

For issues, feature requests, or questions about the Google Docs connector:
- [Open an issue](https://github.com/mvmcode/SageMCP/issues)
- Review the [OAuth setup guide](../../.github/docs/oauth-setup.md)
- Check Google's [API documentation](https://developers.google.com/docs/api)
