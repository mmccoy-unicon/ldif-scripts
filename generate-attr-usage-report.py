#!/usr/bin/env python3

import base64
import pandas as pd
from ldif3 import LDIFParser
import matplotlib.pyplot as plt

# Monkey-patch Python 3.14's base64 module to restore the deleted function ldif3 needs
if not hasattr(base64, "decodestring"):
    base64.decodestring = base64.decodebytes

inputFile = "users.ldif"
outReportName = "attribute_usage_report.csv"
outHistogramFile = "user_attribute_histogram.png"

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

usage_report.to_csv(outReportName)
print(f"Analyzed {len(df)} total users. Report saved in {outReportName}")
print("Most populated attributes:")
print(usage_report.head(20))

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
