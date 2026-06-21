## Why

To expose a weather tool through the AgentCore MCP Gateway, we need a Lambda function that a coding agent can invoke to look up current weather conditions for any city. This is the first of two tool Lambdas that will back the gateway; without it the MCP endpoint has no tools to serve.

## What Changes

- New AWS Lambda function `weather-tool` that accepts a city name and returns current weather data by calling the wttr.in public API
- AWS CDK stack (`WeatherToolStack`) for reproducible deployment to account `columbia` (169976659173) and portable to any other account

## Capabilities

### New Capabilities

- `weather-tool`: Lambda function that takes a `city` string and returns current conditions (temperature, description, humidity, wind) for that city

### Modified Capabilities

<!-- None — this is a new capability -->

## Impact

- New Lambda function in `columbia` account, `us-east-1` region
- New CDK stack `WeatherToolStack` added to the shared CDK app in `cdk/`
- No breaking changes to existing resources; tool registration happens in the separate `register-tools` change
