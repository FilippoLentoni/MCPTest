import json
import sys
import warnings

warnings.filterwarnings("ignore")

import boto3
import click
from botocore.exceptions import ClientError, NoCredentialsError

_FUNCTION_NAME = "weather-tool"
_REGION = "us-east-1"


def _invoke_lambda(city: str, profile=None) -> dict:
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    client = session.client("lambda", region_name=_REGION)
    response = client.invoke(
        FunctionName=_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({"city": city}).encode(),
    )
    raw = json.loads(response["Payload"].read())
    if "FunctionError" in response:
        raise RuntimeError(raw.get("errorMessage", "Lambda function error"))
    content = raw.get("content", [{}])
    text = content[0].get("text", "") if content else ""
    return json.loads(text)


@click.group()
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit machine-readable JSON output.")
@click.option("--profile", default=None, help="AWS profile name (default: AWS_PROFILE env var or default profile).")
@click.pass_context
def cli(ctx, as_json, profile):
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    ctx.obj["profile"] = profile


@cli.command()
@click.option("--city", required=True, help="City name, e.g. Tokyo or New York.")
@click.pass_context
def get(ctx, city):
    """Return current weather for a city by invoking the weather-tool Lambda."""
    as_json = ctx.obj["as_json"]
    try:
        data = _invoke_lambda(city, profile=ctx.obj["profile"])
    except NoCredentialsError:
        msg = "AWS credentials not found. Configure via AWS_PROFILE, ~/.aws/credentials, or environment variables."
        if as_json:
            click.echo(json.dumps({"error": msg}))
        else:
            click.echo(f"Error: {msg}", err=True)
        sys.exit(1)
    except (ClientError, RuntimeError, ValueError, KeyError) as exc:
        msg = str(exc)
        if as_json:
            click.echo(json.dumps({"error": msg}))
        else:
            click.echo(f"Error: {msg}", err=True)
        sys.exit(1)

    if as_json:
        click.echo(json.dumps(data))
    else:
        click.echo(
            f"City:        {data.get('city')}\n"
            f"Condition:   {data.get('condition')}\n"
            f"Temperature: {data.get('temperature_c')}°C / {data.get('temperature_f')}°F\n"
            f"Humidity:    {data.get('humidity_percent')}%\n"
            f"Wind:        {data.get('wind_kph')} kph"
        )
