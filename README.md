# `tap-csv`
A Singer Tap for extracting data from CSV files built using the Meltano SDK.

CSV tap class.

Built with the [Meltano SDK](https://sdk.meltano.com) for Singer Taps and Targets.

## Capabilities

* `sync`
* `catalog`
* `discover`

Note: This tap currently does not support incremental state.

## Settings

| Setting              | Required | Default | Description                                                                                                        |
| :------------------- | :------- | :------ | :----------------------------------------------------------------------------------------------------------------- |
| files                | False    | None    | An array of csv file stream settings                                                                               |
| filesystem           | False    | local   | The filesystem to use for reading files                                                                            |
| csv_files_definition | False    | None    | A path to the JSON file holding an array of file settings                                                          |
| add_metadata_columns | False    | 0       | When True, add the metadata columns (`_sdc_source_file`, `_sdc_source_file_mtime`, `_sdc_source_lineno`) to output |

A full list of supported settings and capabilities is available by running: `tap-csv --about`

The `filesystem` setting can be used to specify the filesystem to use for reading files. The following filesystems are supported:

- `local`, the default, for reading files from the local filesystem.
- [`ftp`](#ftp), for reading files from an FTP server.
- [`github`](#github), for reading files from a GitHub repository.
- [`dropbox`](#dropbox), for reading files from a Dropbox account.

The `config.json` contains an array called `files` that consists of dictionary objects detailing each destination table to be passed to Singer. Each of those entries contains:
* `entity`: The entity name to be passed to singer (i.e. the table)
* `path`: Local path to the file to be ingested. Note that this may be a directory, in which case all files in that directory and any of its subdirectories will be recursively processed
* `keys`: The names of the columns that constitute the unique keys for that entity
* `encoding`: [Optional] The file encoding to use when reading the file (i.e. "latin1", "UTF-8"). Use this setting when you get a `UnicodeDecodeError` error.

The following entries are passed through in an internal CSV dialect that then is used to configure the CSV reader:
* `delimiter`: A one-character string used to separate fields. It defaults to ','.
* `doublequote`: Controls how instances of quotechar appearing inside a field should themselves be quoted. When True, the character is doubled. When False, the escapechar is used as a prefix to the quotechar. It defaults to True.
* `escapechar`: A one-character string used by the reader, where the escapechar removes any special meaning from the following character. It defaults to None, which disables escaping.
* `quotechar`: A one-character string used to quote fields containing special characters, such as the delimiter or quotechar, or which contain new-line characters. It defaults to '"'.
* `skipinitialspace`: When True, spaces immediately following the delimiter are ignored. The default is False.
* `strict`: When True, raise exception Error on bad CSV input. The default is False.

Example:

```json
{
	"files":	[
					{	"entity" : "leads",
						"path" : "/path/to/leads.csv",
						"keys" : ["Id"],
						"delimiter": ";"
					},
					{	"entity" : "opportunities",
						"path" : "/path/to/opportunities.csv",
						"keys" : ["Id"],
						"encoding" : "latin1",
						"skipinitialspace": true
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

### Filesystem settings

#### FTP

| Setting      | Required | Default | Description             |
| :----------- | :------- | :------ | :---------------------- |
| ftp          | False    | None    | FTP connection settings |
| ftp.host     | True     | None    | FTP server host         |
| ftp.port     | False    | 21      | FTP server port         |
| ftp.username | False    | None    | FTP username            |
| ftp.password | False    | None    | FTP password            |
| ftp.encoding | False    | utf-8   | FTP server encoding     |

#### GitHub

| Setting         | Required | Default | Description                                                 |
| :-------------- | :------- | :------ | :---------------------------------------------------------- |
| github          | False    | None    | GitHub connection settings                                  |
| github.org      | True     | None    | GitHub organization or user where the repository is located |
| github.repo     | True     | None    | GitHub repository                                           |
| github.username | False    | None    | GitHub username                                             |
| github.token    | False    | None    | GitHub token                                                |

#### Dropbox

| Setting       | Required | Default | Description                 |
| :------------ | :------- | :------ | :-------------------------- |
| dropbox       | False    | None    | Dropbox connection settings |
| dropbox.token | True     | None    | Dropbox token               |

### Built-in Singer SDK settings

The following settings are supported by the Singer SDK and are automatically handled by the tap:

| Setting              | Required | Default | Description                                                                                                                                                                                                                                              |
| :------------------- | :------- | :------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| stream_maps          | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html).                                                                                                              |
| stream_map_config    | False    | None    | User-defined config values to be used within map expressions.                                                                                                                                                                                            |
| faker_config         | False    | None    | Config for the [`Faker`](https://faker.readthedocs.io/en/master/) instance variable `fake` used within map expressions. Only applicable if the plugin specifies `faker` as an addtional dependency (through the `singer-sdk` `faker` extra or directly). |
| faker_config.seed    | False    | None    | Value to seed the Faker generator for deterministic output: https://faker.readthedocs.io/en/master/#seeding-the-generator                                                                                                                                |
| faker_config.locale  | False    | None    | One or more LCID locale strings to produce localized output for: https://faker.readthedocs.io/en/master/#localization                                                                                                                                    |
| flattening_enabled   | False    | None    | 'True' to enable schema flattening and automatically expand nested properties.                                                                                                                                                                           |
| flattening_max_depth | False    | None    | The max depth to flatten schemas.                                                                                                                                                                                                                        |

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
poetry run tox
poetry run tox -e pytest
poetry run tox -e format
poetry run tox -e lint
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
