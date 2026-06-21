## 1. Project Structure

- [ ] 1.1 Create directory `src/weather_tool/` for Lambda source
- [ ] 1.2 Create `src/weather_tool/__init__.py` (empty)
- [ ] 1.3 Create `scripts/` directory for registration helper scripts
- [ ] 1.4 Create `tests/` directory for Lambda unit tests

## 2. Lambda Function (`src/weather_tool/handler.py`)

- [ ] 2.1 Implement `get_weather_data(city: str) -> dict` — calls `https://wttr.in/{city}?format=j1` with `urllib.request`, parses JSON, returns dict with keys: `city`, `temperature_c`, `temperature_f`, `condition`, `humidity_percent`, `wind_kph`
- [ ] 2.2 Implement `lambda_handler(event, context)` — extracts `city` from `event`, calls `get_weather_data`, wraps result as `{"content": [{"type": "text", "text": json.dumps(weather_dict)}]}`
- [ ] 2.3 Add input validation: raise descriptive error response (not exception) when `city` is missing or empty
- [ ] 2.4 Add error handling: catch `urllib.error.URLError` and HTTP errors from wttr.in; return error as content block, not unhandled exception
- [ ] 2.5 Map wttr.in JSON fields to the output schema:
  - `current_condition[0].temp_C` → `temperature_c`
  - `current_condition[0].temp_F` → `temperature_f`
  - `current_condition[0].weatherDesc[0].value` → `condition`
  - `current_condition[0].humidity` → `humidity_percent`
  - `current_condition[0].windspeedKmph` → `wind_kph`
  - `nearest_area[0].areaName[0].value` → `city`

## 3. SAM Template (`template.yaml`)

- [ ] 3.1 Create `template.yaml` at repo root with `AWSTemplateFormatVersion: '2010-09-09'` and `Transform: AWS::Serverless-2016-10-31`
- [ ] 3.2 Add `Globals` section: `Runtime: python3.12`, `Timeout: 30`, `MemorySize: 128`
- [ ] 3.3 Define `WeatherTool` resource of type `AWS::Serverless::Function` with:
  - `FunctionName: weather-tool`
  - `CodeUri: src/weather_tool/`
  - `Handler: handler.lambda_handler`
  - `Description: Returns current weather for a given city via wttr.in`
  - `Policies: [AWSLambdaBasicExecutionRole]`
- [ ] 3.4 Add `Outputs` section exporting `WeatherToolArn` (the Lambda ARN)
- [ ] 3.5 Create `samconfig.toml` with deployment defaults:
  - `stack_name = "weather-tool-stack"`
  - `region = "us-east-1"`
  - `confirm_changeset = false`
  - `capabilities = "CAPABILITY_IAM"`
  - Profile or account ID pointing to `columbia` (169976659173)

## 4. Unit Tests (`tests/test_weather_handler.py`)

- [ ] 5.1 Write test `test_valid_city_returns_weather_fields` — mock `urllib.request.urlopen` to return a sample wttr.in JSON fixture; assert all six output keys are present in the content text
- [ ] 5.2 Write test `test_missing_city_returns_error_content` — invoke handler with `{}` and assert response contains an error message in content, not an exception
- [ ] 5.3 Write test `test_empty_city_returns_error_content` — invoke handler with `{"city": ""}` and assert error content
- [ ] 5.4 Write test `test_wttr_http_error_returns_error_content` — mock `urlopen` to raise `urllib.error.HTTPError`; assert response is a content block, not an unhandled exception
- [ ] 5.5 Add `tests/fixtures/wttr_london_response.json` — sample wttr.in JSON for London (copy a real response and commit it)
- [ ] 5.6 Run `python -m pytest tests/ -v` and confirm all tests pass

## 6. Deployment Verification

- [ ] 6.1 Run `sam build` from repo root — confirm `WeatherTool` build succeeds with no errors
- [ ] 6.2 Run `sam deploy --profile columbia` (or with `--config-env columbia`) — confirm stack reaches `CREATE_COMPLETE`
- [ ] 6.3 Smoke test via AWS CLI:
  ```bash
  aws lambda invoke \
    --function-name weather-tool \
    --payload '{"city": "Rome"}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    /tmp/weather_response.json && cat /tmp/weather_response.json
  ```
  Confirm response contains `temperature_c`, `condition`, and `city` fields.
- [ ] 6.4 Confirm Lambda execution role has only `AWSLambdaBasicExecutionRole` (check IAM console or `aws iam list-attached-role-policies`)
- [ ] 6.5 Record the deployed Lambda ARN (`aws lambda get-function --function-name weather-tool --query 'Configuration.FunctionArn' --output text`) and save it — it is required by the `register-tools` change
