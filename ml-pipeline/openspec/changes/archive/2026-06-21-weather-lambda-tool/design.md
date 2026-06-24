## Context

Greenfield Lambda function. No existing code to migrate. The function will be registered in an AWS AgentCore Gateway so that a Claude Code agent connecting via MCP can invoke it during a conversation. The target AWS account is `columbia` (169976659173), region `us-east-1`.

All AWS infrastructure in this project is deployed via AWS CDK (Python) — no SAM, no manual console steps. The CDK app lives in `cdk/` (established in the `agentcore-gateway` change); this change adds one stack file to it.

The overall system has four planned changes: `agentcore-gateway`, `weather-lambda-tool` (this change), `stock-lambda-tool`, and `register-tools`.

## Goals / Non-Goals

**Goals:**
- Lambda returns structured weather JSON (temp °C/°F, description, humidity, wind km/h)
- Zero external API keys required in this iteration (use wttr.in public endpoint)
- CDK stack deploys the function reproducibly to any account
- Agent can invoke `get_weather(city="London")` through the MCP Gateway and receive readable weather data once tool registration is done in the `register-tools` change

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

### D3: AWS CDK (Python) for deployment
This change adds `cdk/stacks/weather_tool_stack.py` to the shared CDK app established in `agentcore-gateway`. The Lambda is defined using the `aws_cdk.aws_lambda.Function` L2 construct. Deploy with `cdk deploy WeatherToolStack --profile columbia`.

Using CDK is consistent with the project-wide decision (see `agentcore-gateway` design D1): all infrastructure is CDK so stacks are portable, reproducible, and diffable in git.

**Alternatives considered:**
- SAM — Lambda-native but a separate toolchain; mixing SAM and CDK adds complexity and the project already uses CDK
- Terraform — adds HCL and a second state management system; rejected

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

- Tool registration (wiring the Lambda ARN into the Gateway) is handled in the separate `register-tools` change.
