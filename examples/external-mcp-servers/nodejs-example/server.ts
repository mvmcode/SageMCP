#!/usr/bin/env node
/**
 * Example Node.js/TypeScript MCP Server for SageMCP
 *
 * This is a minimal example of an external MCP server that can be hosted by SageMCP.
 * It demonstrates how to:
 * 1. Create a simple MCP server using the Node.js MCP SDK
 * 2. Access OAuth tokens injected by SageMCP
 * 3. Define tools and execute them
 * 4. Integrate with external APIs
 *
 * To use this with SageMCP:
 * 1. Build: npm install && npm run build
 * 2. Configure connector with:
 *    - runtime_type: "external_nodejs"
 *    - runtime_command: '["node", "build/server.js"]'
 *    - package_path: "/path/to/this/directory"
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Create MCP server
const server = new Server(
  {
    name: "example-nodejs-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// List tools handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "greet",
        description: "Greet a user by name",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "The name to greet",
            },
          },
          required: ["name"],
        },
      },
      {
        name: "get_env_info",
        description: "Get information about the runtime environment",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "check_oauth",
        description: "Check if OAuth token is available (for testing)",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "fetch_data",
        description: "Fetch data from an external API (example using OAuth)",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "The URL to fetch",
            },
          },
          required: ["url"],
        },
      },
    ],
  };
});

// Call tool handler
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "greet") {
    const userName = (args as any).name || "stranger";
    return {
      content: [
        {
          type: "text",
          text: `Hello, ${userName}! Welcome to the Node.js MCP Server.`,
        },
      ],
    };
  }

  if (name === "get_env_info") {
    const tenantId = process.env.TENANT_ID || "not set";
    const connectorId = process.env.CONNECTOR_ID || "not set";
    const sagemcpMode = process.env.SAGEMCP_MODE || "not set";
    const nodeVersion = process.version;

    const info = `Runtime Environment Information:
- Tenant ID: ${tenantId}
- Connector ID: ${connectorId}
- SageMCP Mode: ${sagemcpMode}
- Node.js Version: ${nodeVersion}
`;

    return {
      content: [
        {
          type: "text",
          text: info,
        },
      ],
    };
  }

  if (name === "check_oauth") {
    const oauthToken = process.env.OAUTH_TOKEN || "";
    const accessToken = process.env.ACCESS_TOKEN || "";

    let status: string;
    if (oauthToken) {
      const maskedToken = oauthToken.substring(0, 8) + "..." + oauthToken.substring(oauthToken.length - 4);
      status = `✓ OAuth token available (OAUTH_TOKEN): ${maskedToken}`;
    } else if (accessToken) {
      const maskedToken = accessToken.substring(0, 8) + "..." + accessToken.substring(accessToken.length - 4);
      status = `✓ OAuth token available (ACCESS_TOKEN): ${maskedToken}`;
    } else {
      status = "✗ No OAuth token found in environment";
    }

    return {
      content: [
        {
          type: "text",
          text: status,
        },
      ],
    };
  }

  if (name === "fetch_data") {
    const url = (args as any).url;
    const oauthToken = process.env.OAUTH_TOKEN || process.env.ACCESS_TOKEN || "";

    try {
      const headers: Record<string, string> = {};
      if (oauthToken) {
        headers["Authorization"] = `Bearer ${oauthToken}`;
      }

      const response = await fetch(url, { headers });
      const data = await response.text();

      return {
        content: [
          {
            type: "text",
            text: `Fetched data from ${url}:\n\n${data.substring(0, 500)}${data.length > 500 ? "..." : ""}`,
          },
        ],
      };
    } catch (error: any) {
      return {
        content: [
          {
            type: "text",
            text: `Error fetching data: ${error.message}`,
          },
        ],
      };
    }
  }

  throw new Error(`Unknown tool: ${name}`);
});

// List resources handler
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "example://greeting",
        name: "Greeting Resource",
        description: "A simple example resource",
        mimeType: "text/plain",
      },
    ],
  };
});

// Read resource handler
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === "example://greeting") {
    return {
      contents: [
        {
          uri: "example://greeting",
          mimeType: "text/plain",
          text: "Hello from Node.js MCP Server!",
        },
      ],
    };
  }

  throw new Error(`Unknown resource: ${uri}`);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Log to stderr (stdout is used for MCP communication)
  console.error("Node.js MCP server started and ready");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
