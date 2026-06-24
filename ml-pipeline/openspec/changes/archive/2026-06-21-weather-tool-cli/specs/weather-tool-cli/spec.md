## ADDED Requirements

### Requirement: CLI invokes weather-tool Lambda directly
The system SHALL provide a `weather-cli` command that invokes the `weather-tool` Lambda function via `boto3` using the standard AWS credential chain. No MCP gateway or HTTP endpoint SHALL be required.

#### Scenario: Successful invocation
- **WHEN** `weather-cli get --city Tokyo` is run with valid AWS credentials
- **THEN** the CLI prints the weather result for Tokyo to stdout
- **AND** exits with code 0

#### Scenario: Missing city argument
- **WHEN** `weather-cli get` is run without `--city`
- **THEN** the CLI prints a usage error to stderr
- **AND** exits with a non-zero code

#### Scenario: Invalid city
- **WHEN** `weather-cli get --city "zzz_not_a_city"` is run
- **THEN** the CLI prints the error message returned by the Lambda
- **AND** exits with code 1

---

### Requirement: CLI supports JSON output mode
The system SHALL emit machine-readable JSON when the `--json` flag is provided, for both success and error cases.

#### Scenario: JSON success output
- **WHEN** `weather-cli get --city London --json` is run
- **THEN** stdout contains a valid JSON object with keys `city`, `temperature_c`, `temperature_f`, `condition`, `humidity_percent`, `wind_kph`
- **AND** the process exits with code 0

#### Scenario: JSON error output
- **WHEN** `weather-cli get --city "zzz_not_a_city" --json` is run
- **THEN** stdout contains a JSON object with key `error`
- **AND** the process exits with code 1

---

### Requirement: CLI is installable and on PATH
The system SHALL be installable via `pip install -e src/weather_tool_cli` and the `weather-cli` command SHALL be available on `PATH` after installation.

#### Scenario: Command available after install
- **WHEN** `pip install -e src/weather_tool_cli` is run in the project venv
- **THEN** `weather-cli --help` succeeds and prints usage information

---

### Requirement: CLI is discoverable by agents via SKILL.md
The system SHALL include a `SKILL.md` at the repo root that describes the CLI's commands, flags, and output format so AI coding agents can discover and use it without reading source code.

#### Scenario: Agent reads SKILL.md to learn CLI usage
- **WHEN** an agent reads `SKILL.md`
- **THEN** it can construct a valid `weather-cli get --city <city> --json` invocation without inspecting source code
