## 1. Project Structure

- [ ] 1.1 Create directory `src/weather_tool/` for Lambda source
- [ ] 1.2 Create `src/weather_tool/__init__.py` (empty)
- [ ] 1.3 Create `tests/` directory for Lambda unit tests

## 2. Lambda Function (`src/weather_tool/handler.py`)

- [ ] 2.1 Implement `get_weather_data(city: str) -> dict` — calls `https://wttr.in/{city}?format=j1` with `urllib.request`, parses JSON, returns dict with keys: `city`, `temperature_c`, `temperature_f`, `condition`, `humidity_percent`, `wind_kph`
- [ ] 2.2 Implement `lambda_handler(event, context)` — extracts `city` from `event`, calls `get_weather_data`, wraps result as `{"content": [{"type": "text", "text": json.dumps(weather_dict)}]}`
- [ ] 2.3 Add input validation: return a descriptive error content block (not an exception) when `city` is missing or empty
- [ ] 2.4 Add error handling: catch `urllib.error.URLError` and HTTP errors from wttr.in; return error as content block, not unhandled exception
- [ ] 2.5 Map wttr.in JSON fields to the output schema:
  - `current_condition[0].temp_C` → `temperature_c`
  - `current_condition[0].temp_F` → `temperature_f`
  - `current_condition[0].weatherDesc[0].value` → `condition`
  - `current_condition[0].humidity` → `humidity_percent`
  - `current_condition[0].windspeedKmph` → `wind_kph`
  - `nearest_area[0].areaName[0].value` → `city`

## 3. CDK Stack (`cdk/stacks/weather_tool_stack.py`)

*Prerequisite: the CDK app scaffolding was created in the `agentcore-gateway` change. `cdk/app.py` and `cdk/stacks/__init__.py` already exist.*

- [ ] 3.1 Create `cdk/stacks/weather_tool_stack.py` with a `WeatherToolStack` class extending `cdk.Stack`
- [ ] 3.2 Define the Lambda function using the L2 construct:
  ```python
  from aws_cdk import aws_lambda as lambda_

  weather_fn = lambda_.Function(
      self, "WeatherTool",
      function_name="weather-tool",
      runtime=lambda_.Runtime.PYTHON_3_12,
      handler="handler.lambda_handler",
      code=lambda_.Code.from_asset("src/weather_tool"),
      timeout=cdk.Duration.seconds(30),
      memory_size=128,
      description="Returns current weather for a given city via wttr.in",
  )
  ```
- [ ] 3.3 Add a CDK stack output for the Lambda ARN:
  ```python
  cdk.CfnOutput(self, "WeatherToolArn", value=weather_fn.function_arn)
  ```
- [ ] 3.4 Register the stack in `cdk/app.py`:
  ```python
  from stacks.weather_tool_stack import WeatherToolStack

  WeatherToolStack(
      app, "WeatherToolStack",
      env=cdk.Environment(account="169976659173", region="us-east-1"),
  )
  ```

## 4. Unit Tests (`tests/test_weather_handler.py`)

- [ ] 4.1 Write test `test_valid_city_returns_weather_fields` — mock `urllib.request.urlopen` to return a sample wttr.in JSON fixture; assert all six output keys are present in the content text
- [ ] 4.2 Write test `test_missing_city_returns_error_content` — invoke handler with `{}` and assert response contains an error message in content, not an exception
- [ ] 4.3 Write test `test_empty_city_returns_error_content` — invoke handler with `{"city": ""}` and assert error content
- [ ] 4.4 Write test `test_wttr_http_error_returns_error_content` — mock `urlopen` to raise `urllib.error.HTTPError`; assert response is a content block, not an unhandled exception
- [ ] 4.5 Add `tests/fixtures/wttr_london_response.json` — sample wttr.in JSON for London (copy a real response and commit it)
- [ ] 4.6 Run `python -m pytest tests/ -v` and confirm all tests pass

## 5. Synthesise and Deploy

- [ ] 5.1 From the `cdk/` directory, run:
  ```bash
  cdk synth WeatherToolStack
  ```
  Confirm the synthesised template contains a `AWS::Lambda::Function` resource named `weather-tool`.
- [ ] 5.2 Deploy:
  ```bash
  cdk deploy WeatherToolStack --profile columbia
  ```
  Confirm the stack reaches `CREATE_COMPLETE` and CDK prints the `WeatherToolArn` output value.

## 6. Deployment Verification

- [ ] 6.1 Smoke test via AWS CLI:
  ```bash
  aws lambda invoke \
    --function-name weather-tool \
    --payload '{"city": "Rome"}' \
    --cli-binary-format raw-in-base64-out \
    --region us-east-1 \
    --profile columbia \
    /tmp/weather_response.json && cat /tmp/weather_response.json
  ```
  Confirm the response contains `temperature_c`, `condition`, and `city` fields.
- [ ] 6.2 Confirm Lambda execution role has only `AWSLambdaBasicExecutionRole`:
  ```bash
  aws iam list-attached-role-policies \
    --role-name $(aws lambda get-function-configuration \
      --function-name weather-tool --region us-east-1 \
      --query 'Role' --output text | cut -d'/' -f2)
  ```
- [ ] 6.3 Record the Lambda ARN from the CDK output — it is required by the `register-tools` change:
  ```bash
  aws cloudformation describe-stacks \
    --stack-name WeatherToolStack \
    --region us-east-1 \
    --profile columbia \
    --query "Stacks[0].Outputs[?OutputKey=='WeatherToolArn'].OutputValue" \
    --output text
  ```
