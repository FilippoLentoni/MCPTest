## Context

Greenfield Lambda function. No existing code to migrate. The function will be registered in an AWS AgentCore Gateway so that a Claude Code agent connecting via MCP can invoke it during a conversation. The target AWS account is `columbia` (169976659173), region `us-east-1`.

The overall system has three planned features: `weather-lambda-tool` (this change), `stock-lambda-tool`, and `agentcore-gateway` (which will create the Gateway resource itself). This change assumes the Gateway already exists or is created manually before registration; the `agentcore-gateway` change will codify it in IaC.

## Goals / Non-Goals

**Goals:**
- Lambda returns structured weather JSON (temp °C/°F, description, humidity, wind km/h)
- Zero external API keys required in this iteration (use wttr.in public endpoint)
- SAM template deploys the function and registers it as an AgentCore tool
- Agent can invoke `get_weather(city="London")` through the MCP Gateway and receive readable weather data

**Non-Goals:**
- Caching or rate-limit handling (wttr.in has generous limits for demo use)
- Historical weather or forecasts
- Multi-city batch requests
- Authentication on the Lambda URL
- VPC placement

## Decisions

### D1: Use wttr.in as the weather data source
`GET https://wttr.in/{city}?format=j1` returns structured JSON with no API key. This removes credential management for a first iteration and keeps the focus on the AgentCore integration.

**Alternatives considered:**
- OpenWeatherMap — requires account + API key, adds secret management complexity
- Open-Meteo — requires geocoding step to convert city name to lat/lon first

### D2: Python 3.12 Lambda runtime
Consistent with team's Python toolchain. `urllib.request` from stdlib handles the HTTP call; no third-party packages needed, so no Lambda layer or Docker image required.

**Alternatives considered:**
- Node.js 20 — no strong reason to switch runtimes for a simple HTTP wrapper

### D3: SAM for deployment
AWS SAM (`template.yaml`) is the lightest-weight IaC option that natively understands Lambda. A single `sam deploy` command deploys the function. CDK adds unnecessary abstraction for a two-resource stack.

**Alternatives considered:**
- AWS CDK — better for large stacks; overkill here
- Terraform — adds HCL dependency, slower iteration

### D4: Lambda response format for AgentCore
AgentCore expects the Lambda to return a response conforming to the MCP tool result contract. The function returns:

```json
{
  "content": [
    {
      "type": "text",
      "text": "<JSON-encoded weather object>"
    }
  ]
}
```

The `text` value is a JSON string containing the structured weather fields so the calling agent can parse it.

**Alternatives considered:**
- Return plain text description — loses structure, harder for agent to extract specific values
- Return raw wttr.in response — too verbose (>50 fields), pollutes agent context

### D5: Input validation in the Lambda
The function validates that `city` is a non-empty string and returns a descriptive error in the MCP `content` field (not an HTTP 500) if the city is not found or wttr.in returns an error. This keeps the MCP contract clean — the gateway never sees a Lambda invocation error.

### D6: Tool schema definition
The `get_weather` tool is registered with this input schema:

```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "Name of the city to get weather for, e.g. 'London' or 'New York'"
    }
  },
  "required": ["city"]
}
```

## Risks / Trade-offs

- **wttr.in availability** — public free service, no SLA. Acceptable for demo/experiment; replace with OpenWeatherMap for production.
- **City name ambiguity** — "Springfield" matches multiple cities. wttr.in picks the most popular match. Document this limitation.
- **Cold start latency** — Python 3.12 with no dependencies has a cold start under 500 ms. Acceptable for interactive agent use.

## Open Questions

- Should the AgentCore tool registration be done via SAM (using a custom resource) or via a separate `aws bedrock-agent` CLI call post-deploy? (Deferred — tasks.md uses CLI for now; IaC approach tracked in `agentcore-gateway` change.)
