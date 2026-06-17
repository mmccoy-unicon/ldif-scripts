#!/usr/bin/env python3

import base64
import pandas as pd
from ldif3 import LDIFParser
import matplotlib.pyplot as plt

# Monkey-patch Python 3.14's base64 module to restore the deleted function ldif3 needs
if not hasattr(base64, "decodestring"):
    base64.decodestring = base64.decodebytes

inputFile = "users.ldif"
schema_report = "schema_report.csv"
outReportRaw = "attribute_usage_report_raw.csv"
outReportName = "attribute_usage_report.csv"
outHistogramFile = "user_attribute_histogram.png"

def merge_schema_and_usage(schema_csv, usage_csv, output_csv):
    df_schema = pd.read_csv(schema_csv)
    df_usage = pd.read_csv(usage_csv)
    df_usage.rename(columns={df_usage.columns[0]: 'NAME'}, inplace=True)
    # An outer join ensures that if an attribute exists in the schema but has 0 usage,
    # or if an operational attribute exists in the data but wasn't in tne schema file,
    # neither gets dropped.
    df_master = pd.merge(df_schema, df_usage, on='NAME', how='outer')

    # Clean up missing values (indicate zero usage)
    df_master['Active Entries'] = df_master['Active Entries'].fillna(0).astype(int)
    df_master['Fill Rate (%)'] = df_master['Fill Rate (%)'].fillna(0.0)
    # Sort the report so that unused attributes are at the bottom
    df_master = df_master.sort_values(by='Active Entries', ascending=False)

    # Export to a final consolidated CSV
    df_master.to_csv(output_csv, index=False)
    print(f"Master consolidation complete! Saved to {output_csv}")


def ldif_to_dataframe(ldif_path):
    records = []
    with open(ldif_path, "rb") as f:
        parser = LDIFParser(f)
        # Loop through each entry in the LDIF file
        for dn, entry in parser.parse():
            # ldif3 returns data as bytes; decode it to strings
            record = {"dn": dn}
            for attr, values in entry.items():
                # If an attribute has multiple values, join them or take the first
                # For stringified JSON, there's usually just 1 value in the list
                record[attr] = values[0] if len(values) == 1 else values
            records.append(record)
    return pd.DataFrame(records)

df = ldif_to_dataframe(inputFile)

## generate report showing attribute usage percentages
attribute_counts = df.notnull().sum().sort_values(ascending=False)
usage_report = pd.DataFrame({
    'Active Entries': attribute_counts,
    'Fill Rate (%)': (attribute_counts / len(df)) * 100
})
usage_report.to_csv(outReportRaw)
print(f"Analyzed {len(df)} total users. Report saved in {outReportRaw}")
print("Most populated attributes:")
print(usage_report.head(20))
merge_schema_and_usage(schema_report, outReportRaw, outReportName)

## generate histogram showing attribute density across all users
attributes_per_user = df.notnull().sum(axis=1)
plt.figure(figsize=(10, 6))
plt.hist(attributes_per_user, bins=range(attributes_per_user.min(), attributes_per_user.max() + 2), edgecolor='black', color='teal', alpha=0.7)
plt.title('Distribution of Attribute Density Per User Record', fontsize=14)
plt.xlabel('Number of Unique Attributes Populated', fontsize=12)
plt.ylabel('Number of Users (Frequency)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
print(f"Saving plot to {outHistogramFile}")
plt.savefig(outHistogramFile, dpi=300)
