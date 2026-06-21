## Why

Before any Lambda tool can be registered or invoked over MCP, the AgentCore Gateway resource must exist. It is the single entry point that Claude Code connects to as an MCP server. Without it, none of the other changes (`weather-lambda-tool`, `stock-lambda-tool`, `register-tools`) can be verified end-to-end.

## What Changes

- New AWS AgentCore Gateway resource created in account `columbia` (169976659173), region `us-east-1`
- Gateway metadata (ID and MCP endpoint URL) recorded in `gateway_config.json` at repo root so downstream changes can reference it without manual lookup

## Capabilities

### New Capabilities

- `agentcore-gateway-resource`: The AgentCore Gateway itself — a managed MCP server endpoint hosted by AWS that Claude Code can connect to via the MCP protocol

### Modified Capabilities

<!-- None — this is a prerequisite infrastructure piece -->

## Impact

- One new AWS resource in the `columbia` account
- `gateway_config.json` added to repo (non-sensitive metadata only — no secrets)
- No Lambda functions, no tool registrations — those are separate changes
- Unblocks: `register-tools` change
