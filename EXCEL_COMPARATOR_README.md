# Excel Comparator Tool

## Overview
A Java utility to compare two Excel files (.xlsx) and display differences in the console with color-coded output.

## Features
✓ Compares multiple sheets
✓ Detects structure differences (missing sheets, rows, columns)
✓ Shows cell-by-cell differences
✓ Color-coded console output for easy reading
✓ Supports all Excel data types (text, numbers, dates, formulas, booleans)

## Prerequisites
- Java 11 or higher
- Maven (for building)

## Building the Tool

```bash
# Compile and package
mvn clean package

# This creates: target/excel-comparator-1.0.0-jar-with-dependencies.jar
```

## Usage

```bash
# Run the comparator
java -jar target/excel-comparator-1.0.0-jar-with-dependencies.jar file1.xlsx file2.xlsx

# Or compile and run directly
javac -cp ".;poi-5.2.5.jar;poi-ooxml-5.2.5.jar" ExcelComparator.java
java -cp ".;poi-5.2.5.jar;poi-ooxml-5.2.5.jar" ExcelComparator file1.xlsx file2.xlsx
```

## Output Example

```
================================================================================
EXCEL FILE COMPARISON
================================================================================
File 1: data/report_v1.xlsx
File 2: data/report_v2.xlsx
================================================================================

📊 Comparing Sheet: Sales Data
--------------------------------------------------------------------------------
  ⚠ Cell B3:
    File 1: "1000.50"
    File 2: "1050.75"
  
  ⚠ Cell D5:
    File 1: "Pending"
    File 2: "Completed"

================================================================================
COMPARISON SUMMARY
================================================================================
✗ DIFFERENCES FOUND:
  - Total cell differences: 2
```

## Color Legend
- 🔴 RED: Missing data or errors
- 🟢 GREEN: File 2 values
- 🟡 YELLOW: Warnings and cell references
- 🔵 BLUE: Section headers

## Supported Excel Features
- Multiple sheets
- Text, numbers, dates
- Formulas
- Boolean values
- Blank cells
- Cell formatting detection

## Notes
- Files must be in .xlsx format (Excel 2007+)
- Large files may take time to process
- Numeric comparisons use 0.0001 tolerance for floating-point precision
