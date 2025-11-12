# GitHub Connector

The GitHub connector provides comprehensive integration with GitHub's API, enabling Claude Desktop to interact with repositories, issues, pull requests, workflows, and more through OAuth 2.0 authentication.

## Features

- **24 comprehensive tools** covering all major GitHub operations
- **Full OAuth 2.0 authentication** with organization access
- **Dynamic resource discovery** of repositories and files
- **Real-time access** to repositories, commits, branches, and workflows

## OAuth Setup

### Prerequisites

- A GitHub account
- Access to create OAuth apps (personal account or organization)

### Step-by-Step Configuration

1. **Create GitHub OAuth App**
   - Go to GitHub Settings → Developer settings → OAuth Apps
   - Click "New OAuth App"
   - Fill in the details:
     - **Application name**: `SageMCP` (or your preferred name)
     - **Homepage URL**: `http://localhost:3001` (or your deployment URL)
     - **Authorization callback URL**: `http://localhost:8000/api/v1/oauth/callback/github`
   - Click "Register application"

2. **Get Credentials**
   - Note the **Client ID**
   - Generate a new **Client Secret**
   - Save both credentials securely

3. **Configure SageMCP**
   - Add to your `.env` file:
     ```env
     GITHUB_CLIENT_ID=your_client_id_here
     GITHUB_CLIENT_SECRET=your_client_secret_here
     ```

4. **Add Connector in SageMCP**
   - Open SageMCP web interface
   - Create or select a tenant
   - Add GitHub connector
   - Complete OAuth authorization flow

### Required OAuth Scopes

The GitHub connector automatically requests these scopes:
- `repo` - Full access to repositories
- `read:org` - Read organization membership
- `user:email` - Access user email addresses
- `workflow` - Access GitHub Actions workflows

## Available Tools

### Repository Management

#### `github_list_repositories`
List repositories for the authenticated user.

**Parameters:**
- `type` (optional): Filter by type - `all`, `owner`, `public`, `private`, `member` (default: `all`)
- `sort` (optional): Sort by - `created`, `updated`, `pushed`, `full_name` (default: `updated`)
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_get_repository`
Get detailed information about a specific repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name

#### `github_search_repositories`
Search for repositories across GitHub.

**Parameters:**
- `q` (required): Search query
- `sort` (optional): Sort by - `stars`, `forks`, `help-wanted-issues`, `updated`
- `order` (optional): Sort order - `asc`, `desc` (default: `desc`)
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_get_repo_stats`
Get detailed statistics about a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name

### Issues & Pull Requests

#### `github_list_issues`
List issues for a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `state` (optional): Issue state - `open`, `closed`, `all` (default: `open`)
- `labels` (optional): Comma-separated list of labels
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_list_pull_requests`
List pull requests for a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `state` (optional): PR state - `open`, `closed`, `all` (default: `open`)
- `per_page` (optional): Results per page (1-100, default: 30)

### Files & Content

#### `github_get_file_content`
Get the content of a file from a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `path` (required): File path
- `ref` (optional): Git reference (branch, tag, or commit SHA)

### Commits & Branches

#### `github_list_commits`
List commits for a repository or branch.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `sha` (optional): SHA or branch to start listing from
- `path` (optional): Only commits containing this file path
- `author` (optional): GitHub username or email
- `since` (optional): Only commits after this date (ISO 8601)
- `until` (optional): Only commits before this date (ISO 8601)
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_get_commit`
Get details of a specific commit including files changed and diff.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `sha` (required): Commit SHA

#### `github_compare_commits`
Compare two commits or branches.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `base` (required): Base branch or commit SHA
- `head` (required): Head branch or commit SHA

#### `github_list_branches`
List branches for a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `protected` (optional): Filter by protected branches
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_get_branch`
Get detailed information about a branch.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `branch` (required): Branch name

### GitHub Actions Workflows

#### `github_list_workflows`
List GitHub Actions workflows for a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_list_workflow_runs`
List workflow runs for a repository or specific workflow.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `workflow_id` (optional): Workflow ID or filename to filter
- `status` (optional): Filter by status - `completed`, `action_required`, `cancelled`, `failure`, `success`, etc.
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_get_workflow_run`
Get details of a specific workflow run.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `run_id` (required): Workflow run ID

### Releases

#### `github_list_releases`
List releases for a repository.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `per_page` (optional): Results per page (1-100, default: 30)

#### `github_get_release`
Get details of a specific release.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `release_id` (required): Release ID, tag name, or `latest`

### Users & Organizations

#### `github_get_user_info`
Get information about a specific GitHub user.

**Parameters:**
- `username` (required): GitHub username

#### `github_get_user_activity`
Get user's recent activity including commits, PRs, and issues.

**Parameters:**
- `username` (required): GitHub username
- `per_page` (optional): Events per page (1-100, default: 30)

#### `github_get_user_stats`
Get statistics about a user's contributions and repositories.

**Parameters:**
- `username` (required): GitHub username

#### `github_list_organizations`
List organizations the authenticated user belongs to.

**Parameters:** None

#### `github_list_contributors`
List contributors to a repository with contribution stats.

**Parameters:**
- `owner` (required): Repository owner
- `repo` (required): Repository name
- `per_page` (optional): Results per page (1-100, default: 30)

### Authentication

#### `github_check_token_scopes`
Check the current OAuth token's scopes and user information.

**Parameters:** None

## Resource URIs

The connector exposes these resource types:

- **Repositories**: `github://repo/{owner}/{repo}`
  - Returns full repository information

- **Files**: `github://file/{owner}/{repo}/{path}`
  - Returns decoded file content
  - Common files (README.md, package.json, etc.) are auto-discovered

## Usage Examples

### Example 1: List Your Repositories

```typescript
// Using Claude Desktop
"List my GitHub repositories sorted by last updated"

// This will call github_list_repositories with:
{
  "type": "all",
  "sort": "updated",
  "per_page": 30
}
```

### Example 2: Get Repository Statistics

```typescript
"Get statistics for the repository mvmcode/SageMCP"

// This will call github_get_repo_stats with:
{
  "owner": "mvmcode",
  "repo": "SageMCP"
}
```

### Example 3: Search for Issues

```typescript
"Show me open issues labeled 'bug' in mvmcode/SageMCP"

// This will call github_list_issues with:
{
  "owner": "mvmcode",
  "repo": "SageMCP",
  "state": "open",
  "labels": "bug"
}
```

### Example 4: Monitor Workflow Runs

```typescript
"Show me failed workflow runs for mvmcode/SageMCP"

// This will call github_list_workflow_runs with:
{
  "owner": "mvmcode",
  "repo": "SageMCP",
  "status": "failure"
}
```

## Troubleshooting

### Common Issues

**Issue**: "Invalid or expired GitHub credentials"
- **Solution**: Re-authorize the connector through the SageMCP web interface

**Issue**: "Resource not accessible"
- **Solution**: Ensure you have proper permissions (repository access, organization membership)

**Issue**: "Rate limit exceeded"
- **Solution**: GitHub has API rate limits. Authenticated requests get 5,000 requests/hour. Wait or optimize your queries.

### Debug Mode

The connector includes debug logging. Check application logs for detailed API requests:
```
DEBUG: Making GitHub API request to /user/repos
DEBUG: GitHub API returned 200
```

## API Reference

- **GitHub REST API Documentation**: https://docs.github.com/en/rest
- **OAuth Scopes**: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
- **Rate Limiting**: https://docs.github.com/en/rest/overview/rate-limits-for-the-rest-api

## Source Code

Implementation: `src/sage_mcp/connectors/github.py`
