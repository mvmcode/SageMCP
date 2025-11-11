# Jira Connector

The Jira connector provides comprehensive integration with Jira Cloud, enabling Claude Desktop to manage issues, projects, sprints, boards, and workflows through OAuth 2.0 authentication.

## Features

- **20 comprehensive tools** for Jira operations
- **Full OAuth 2.0 authentication** with Jira Cloud
- **Issue management** - create, update, search, and transition issues
- **Sprint & board operations** - manage agile workflows
- **JQL support** - powerful issue searching
- **Project and user management**
- **Version/release tracking**

## OAuth Setup

### Prerequisites

- A Jira Cloud instance (not Jira Server/Data Center)
- Atlassian account with admin permissions

### Step-by-Step Configuration

1. **Create OAuth 2.0 App**
   - Go to https://developer.atlassian.com/console/myapps/
   - Click "Create" and select "OAuth 2.0 integration"
   - Enter app name (e.g., "SageMCP")
   - Accept the terms and click "Create"

2. **Configure OAuth Settings**
   - In the app settings, go to "Permissions"
   - Click "Add" next to "OAuth 2.0 (3LO)"
   - Add callback URL:
     ```
     http://localhost:8000/api/v1/oauth/callback/jira
     ```
     (Update with your deployment URL for production)

3. **Add Required Scopes**

   Under "Permissions", add these Jira API scopes:
   - `read:jira-work` - Read Jira project and issue data
   - `write:jira-work` - Create and update issues and other data
   - `read:jira-user` - Read user information
   - `offline_access` - Enable token refresh

4. **Get Credentials**
   - In "Settings", find your:
     - **Client ID**
     - **Client Secret**
   - Save both credentials securely

5. **Configure SageMCP**
   - Add to your `.env` file:
     ```env
     JIRA_CLIENT_ID=your_client_id_here
     JIRA_CLIENT_SECRET=your_client_secret_here
     ```

6. **Add Connector in SageMCP**
   - Open SageMCP web interface
   - Create or select a tenant
   - Add Jira connector
   - Complete OAuth authorization flow
   - Select which Jira site to connect (if you have multiple)

## Available Tools

### Issue Management

#### `jira_search_issues`
Search for Jira issues using JQL (Jira Query Language).

**Parameters:**
- `jql` (required): JQL query string (e.g., `project = PROJ AND status = Open`)
- `max_results` (optional): Maximum results to return (1-100, default: 50)
- `fields` (optional): Specific fields to include (array of field names)

**JQL Examples:**
- `project = MYPROJECT` - All issues in a project
- `assignee = currentUser()` - Issues assigned to you
- `status = "In Progress"` - Issues in specific status
- `created >= -7d` - Issues created in last 7 days
- `project = PROJ AND status != Done ORDER BY updated DESC` - Complex query

#### `jira_get_issue`
Get detailed information about a specific issue.

**Parameters:**
- `issue_key` (required): Issue key (e.g., `PROJ-123`)
- `fields` (optional): Specific fields to include (array)

#### `jira_create_issue`
Create a new Jira issue.

**Parameters:**
- `project_key` (required): Project key (e.g., `PROJ`)
- `summary` (required): Issue summary/title
- `issue_type` (required): Issue type (e.g., `Task`, `Bug`, `Story`)
- `description` (optional): Issue description
- `assignee_id` (optional): Assignee account ID
- `priority_name` (optional): Priority (e.g., `High`, `Medium`, `Low`)
- `labels` (optional): Array of label strings

#### `jira_update_issue`
Update an existing issue.

**Parameters:**
- `issue_key` (required): Issue key (e.g., `PROJ-123`)
- `summary` (optional): New summary/title
- `description` (optional): New description
- `assignee_id` (optional): New assignee account ID
- `priority_name` (optional): New priority
- `labels` (optional): New labels array

#### `jira_transition_issue`
Move an issue through workflow (e.g., from "To Do" to "In Progress").

**Parameters:**
- `issue_key` (required): Issue key (e.g., `PROJ-123`)
- `transition_id` (required): Transition ID (use `jira_get_transitions` to find)
- `comment` (optional): Comment to add during transition

#### `jira_get_transitions`
Get available workflow transitions for an issue.

**Parameters:**
- `issue_key` (required): Issue key (e.g., `PROJ-123`)

#### `jira_assign_issue`
Assign an issue to a user.

**Parameters:**
- `issue_key` (required): Issue key (e.g., `PROJ-123`)
- `account_id` (required): User account ID (use `jira_search_users` to find)

### Comments

#### `jira_add_comment`
Add a comment to an issue.

**Parameters:**
- `issue_key` (required): Issue key (e.g., `PROJ-123`)
- `body` (required): Comment text

#### `jira_get_comments`
Get all comments for an issue.

**Parameters:**
- `issue_key` (required): Issue key (e.g., `PROJ-123`)

### Projects

#### `jira_list_projects`
List all accessible Jira projects.

**Parameters:**
- `max_results` (optional): Maximum results (1-100, default: 50)

#### `jira_get_project`
Get detailed information about a project.

**Parameters:**
- `project_key` (required): Project key (e.g., `PROJ`)

### Boards & Sprints

#### `jira_list_boards`
List all Jira boards.

**Parameters:**
- `project_key` (optional): Filter by project key
- `max_results` (optional): Maximum results (1-100, default: 50)

#### `jira_get_board`
Get detailed information about a board.

**Parameters:**
- `board_id` (required): Board ID

#### `jira_list_sprints`
List sprints for a board.

**Parameters:**
- `board_id` (required): Board ID
- `state` (optional): Filter by state - `active`, `future`, `closed`

#### `jira_get_sprint`
Get detailed information about a sprint.

**Parameters:**
- `sprint_id` (required): Sprint ID

#### `jira_get_sprint_issues`
Get all issues in a sprint.

**Parameters:**
- `sprint_id` (required): Sprint ID
- `max_results` (optional): Maximum results (1-100, default: 50)

### User Management

#### `jira_search_users`
Search for Jira users.

**Parameters:**
- `query` (required): Search query (name or email)
- `max_results` (optional): Maximum results (1-100, default: 50)

#### `jira_get_current_user`
Get information about the currently authenticated user.

**Parameters:** None

### Versions/Releases

#### `jira_list_versions`
List versions/releases for a project.

**Parameters:**
- `project_key` (required): Project key (e.g., `PROJ`)

#### `jira_get_version`
Get detailed information about a version/release.

**Parameters:**
- `version_id` (required): Version ID

## Resource URIs

The connector exposes these resource types:

- **Projects**: `jira://project/{projectKey}`
  - Returns full project information

- **Issues**: `jira://issue/{issueKey}`
  - Returns complete issue details

- **Boards**: `jira://board/{boardId}`
  - Returns board configuration and details

## Usage Examples

### Example 1: Create a Bug Report

```typescript
// Using Claude Desktop
"Create a bug in project MYAPP titled 'Login button not working' with high priority"

// This will call jira_create_issue with:
{
  "project_key": "MYAPP",
  "summary": "Login button not working",
  "issue_type": "Bug",
  "priority_name": "High",
  "description": "The login button on the main page is not responding to clicks"
}
```

### Example 2: Search for Your Open Issues

```typescript
"Show me all my open issues"

// This will call jira_search_issues with:
{
  "jql": "assignee = currentUser() AND status != Done",
  "max_results": 50
}
```

### Example 3: Move Issue to In Progress

```typescript
"Move PROJ-123 to In Progress"

// First, get available transitions:
{
  "issue_key": "PROJ-123"
}
// Returns: [{ "id": "11", "name": "In Progress", "to": "In Progress" }]

// Then transition the issue:
{
  "issue_key": "PROJ-123",
  "transition_id": "11"
}
```

### Example 4: View Sprint Backlog

```typescript
"Show me all issues in the current sprint for board 5"

// First, list sprints to find active one:
{
  "board_id": 5,
  "state": "active"
}
// Returns: [{ "id": 23, "name": "Sprint 5", "state": "active" }]

// Then get sprint issues:
{
  "sprint_id": 23
}
```

### Example 5: Add Comment to Issue

```typescript
"Add a comment to PROJ-456 saying 'Fixed in latest commit'"

// This will call jira_add_comment with:
{
  "issue_key": "PROJ-456",
  "body": "Fixed in latest commit"
}
```

## Understanding Jira IDs

Jira uses several types of IDs:

- **Issue Keys**: Human-readable like `PROJ-123` (project key + number)
- **Account IDs**: User identifiers like `557058:f5a4e8e3-b1e1-4f1a-9d3f-9c8b7a6f5e4d`
- **Transition IDs**: Numeric IDs for workflow transitions like `"11"`, `"21"`
- **Board/Sprint IDs**: Numeric IDs for agile entities

Use the search and list tools to discover these IDs.

## JQL (Jira Query Language)

JQL is a powerful query language for searching issues:

### Basic Syntax
```
field operator value
```

### Common Fields
- `project` - Project key
- `assignee` - User assigned to issue
- `status` - Current status
- `priority` - Issue priority
- `created`, `updated` - Timestamps
- `labels` - Issue labels
- `sprint` - Sprint name or ID

### Operators
- `=` - Equals
- `!=` - Not equals
- `>`, `<`, `>=`, `<=` - Comparison
- `IN` - In list
- `~` - Contains text

### Functions
- `currentUser()` - Currently logged in user
- `now()` - Current time
- `startOfDay()`, `endOfDay()` - Time functions

### Examples
```
project = MYAPP AND status = "In Progress"
assignee = currentUser() AND priority IN (High, Highest)
created >= -30d AND labels = urgent
sprint = "Sprint 5" AND status != Done
text ~ "database" ORDER BY updated DESC
```

## Troubleshooting

### Common Issues

**Issue**: "Invalid or expired Jira credentials"
- **Solution**: Re-authorize the connector through the SageMCP web interface

**Issue**: "No accessible Jira resources found"
- **Solution**: Ensure your Atlassian account has access to at least one Jira Cloud site

**Issue**: "Field does not exist" when creating issues
- **Solution**: Check your project's issue type configuration - some fields may be required or optional depending on project settings

**Issue**: "Transition not available"
- **Solution**: Use `jira_get_transitions` to see which transitions are available for the current issue state

**Issue**: "User not found" when assigning
- **Solution**: Use `jira_search_users` to find the correct account ID

### Finding Account IDs

To assign issues or mention users, you need their account ID:

1. Use `jira_search_users` with their name or email
2. Copy the `accountId` from the results
3. Use that ID in assign or mention operations

Account IDs look like: `557058:f5a4e8e3-b1e1-4f1a-9d3f-9c8b7a6f5e4d`

## API Versions

The connector uses:
- **Jira REST API v3** for core functionality (issues, projects, comments)
- **Jira Agile API v1.0** for boards and sprints

Both are fully supported by Jira Cloud.

## API Reference

- **Jira Platform REST API v3**: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
- **Jira Agile REST API**: https://developer.atlassian.com/cloud/jira/software/rest/
- **JQL Reference**: https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/
- **OAuth 2.0 Setup**: https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/

## Source Code

Implementation: `src/sage_mcp/connectors/jira.py`
