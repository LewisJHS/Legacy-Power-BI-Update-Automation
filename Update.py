import pandas as pd
import numpy as np
import sheet_specific_transforms as transform

custom_transform_map = {
        "A3 - A12": transform.A3_A12_custom,
        "A4bA5single2": transform.A4bA5single2,
        "A4bA5single2 - All Platforms":transform.A4bA5single2_All_Platforms,
        "A12":transform.A12,
        "A12b":transform.A12b,
        "S9":transform.S9,
        "A10 Other Services":transform.A10_Other_Services,
        "S8":transform.S8_STACKING
}

#=====================IMPORT/EXPORT FILES ==============================================
devspace_import_path = r"Dashboard Import Excel filepath"
new_export_filepath = r"New Wave Export filepath"
#=====================IMPORT/EXPORT FILES ==============================================

# CREATE IMPORT AND EXPORT DATAFRAMES, CREATE EXCEL WRITER TO HANDLE INSERTING MULTIPLE SHEETS TO THE SAME WORKBOOK FILE
pbi_xl = pd.ExcelFile(devspace_import_path) #pd.ExcelFile opens file once then accesses separate sheets. whereas pd.read_excel(file,sheet_name=1) will open and close the file each time
new_export = pd.read_excel(new_export_filepath)
# mode w overwrites whatever was there, mode a does not so the 'if_sheet_exists' exists to specify how to handle cases where a sheet of same name already exists in file
writer = pd.ExcelWriter(r"Updated Data Import filepath",mode="w")
#====================================

#===DEFINE COLUMNS THAT REPEAT ON ALL/MULTIPLE SHEETS============
old = pbi_xl.parse("Demographics")
unique_id_start = old["UNIQUE_ID"].max() + 1
id_end = unique_id_start + len(new_export) # is actually 1 too big but range() is exclusive

new_export["UNIQUE_ID"] = range(unique_id_start, id_end)

# below uses wave and date to return the export wave in the format seen for import, 
# but per new export we only want to title the wave with the earliest month year seen among all the new dates
# earliest_date is a scalar, not a series/df so .dt.month etc is not applicable {though in general you can do dt.strftime(...)}
# use .strftime() to convert it to a string of your chosen format
# %Y for 4-digit year, %y for 2 digit year, %m for months as '03','05' etc, "%B" for 'January','February' etc
new_export["date: Completion time and date"] = pd.to_datetime(new_export["date: Completion time and date"],dayfirst=True,format="mixed")
earliest_date = new_export["date: Completion time and date"].min()
new_export["WAVE"] = new_export["WAVE"] + earliest_date.strftime(" (%b '%y)") # eg "Wave 21 (Feb'26)"
new_export["MONTH"] = new_export['date: Completion time and date'].dt.month_name()
new_export["YEAR"] = new_export["date: Completion time and date"].dt.year
new_export["DATE"] = new_export["MONTH"] + " " + new_export["YEAR"].astype(str)

needed_cols = ["UNIQUE_ID", "WAVE", "DATE", "MONTH", "YEAR"]
#===DEFINE COLUMNS THAT REPEAT ON ALL/MULTIPLE SHEETS============



def generate_new_sheet(cur_sheet: str, new_export: pd.DataFrame):
        old = pbi_xl.parse(cur_sheet) #pd.ExcelFile(filepath).parse(sheet_name) faster than read_excel since it doesnt needlessly re-open the file
        old = old[[x for x in old.columns if "Unnamed" not in x]]
        suffix = " -" + cur_sheet + "-"
        cols_unique_to_sheet = [col for col in new_export.columns if suffix in col]

        if not cols_unique_to_sheet:
                print(f"No variables with suffix '{suffix}' were found in the export. This question is either old or missing from the export. 'Missing data' will fill all new rows added.")
        
        cols_unique_to_sheet_suffix_removed = [col.partition(suffix)[0] for col in new_export.columns if suffix in col]
        cols_to_use = needed_cols + cols_unique_to_sheet
        tidy_cols = needed_cols + cols_unique_to_sheet_suffix_removed

        new = new_export[cols_to_use]

        # REMOVE SUFFIX FROM COL LABELS SO THE NEW AND OLD LABELS WILL MATCH IN CONCAT
        new.columns = tidy_cols

        #======TRANSFORMATION APPLIED============
        new = custom_transform_map.get(cur_sheet,transform.identity)(new)
        #========================================

        # 'list(old.columns) + new_cols_to_include' ensure that the old cols remain in right order, then new cols are at the end
        new_cols_to_include = [x for x in new.columns if x not in old.columns]
        # old.columns is a pandas.index object so the "+" operator won't append the list as expected. must convert to list
        output = pd.concat([old, new],ignore_index=True)[list(old.columns) + new_cols_to_include].fillna("Missing data")

        output.to_excel(writer,sheet_name=cur_sheet,index=False)
        return

sheets_to_update = ['Demographics', 'S8', 'A2', 'A3', 'A3 - A12', 'A4bA5', 'A4bA5single2', 'A4bA5single2 - DATE', 
                 'A4bA5single2 - All Platforms', 'A12', 'A12b', 'A13', 'A14', 'A15a. Hayu', 'A15c,e,f', 
                 'A15d', 'A17a', 'A18a', 'A18b', 'S9', 'A10 Other Services', 'S9 Other Services']

for sheet in sheets_to_update:
        print(f"about to generate {sheet}")
        generate_new_sheet(sheet,new_export)
        print(f"Generated {sheet}")

writer.close()
print("Export Updated!")
