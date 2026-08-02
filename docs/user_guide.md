# Aviation Audit Analytics — User Guide

## 1. Purpose

Aviation Audit Analytics is a management decision-support application designed for aviation Maintenance, Repair and Overhaul (MRO) organisations to analyse audit findings.

The application provides:

- Upload of Excel or CSV audit registers.
- Automatic data cleaning and validation.
- Executive dashboard.
- Severity analysis.
- Human factor analysis.
- Root cause analysis.
- Corrective action analysis.
- Preventive action analysis.
- Data quality assessment.
- Word management report generation.
- Excel analytics workbook generation.

---

## 2. Starting the Application

Activate the Conda environment:

```bash
conda activate audit-ai
```

Navigate to the project folder:

```bash
cd ~/Personal\ Projects/aviation-audit-analysis
```

Start Streamlit:

```bash
streamlit run app.py
```

Open the browser using the address shown in the terminal (normally):

```
http://localhost:8501
```

---

## 3. Uploading Audit Data

1. Select **Data Upload** from the navigation menu.
2. Upload an Excel (.xlsx) or CSV audit register.
3. The application automatically:
   - loads the file;
   - cleans the data;
   - validates mandatory fields;
   - standardises severity values;
   - reports any validation issues.
4. Review the validation summary before proceeding.

Once validation succeeds, the remaining dashboard pages become available.

---

## 4. Executive Overview

The Executive Overview page provides a management summary including:

- Total findings
- Major findings
- Minor findings
- Observations
- Response due-date position
- Leading human factor
- Leading root cause
- Severity Pareto chart
- Monthly response workload
- Deterministic management observations

### Important qualification

A response due date earlier than the selected report date is classified as **Past Due**.

Because the uploaded dataset does not currently include finding status or closure dates, this does **not** prove that the finding remains open.

---

## 5. Severity Analysis

The Severity Analysis page provides an overview of audit findings grouped by severity level.

### Dashboard KPIs

The page displays:

- Total findings
- Major findings
- Minor findings
- Observations
- Latest monthly change
- Latest quarterly change
- Latest yearly change

### Charts

The page includes:

- Severity Pareto chart
- Monthly response workload chart

The Pareto chart shows:

- findings ordered from highest frequency to lowest;
- cumulative percentage line;
- 80% Pareto reference line.

### Trend Tables

Monthly, quarterly and yearly trend tables are available.

These trends are calculated using the **Response Due Date**, not the original audit date.

### Management Observations

Automatically generated deterministic observations include:

- largest severity category;
- concentration of findings;
- monthly workload trend;
- Pareto concentration.

No AI-generated interpretations are used.

---

## 6. Human Factor Analysis

The Human Factor Analysis page identifies the most common human-factor categories associated with audit findings.

### Dashboard KPIs

The page displays:

- Total findings
- Specified human factors
- Unspecified human factors
- Unique human factors
- Leading human factor
- Monthly change
- Quarterly change
- Yearly change

### Charts

The Human Factor Pareto chart displays:

- human factors sorted by frequency;
- cumulative percentage;
- 80% Pareto reference.

### Trend Tables

Monthly

Quarterly

Yearly

trend tables are available.

### Management Observations

The dashboard highlights:

- most common human factor;
- proportion of specified records;
- Pareto concentration;
- recurring workforce issues.

---

## 7. Root Cause Analysis

The Root Cause Analysis page identifies the most frequently occurring organisational causes behind audit findings.

### Dashboard KPIs

Displayed metrics include:

- Total findings
- Specified root causes
- Unspecified root causes
- Unique root causes
- Leading root cause
- Monthly change
- Quarterly change
- Yearly change

### Charts

The Root Cause page contains a horizontal Pareto chart showing:

- root causes sorted from largest to smallest;
- cumulative percentage line;
- 80% Pareto reference.

### Trend Tables

Monthly

Quarterly

Yearly

trend summaries are available.

### Management Observations

The observations summarise:

- dominant organisational weaknesses;
- recurring process failures;
- Pareto concentration;
- long-term trends.

---

## 8. Corrective Action Analysis

The Corrective Action Analysis page summarises the corrective actions taken in response to audit findings.

### Dashboard KPIs

The page displays:

- Total findings
- Specified corrective actions
- Unspecified corrective actions
- Unique corrective actions
- Leading corrective action
- Latest monthly change
- Latest quarterly change
- Latest yearly change

### Charts

The page includes a horizontal Pareto chart showing:

- corrective actions sorted by frequency;
- cumulative percentage;
- 80% Pareto reference line.

### Trend Tables

Monthly, quarterly and yearly trend tables are available.

### Management Observations

The dashboard automatically summarises:

- most frequently used corrective actions;
- corrective-action concentration;
- recurring operational themes;
- long-term trends.

---

## 9. Preventive Action Analysis

The Preventive Action Analysis page focuses on long-term actions intended to prevent recurrence.

### Dashboard KPIs

Displayed metrics include:

- Total findings
- Specified preventive actions
- Unspecified preventive actions
- Unique preventive actions
- Leading preventive action
- Latest monthly change
- Latest quarterly change
- Latest yearly change

### Charts

A horizontal Pareto chart displays:

- preventive actions sorted from highest to lowest frequency;
- cumulative percentage;
- 80% Pareto reference line.

### Trend Tables

Monthly, quarterly and yearly trend tables are available.

### Management Observations

Automatically generated observations include:

- leading preventive action;
- Pareto concentration;
- preventive-action coverage;
- recurring prevention themes.

---

## 10. Data Quality

The Data Quality page summarises the results of dataset validation.

### Dashboard KPIs

The page displays:

- Rows loaded
- Validation status
- Total issues
- Missing required columns
- Duplicate references
- Missing due dates
- Invalid severities

### Validation Summary

Validation checks include:

- duplicate reference numbers;
- missing finding descriptions;
- missing response due dates;
- missing root causes;
- missing corrective actions;
- missing preventive actions;
- invalid severity values;
- missing mandatory columns.

### Missing-Value Summary

The dashboard reports missing values for every required field.

### Exception Records

Exception tables identify:

- invalid severity values;
- duplicate references;
- missing due dates.

If no exceptions exist, confirmation messages are displayed.

---

## 11. Reports

The Reports page generates management-ready reports.

### Word Report

The Microsoft Word report includes:

- cover page;
- executive summary;
- KPI summary;
- leading human factor;
- leading root cause;
- severity Pareto summary;
- monthly workload summary;
- management observations;
- management considerations;
- report limitations.

### Excel Analytics Workbook

The Excel workbook contains:

- Executive Summary
- Severity Analysis
- Human Factors
- Root Causes
- Corrective Actions
- Preventive Actions
- Data Quality
- Cleaned Audit Data

### Downloading Reports

Select **Generate Reports**.

The application generates:

- Microsoft Word management report (.docx)
- Microsoft Excel analytics workbook (.xlsx)

Both reports become available for download immediately after generation.

---

## 12. Known Limitations

The application currently assumes:

- the uploaded dataset has already been cleaned;
- one row represents one audit finding;
- response due date is available;
- severity values follow the supported categories.

Current limitations include:

- no audit status tracking;
- no closure-date analysis;
- no predictive analytics;
- no external database connection;
- no user authentication;
- no multi-user collaboration.

---

## 13. Technical Stack

The application is built using:

- Python 3.11
- Streamlit
- Pandas
- Altair
- OpenPyXL
- python-docx
- Pytest
- Ruff
- MyPy

The project follows:

- deterministic analytics;
- reusable analytics engines;
- reusable UI components;
- modular architecture;
- automated testing.

---

## 14. Support

Before reporting an issue:

1. Confirm the audit dataset loads successfully.
2. Verify that validation has passed.
3. Regenerate the reports.
4. Review any error messages displayed in the application.

If problems persist, review the project logs and rerun the automated test suite.

---

## 15. Version

Current release:

**Version 1.0**

Prepared for:

**Management Decision Support – Aviation MRO Audit Analytics**