# `tap-csv`
A Singer Tap for extracting data from CSV files built using the Meltano SDK.

CSV tap class.

Built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps and Targets.

## Capabilities

* `sync`
* `catalog`
* `state`
* `discover`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| files               | False    | None    | An array of csv file stream settings. |
| csv_files_definition| False    | None    | A path to the JSON file holding an array of file settings. |

A full list of supported settings and capabilities is available by running: `tap-csv --about`

The `config.json` contains an array called `files` that consists of dictionary objects detailing each destination table to be passed to Singer. Each of those entries contains: 
* `entity`: The entity name to be passed to singer (i.e. the table)
* `path`: Local path to the file to be ingested. Note that this may be a directory, in which case all files in that directory and any of its subdirectories will be recursively processed
* `keys`: The names of the columns that constitute the unique keys for that entity

Example:

```json
{
	"files":	[ 	
					{	"entity" : "leads",
						"path" : "/path/to/leads.csv",
						"keys" : ["Id"]
					},
					{	"entity" : "opportunities",
						"path" : "/path/to/opportunities.csv",
						"keys" : ["Id"]
					}
				]
}
```

Optionally, the files definition can be provided by an external json file:

**config.json**
```json
{
	"csv_files_definition": "files_def.json"
}
```


**files_def.json**
```json
[ 	
	{	"entity" : "leads",
		"path" : "/path/to/leads.csv",
		"keys" : ["Id"]
	},
	{	"entity" : "opportunities",
		"path" : "/path/to/opportunities.csv",
		"keys" : ["Id"]
	}
]
```

## Installation

```bash
pipx install git+https://github.com/MeltanoLabs/tap-csv.git
```

## Usage

You can easily run `tap-csv` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-csv --version
tap-csv --help
tap-csv --config CONFIG --discover > ./catalog.json
```

## Developer Resources

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_csv/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-csv` CLI interface directly using `poetry run`:

```bash
poetry run tap-csv --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-csv
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-csv --version
# OR run a test `elt` pipeline:
meltano elt tap-csv target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
