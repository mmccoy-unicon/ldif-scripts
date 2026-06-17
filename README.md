# LDAP Analysis scripts

## Prerequisites

- Python3 with the following modules:
  - matplotlib
  - pandas

### Setup python with a virtual environment and install modules

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pandas
python3 -m pip install ldif3
```

### enable the venv later

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
