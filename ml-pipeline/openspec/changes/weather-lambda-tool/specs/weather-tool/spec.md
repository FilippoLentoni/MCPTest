## ADDED Requirements

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

### Requirement: Deployable via SAM in the columbia account
The system SHALL include a SAM `template.yaml` that, when deployed with `sam deploy`, creates the Lambda function in account `columbia` (169976659173), region `us-east-1`, with the function name `weather-tool`.

#### Scenario: SAM deploy succeeds
- **WHEN** `sam deploy --guided` is run with valid AWS credentials for the `columbia` account
- **THEN** the CloudFormation stack `weather-tool-stack` is created with a `WeatherTool` Lambda resource in state `CREATE_COMPLETE`

#### Scenario: Lambda execution role
- **WHEN** the stack is deployed
- **THEN** the Lambda execution role has only `AWSLambdaBasicExecutionRole` attached (least privilege — no extra permissions needed for an outbound HTTP call)

---

### Requirement: Callable with curl for smoke testing
The system SHALL support direct Lambda invocation via the AWS CLI so that a developer can verify the function independently of the AgentCore Gateway.

#### Scenario: Direct invocation via AWS CLI
- **WHEN** a developer runs:
  ```
  aws lambda invoke \
    --function-name weather-tool \
    --payload '{"city": "Rome"}' \
    --cli-binary-format raw-in-base64-out \
    response.json
  ```
- **THEN** `response.json` contains a valid weather content block for Rome
- **AND** the AWS CLI exits with status code 0
