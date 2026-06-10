#!/usr/bin/env python3
import re
import csv


def parse_ldap_schema(input_file, output_csv):
    # Regex patterns for Attribute Types and Object Classes
    attr_pattern = re.compile(
        r"attributeTypes:\s*\(\s*([\d\.]+)\s+NAME\s+'([^']+)'\s*(?:DESC\s+'([^']+)')?",
        re.IGNORECASE,
    )
    oc_pattern = re.compile(
        r"objectClasses:\s*\(\s*[\d\.]+\s+NAME\s+'([^']+)'\s*.*?((?:MUST|MAY)\s+\(.[^\)]+\))",
        re.IGNORECASE | re.DOTALL,
    )

    attributes = {}  # Store as { 'name': { 'oid': '', 'desc': '', 'classes': [] } }

    with open(input_file, "r") as f:
        content = f.read()

    # 1. Extract all defined Attributes
    for match in attr_pattern.finditer(content):
        oid, name, desc = match.groups()
        attributes[name] = {
            "OID": oid,
            "NAME": name,
            "DESC": desc if desc else "",
            "OBJECT_CLASSES": [],
        }

    # 2. Map Attributes to Object Classes
    for match in oc_pattern.finditer(content):
        oc_name, attr_section = match.groups()
        # Clean the MUST/MAY block and extract attribute words
        found_attrs = re.findall(
            r"[\w-]+",
            attr_section.replace("MUST", "").replace("MAY", "").replace("$", " "),
        )
        for attr in found_attrs:
            if attr in attributes:
                attributes[attr]["OBJECT_CLASSES"].append(oc_name)

    # 3. Write to CSV
    with open(output_csv, "w", newline="") as csvfile:
        fieldnames = ["NAME", "OID", "DESC", "OBJECT_CLASSES"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for attr_name in sorted(attributes.keys()):
            row = attributes[attr_name]
            # Join classes with a semicolon for better CSV compatibility
            row["OBJECT_CLASSES"] = "; ".join(row["OBJECT_CLASSES"])
            writer.writerow(row)

    print(f"Successfully generated {output_csv}")


# Usage
parse_ldap_schema("schema.ldif", "schema_report.csv")
