from setuptools import find_packages, setup

setup(
    name="weather-tool-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "weather-cli=weather_tool_cli.cli:cli",
        ],
    },
)
