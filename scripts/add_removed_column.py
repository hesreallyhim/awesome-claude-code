#!/usr/bin/env python3
"""
Temporary script to add 'Removed From Origin' column to CSV
Created to safely add the new column with FALSE for all rows except row 117
"""

import csv


def add_removed_column(csv_path):
    """Add 'Removed From Origin' column to CSV file."""

    # Read all data
    rows = []
    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader, start=1):
            rows.append((row_num, row))

    # Add new column header
    if rows:
        header_row = rows[0][1]
        header_row.append("Removed From Origin")

        # Add values to all other rows
        for row_num, row in rows[1:]:
            # Row 117 gets TRUE, all others get FALSE
            if row_num == 117:
                row.append("TRUE")
                print(f"Row {row_num}: Setting 'Removed From Origin' to TRUE for {row[1]}")
            else:
                row.append("FALSE")

    # Write back to file
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for _row_num, row in rows:
            writer.writerow(row)

    print(f"✅ Successfully added 'Removed From Origin' column to {csv_path}")
    print(f"   Total rows processed: {len(rows)}")


if __name__ == "__main__":
    csv_path = "/Users/hesreallyhim/coding/projects/awesome-claude-code/THE_RESOURCES_TABLE.csv"
    add_removed_column(csv_path)
