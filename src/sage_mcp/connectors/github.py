"""GitHub connector implementation."""

import json
from typing import Any, Dict, List, Optional

from mcp import types

from ..models.connector import Connector, ConnectorType
from ..models.oauth_credential import OAuthCredential
from .base import BaseConnector
from .registry import register_connector


@register_connector(ConnectorType.GITHUB)
class GitHubConnector(BaseConnector):
    """GitHub connector for accessing GitHub API."""
    
    @property
    def display_name(self) -> str:
        return "GitHub"
    
    @property
    def description(self) -> str:
        return "Access GitHub repositories, issues, pull requests, and more"
    
    @property
    def requires_oauth(self) -> bool:
        return True
    
    async def get_tools(self, connector: Connector, oauth_cred: Optional[OAuthCredential] = None) -> List[types.Tool]:
        """Get available GitHub tools."""
        tools = [
            types.Tool(
                name="github_list_repositories",
                description="List repositories for the authenticated user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["all", "owner", "public", "private", "member"],
                            "default": "all",
                            "description": "Type of repositories to list"
                        },
                        "sort": {
                            "type": "string", 
                            "enum": ["created", "updated", "pushed", "full_name"],
                            "default": "updated",
                            "description": "Sort order"
                        },
                        "per_page": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30,
                            "description": "Number of results per page"
                        }
                    }
                }
            ),
            types.Tool(
                name="github_get_repository",
                description="Get detailed information about a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string", 
                            "description": "Repository name"
                        }
                    },
                    "required": ["owner", "repo"]
                }
            ),
            types.Tool(
                name="github_list_issues",
                description="List issues for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "default": "open",
                            "description": "Issue state"
                        },
                        "labels": {
                            "type": "string",
                            "description": "Comma-separated list of labels"
                        },
                        "per_page": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30,
                            "description": "Number of results per page"
                        }
                    },
                    "required": ["owner", "repo"]
                }
            ),
            types.Tool(
                name="github_get_file_content",
                description="Get the content of a file from a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "path": {
                            "type": "string",
                            "description": "File path"
                        },
                        "ref": {
                            "type": "string",
                            "description": "Git reference (branch, tag, or commit SHA)"
                        }
                    },
                    "required": ["owner", "repo", "path"]
                }
            ),
            types.Tool(
                name="github_list_pull_requests",
                description="List pull requests for a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "Repository owner"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Repository name"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "default": "open",
                            "description": "Pull request state"
                        },
                        "per_page": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30,
                            "description": "Number of results per page"
                        }
                    },
                    "required": ["owner", "repo"]
                }
            ),
            types.Tool(
                name="github_search_repositories",
                description="Search for repositories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "sort": {
                            "type": "string",
                            "enum": ["stars", "forks", "help-wanted-issues", "updated"],
                            "description": "Sort field"
                        },
                        "order": {
                            "type": "string",
                            "enum": ["asc", "desc"],
                            "default": "desc",
                            "description": "Sort order"
                        },
                        "per_page": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30,
                            "description": "Number of results per page"
                        }
                    },
                    "required": ["q"]
                }
            ),
            types.Tool(
                name="github_check_token_scopes",
                description="Check the current OAuth token's scopes and user information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            types.Tool(
                name="github_list_organizations",
                description="List organizations the user belongs to",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            types.Tool(
                name="github_get_user_info",
                description="Get information about a specific GitHub user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username to look up"
                        }
                    },
                    "required": ["username"]
                }
            )
        ]
        
        return tools
    
    async def get_resources(self, connector: Connector, oauth_cred: Optional[OAuthCredential] = None) -> List[types.Resource]:
        """Get available GitHub resources."""
        if not oauth_cred or not self.validate_oauth_credential(oauth_cred):
            return []
        
        # Get user's repositories to create resource URIs
        try:
            response = await self._make_authenticated_request(
                "GET",
                "https://api.github.com/user/repos",
                oauth_cred,
                params={"type": "all", "per_page": 50}
            )
            repos = response.json()
            
            resources = []
            for repo in repos:
                owner = repo["owner"]["login"]
                name = repo["name"]
                
                # Add repository resource
                resources.append(types.Resource(
                    uri=f"github://repo/{owner}/{name}",
                    name=f"{owner}/{name}",
                    description=f"GitHub repository: {repo.get('description', 'No description')}"
                ))
                
                # Add common files as resources
                common_files = ["README.md", "package.json", "pyproject.toml", "Dockerfile", ".github/workflows"]
                for file_path in common_files:
                    resources.append(types.Resource(
                        uri=f"github://file/{owner}/{name}/{file_path}",
                        name=f"{owner}/{name}:{file_path}",
                        description=f"File in {owner}/{name}"
                    ))
            
            return resources
            
        except Exception as e:
            print(f"Error fetching GitHub resources: {e}")
            return []
    
    async def execute_tool(
        self,
        connector: Connector,
        tool_name: str,
        arguments: Dict[str, Any],
        oauth_cred: Optional[OAuthCredential] = None
    ) -> str:
        """Execute a GitHub tool."""
        if not oauth_cred or not self.validate_oauth_credential(oauth_cred):
            return "Error: Invalid or expired GitHub credentials"
        
        try:
            if tool_name == "list_repositories":
                return await self._list_repositories(arguments, oauth_cred)
            elif tool_name == "get_repository":
                return await self._get_repository(arguments, oauth_cred)
            elif tool_name == "list_issues":
                return await self._list_issues(arguments, oauth_cred)
            elif tool_name == "get_file_content":
                return await self._get_file_content(arguments, oauth_cred)
            elif tool_name == "list_pull_requests":
                return await self._list_pull_requests(arguments, oauth_cred)
            elif tool_name == "search_repositories":
                return await self._search_repositories(arguments, oauth_cred)
            elif tool_name == "check_token_scopes":
                return await self._check_token_scopes(oauth_cred)
            elif tool_name == "list_organizations":
                return await self._list_organizations(oauth_cred)
            elif tool_name == "get_user_info":
                return await self._get_user_info(arguments, oauth_cred)
            else:
                return f"Unknown tool: {tool_name}"
        
        except Exception as e:
            return f"Error executing GitHub tool '{tool_name}': {str(e)}"
    
    async def read_resource(
        self,
        connector: Connector,
        resource_path: str,
        oauth_cred: Optional[OAuthCredential] = None
    ) -> str:
        """Read a GitHub resource."""
        if not oauth_cred or not self.validate_oauth_credential(oauth_cred):
            return "Error: Invalid or expired GitHub credentials"
        
        try:
            # Parse resource path: repo/owner/name or file/owner/name/path
            parts = resource_path.split("/", 3)
            if len(parts) < 3:
                return "Error: Invalid resource path"
            
            resource_type = parts[0]
            owner = parts[1]
            repo_name = parts[2]
            
            if resource_type == "repo":
                # Return repository information
                response = await self._make_authenticated_request(
                    "GET",
                    f"https://api.github.com/repos/{owner}/{repo_name}",
                    oauth_cred
                )
                repo_data = response.json()
                return json.dumps(repo_data, indent=2)
            
            elif resource_type == "file" and len(parts) == 4:
                file_path = parts[3]
                # Return file content
                response = await self._make_authenticated_request(
                    "GET",
                    f"https://api.github.com/repos/{owner}/{repo_name}/contents/{file_path}",
                    oauth_cred
                )
                file_data = response.json()
                
                if file_data.get("type") == "file":
                    import base64
                    content = base64.b64decode(file_data["content"]).decode("utf-8")
                    return content
                else:
                    return json.dumps(file_data, indent=2)
            
            else:
                return "Error: Unsupported resource type"
        
        except Exception as e:
            return f"Error reading GitHub resource: {str(e)}"
    
    async def _list_repositories(self, arguments: Dict[str, Any], oauth_cred: OAuthCredential) -> str:
        """List user repositories."""
        params = {
            "type": arguments.get("type", "all"),
            "sort": arguments.get("sort", "updated"),
            "per_page": arguments.get("per_page", 30)
        }
        
        try:
            print(f"DEBUG: Making GitHub API request to /user/repos with params: {params}")
            response = await self._make_authenticated_request(
                "GET",
                "https://api.github.com/user/repos",
                oauth_cred,
                params=params
            )
            
            repos = response.json()
            print(f"DEBUG: GitHub API returned {len(repos)} repositories")
            
            result = []
            for repo in repos:
                result.append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "description": repo.get("description"),
                    "private": repo["private"],
                    "html_url": repo["html_url"],
                    "updated_at": repo["updated_at"]
                })
            
            return json.dumps(result, indent=2)
        
        except Exception as e:
            print(f"DEBUG: GitHub API error in _list_repositories: {str(e)}")
            print(f"DEBUG: Error type: {type(e)}")
            if hasattr(e, 'response'):
                print(f"DEBUG: HTTP status: {e.response.status_code}")
                print(f"DEBUG: Response text: {e.response.text}")
            raise
    
    async def _get_repository(self, arguments: Dict[str, Any], oauth_cred: OAuthCredential) -> str:
        """Get repository details."""
        owner = arguments["owner"]
        repo = arguments["repo"]
        
        response = await self._make_authenticated_request(
            "GET",
            f"https://api.github.com/repos/{owner}/{repo}",
            oauth_cred
        )
        
        return json.dumps(response.json(), indent=2)
    
    async def _list_issues(self, arguments: Dict[str, Any], oauth_cred: OAuthCredential) -> str:
        """List repository issues."""
        owner = arguments["owner"]
        repo = arguments["repo"]
        
        params = {
            "state": arguments.get("state", "open"),
            "per_page": arguments.get("per_page", 30)
        }
        
        if "labels" in arguments:
            params["labels"] = arguments["labels"]
        
        response = await self._make_authenticated_request(
            "GET",
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            oauth_cred,
            params=params
        )
        
        issues = response.json()
        result = []
        for issue in issues:
            # Skip pull requests (they appear in issues API)
            if "pull_request" not in issue:
                result.append({
                    "number": issue["number"],
                    "title": issue["title"],
                    "state": issue["state"],
                    "user": issue["user"]["login"],
                    "created_at": issue["created_at"],
                    "html_url": issue["html_url"]
                })
        
        return json.dumps(result, indent=2)
    
    async def _get_file_content(self, arguments: Dict[str, Any], oauth_cred: OAuthCredential) -> str:
        """Get file content from repository."""
        owner = arguments["owner"]
        repo = arguments["repo"]
        path = arguments["path"]
        ref = arguments.get("ref")
        
        params = {}
        if ref:
            params["ref"] = ref
        
        response = await self._make_authenticated_request(
            "GET",
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            oauth_cred,
            params=params
        )
        
        file_data = response.json()
        if file_data.get("type") == "file":
            import base64
            content = base64.b64decode(file_data["content"]).decode("utf-8")
            return f"File: {path}\n\n{content}"
        else:
            return json.dumps(file_data, indent=2)
    
    async def _list_pull_requests(self, arguments: Dict[str, Any], oauth_cred: OAuthCredential) -> str:
        """List repository pull requests."""
        owner = arguments["owner"]
        repo = arguments["repo"]
        
        params = {
            "state": arguments.get("state", "open"),
            "per_page": arguments.get("per_page", 30)
        }
        
        response = await self._make_authenticated_request(
            "GET",
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            oauth_cred,
            params=params
        )
        
        pulls = response.json()
        result = []
        for pr in pulls:
            result.append({
                "number": pr["number"],
                "title": pr["title"],
                "state": pr["state"],
                "user": pr["user"]["login"],
                "created_at": pr["created_at"],
                "html_url": pr["html_url"],
                "base": pr["base"]["ref"],
                "head": pr["head"]["ref"]
            })
        
        return json.dumps(result, indent=2)
    
    async def _search_repositories(self, arguments: Dict[str, Any], oauth_cred: OAuthCredential) -> str:
        """Search for repositories."""
        params = {
            "q": arguments["q"],
            "per_page": arguments.get("per_page", 30)
        }
        
        if "sort" in arguments:
            params["sort"] = arguments["sort"]
        if "order" in arguments:
            params["order"] = arguments["order"]
        
        response = await self._make_authenticated_request(
            "GET",
            "https://api.github.com/search/repositories",
            oauth_cred,
            params=params
        )
        
        search_results = response.json()
        result = {
            "total_count": search_results["total_count"],
            "repositories": []
        }
        
        for repo in search_results["items"]:
            result["repositories"].append({
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo.get("description"),
                "html_url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "language": repo.get("language")
            })
        
        return json.dumps(result, indent=2)
    
    async def _check_token_scopes(self, oauth_cred: OAuthCredential) -> str:
        """Check the current OAuth token's scopes and user information."""
        try:
            # Get current user information
            user_response = await self._make_authenticated_request(
                "GET",
                "https://api.github.com/user",
                oauth_cred
            )
            user_data = user_response.json()
            
            # Get the token's scopes from the response headers
            token_scopes = user_response.headers.get("X-OAuth-Scopes", "")
            accepted_scopes = user_response.headers.get("X-Accepted-OAuth-Scopes", "")
            
            # Also check what the stored credential says
            stored_scopes = oauth_cred.scopes if oauth_cred.scopes else "No scopes stored"
            
            result = {
                "user": {
                    "login": user_data.get("login"),
                    "id": user_data.get("id"),
                    "type": user_data.get("type"),
                    "name": user_data.get("name"),
                    "email": user_data.get("email"),
                    "company": user_data.get("company"),
                    "public_repos": user_data.get("public_repos"),
                    "private_repos": user_data.get("total_private_repos")
                },
                "token_info": {
                    "current_scopes": token_scopes.split(", ") if token_scopes else [],
                    "accepted_scopes": accepted_scopes.split(", ") if accepted_scopes else [],
                    "stored_scopes": stored_scopes,
                    "expires_at": str(oauth_cred.expires_at) if oauth_cred.expires_at else "No expiration"
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error checking token information: {str(e)}"
    
    async def _list_organizations(self, oauth_cred: OAuthCredential) -> str:
        """List organizations the user belongs to."""
        try:
            # Get user's organizations
            org_response = await self._make_authenticated_request(
                "GET",
                "https://api.github.com/user/orgs",
                oauth_cred
            )
            orgs_data = org_response.json()
            
            result = {
                "organizations": [],
                "total_count": len(orgs_data)
            }
            
            for org in orgs_data:
                result["organizations"].append({
                    "login": org.get("login"),
                    "id": org.get("id"),
                    "description": org.get("description"),
                    "url": org.get("url"),
                    "html_url": org.get("html_url")
                })
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error listing organizations: {str(e)}"
    
    async def _get_user_info(self, arguments: Dict[str, Any], oauth_cred: OAuthCredential) -> str:
        """Get information about a specific GitHub user."""
        username = arguments["username"]
        
        try:
            # Get user information
            user_response = await self._make_authenticated_request(
                "GET",
                f"https://api.github.com/users/{username}",
                oauth_cred
            )
            user_data = user_response.json()
            
            # Also try to get their repositories
            repos_response = await self._make_authenticated_request(
                "GET",
                f"https://api.github.com/users/{username}/repos",
                oauth_cred,
                params={"per_page": 20}
            )
            repos_data = repos_response.json()
            
            result = {
                "user": {
                    "login": user_data.get("login"),
                    "id": user_data.get("id"),
                    "type": user_data.get("type"),
                    "name": user_data.get("name"),
                    "company": user_data.get("company"),
                    "blog": user_data.get("blog"),
                    "location": user_data.get("location"),
                    "email": user_data.get("email"),
                    "bio": user_data.get("bio"),
                    "public_repos": user_data.get("public_repos"),
                    "public_gists": user_data.get("public_gists"),
                    "followers": user_data.get("followers"),
                    "following": user_data.get("following"),
                    "created_at": user_data.get("created_at"),
                    "updated_at": user_data.get("updated_at")
                },
                "repositories": []
            }
            
            for repo in repos_data:
                result["repositories"].append({
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "private": repo["private"],
                    "description": repo.get("description"),
                    "html_url": repo["html_url"],
                    "language": repo.get("language"),
                    "stargazers_count": repo["stargazers_count"],
                    "updated_at": repo["updated_at"]
                })
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error getting user info for {username}: {str(e)}"