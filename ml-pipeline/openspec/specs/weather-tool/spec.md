## Requirements

### Requirement: Accept a city name and return current weather
The system SHALL expose a Lambda function that accepts a JSON payload containing a `city` string and returns structured current weather data for that city. The function SHALL be invocable by an AgentCore Gateway as an MCP tool.

#### Scenario: Valid city provided
- **WHEN** the Lambda is invoked with `{"city": "London"}`
- **THEN** the function returns a content block containing a JSON object with fields: `city`, `temperature_c`, `temperature_f`, `condition`, `humidity_percent`, `wind_kph`

#### Scenario: City not found
- **WHEN** the Lambda is invoked with a city name that wttr.in cannot resolve
- **THEN** the function returns a content block with a human-readable error message and does NOT raise an unhandled exception

#### Scenario: Empty city string
- **WHEN** the Lambda is invoked with `{"city": ""}` or the `city` key is missing
- **THEN** the function returns a content block with the message `"city parameter is required and must be a non-empty string"` and does NOT raise an unhandled exception

---

### Requirement: Return structured JSON weather data
The system SHALL return weather data in a consistent, machine-readable JSON structure so that the calling agent can extract specific fields without text parsing.

#### Scenario: Response structure
- **WHEN** weather data is successfully retrieved
- **THEN** the `text` field in the content block is a valid JSON string containing exactly these keys:
  - `city` (string) — the resolved city name as returned by wttr.in
  - `temperature_c` (number) — current temperature in Celsius
  - `temperature_f` (number) — current temperature in Fahrenheit
  - `condition` (string) — plain-English weather description, e.g. "Partly cloudy"
  - `humidity_percent` (number) — relative humidity as a percentage (0–100)
  - `wind_kph` (number) — wind speed in kilometres per hour

#### Scenario: Response wrapping for AgentCore
- **WHEN** the Lambda handler returns
- **THEN** the response body is `{"content": [{"type": "text", "text": "<json_string>"}]}`
- **AND** the HTTP status code is 200

---

### Requirement: Deployable via CDK with no manual steps
The system SHALL include a CDK stack (`WeatherToolStack` in `cdk/stacks/weather_tool_stack.py`) that, when deployed with `cdk deploy WeatherToolStack`, creates the Lambda function in account `columbia` (169976659173), region `us-east-1`, with the function name `weather-tool`. No AWS Console interaction SHALL be required.

#### Scenario: CDK deploy succeeds
- **WHEN** `cdk deploy WeatherToolStack --profile columbia` is run with valid credentials for the `columbia` account
- **THEN** the CloudFormation stack `WeatherToolStack` is created with a Lambda function resource in state `CREATE_COMPLETE`
- **AND** CDK prints a `WeatherToolArn` output value

#### Scenario: Deploy to a different account
- **WHEN** the `account` in `WeatherToolStack`'s `cdk.Environment(...)` is changed to a different account ID
- **AND** `cdk deploy` is run with credentials for that account
- **THEN** an identical Lambda function is created in that account — no other code changes required

#### Scenario: Lambda execution role
- **WHEN** the stack is deployed
- **THEN** the Lambda execution role has only `AWSLambdaBasicExecutionRole` attached (least privilege — no extra permissions needed for an outbound HTTP call)

---

### Requirement: Smoke-testable via the AWS CLI after deploy
The system SHALL support direct Lambda invocation via the AWS CLI so that a developer can verify the function independently of the AgentCore Gateway.

#### Scenario: Direct invocation via AWS CLI
- **WHEN** a developer runs:
  ```bash
  aws lambda invoke \
    --function-name weather-tool \
    --payload '{"city": "Rome"}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 --profile columbia \
    response.json
  ```
- **THEN** `response.json` contains a valid weather content block for Rome
- **AND** the AWS CLI exits with status code 0

---

### Requirement: Weather tool is invocable via MCP through the AgentCore Gateway
The system SHALL allow a Claude Code session to call the weather tool by name over MCP — no direct Lambda invocation or IAM Lambda permissions required from the caller.

#### Scenario: Claude Code calls get_weather via MCP
- **WHEN** a Claude Code session has `agentcore-gateway` configured as an MCP server
- **AND** the user asks for the weather in any city (e.g. "what's the weather in Tokyo?")
- **THEN** Claude Code invokes the `get_weather` tool via the MCP endpoint
- **AND** the response contains a JSON object with `city`, `temperature_c`, `temperature_f`, `condition`, `humidity_percent`, `wind_kph`

#### Scenario: Tool schema exposed to MCP clients
- **WHEN** an MCP client calls `tools/list` on the gateway endpoint
- **THEN** the response includes a tool entry with name `get_weather`, a description, and an input schema requiring a `city` string parameter
