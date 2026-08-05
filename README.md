# LDAP Analysis scripts

## Prerequisites

- Python3 with the following modules:
  - matplotlib
  - pandas
  - ldif3

### Setup python with a virtual environment and install modules

Note: use a venv instance instead of the system-wide installation of Python, so that 
you can install these modules without conflicting with the system-installed version of Python.


```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pandas
python3 -m pip install matplotlib
python3 -m pip install ldif3
```

### enable the venv

Note: this must be done once per login session prior to running the other Python
scripts. This will ensure the correct venv instance of Python is used with the
installed modules.

```bash
source .venv/bin/activate
```

## Usage

### Generate a schema report

The schema report takes an exported schema LDIF and creates a CSV file containing the metadata about each attribute (name, OID, description, objectclasses, etc).

This report can be used when generating the usage report later. This should be done once at the beginning of the analysis and then only when the schema changes.

```bash
cd ldif
../scripts/schema-to-csv.py
```

### Generate the usage report

Ensure that the schema CSV has been created, then run this script:

```bash
../scripts/generate-attr-usage-report.py
```
