**Legacy Power BI Update Automation**

**Overview**

  This pipeline automates the process of updating a legacy Power BI dashboard's data import file 
  each survey wave. Previously, this required manual copying and reformatting of data across many 
  Excel sheets — a repetitive, error-prone process. 
  The script replaces this entirely: run it once per wave and the import file is ready to refresh the dashboard.
  
**The Problem**

  The dashboard's import file was updated each wave by manually copying and pasting new export data into 
  each of its 30+ sheets, then dragging down Excel formulas across each one. With a new wave arriving 
  regularly, this was a significant time cost and an obvious source of human error.

  Bridging this cleanly, without hardcoding column lists for every sheet, required a systematic approach 
  to variable extraction — solved here by embedding each variable's destination sheet into its column name 
  via a suffix convention, allowing the script to dynamically route columns to the correct sheet.
  
**How It Works**

  **Column Mapping via Suffix Convention**
    The new export uses a naming convention where columns are suffixed with the sheet they belong to (e.g. Q1 -Demographics-). 
    The script uses this to dynamically identify which columns belong to each sheet, strips the suffix so new and old column names 
    align, and then concatenates the data — all without hardcoding column lists per sheet.
    
  **Sheet-Specific Transformations**
    A dictionary maps sheet names to transformation functions. Sheets that need no transformation receive an 
    identity function by default, keeping the main loop clean. Custom transformations include:

  NPS scoring — converts raw 0–10 ratings into -100/0/100 scores
  Dummy coding — expands single-response columns into Selected/Not Selected binary columns per response code
  Stacking (S8) — performs a full melt > string split > pivot pipeline to reshape wide survey data into a stacked long format matching the dashboard's expected structure

  **Wave Metadata**
  
  Unique IDs are assigned sequentially from the existing maximum, and wave/date metadata is derived 
  automatically from the export's completion timestamps — including formatting the wave label from 
  the earliest date in the new data.
    
**Main Loop**

    for sheet in sheets_to_update:
      generate_new_sheet(sheet, new_export)
    
  Each iteration parses the relevant sheet, maps and strips suffixes, applies the appropriate transformation, 
  concatenates with historical data, and writes the result to the output file.
  
**Usage**

  Drop the new wave export into the designated filepath
  Run update.py
  Refresh the Power BI dashboard

**Dependencies**

pandas
numpy
