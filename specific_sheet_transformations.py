import pandas as pd
import numpy as np

def identity(df: pd.DataFrame) -> pd.DataFrame:
        # to be used as a default case for .get()
        # eg custom_transform_dict.get(curr_sheet_name, identity)(df)
        # where df is the curr_sheet_df of the given iteration
        return df

def NPS(col: pd.Series) -> pd.Series:
        res = pd.to_numeric(col,errors="coerce")
        output = np.select([res<=6,res>=9],[-100,100],default=0)

        return pd.Series(output)

def A3_A12_custom(df: pd.DataFrame) -> pd.DataFrame:
        # FORCE VALUES TO BE INT IF STRING
        A10_col_copy = pd.to_numeric(df.loc[:, "A10"],errors="coerce")

        df["A10_NPS"] = NPS(A10_col_copy)
                
        return df

def A4bA5single2(df: pd.DataFrame) -> pd.DataFrame:
        possible_codes = ['iOS', 'Android', 'Cable TV', 'Web Browser', 'TV App/Stick', 'Other']
        for code in possible_codes:
                df[code] = np.select([df["A4bA5single2"] == code],["Selected"],default="Not Selected")

        return df

def A4bA5single2_All_Platforms(df: pd.DataFrame) -> pd.DataFrame:
        possible_codes = ['iOS', 'Android', 'Cable TV', 'Web Browser', 'TV App/Stick', 'Other']
        df["All Platforms"] = np.select([df["A4bA5single2"].isin(possible_codes)],["Selected"],default="Not selected")

        return df

def A12(df: pd.DataFrame) -> pd.DataFrame:
        # As of Wave 21, this question has been removed. Will maintain logic in case it is ever re-introduced
        possible_codes = ['Yes, deﬁnitely', 'Yes, quite likely', 'No, not very likely', 'No, deﬁnitely not', 'I\'m not sure']

        for code in possible_codes:
                df[code] = np.select([df["A12"] == code, df["A12"] == "Missing data"],["Selected","Missing data"],default="Not Selected")
        
        return df

def A12b(df: pd.DataFrame) -> pd.DataFrame:
        # As of Wave 21, this question has been removed. Will maintain logic in case it is ever re-introduced
        possible_codes = ['Yes, deﬁnitely', 'Yes, quite likely', 'No, not very likely', 'No, deﬁnitely not', 'I\'m not sure']

        for code in possible_codes:
                df[code] = np.select([df["A12b"] == code, df["A12b"] == "Missing data"],["Selected","Missing data"],default="Not Selected")
        
        return df

def S9(df: pd.DataFrame) -> pd.DataFrame:
        possible_codes = ['Love it', 'Like it', 'It\'s ok, no strong opinion', 'Don\'t like it', 'Hate it']

        for code in possible_codes:
                df[code] = np.select([df["Hayu"] == code, df["Hayu"] == "Missing data"],["Selected","Missing data"],default="Not Selected")
        
        return df

def A10_Other_Services(df:pd.DataFrame) -> pd.DataFrame:
        codes_for_NPS = ['Netflix', 'Disney+', 'Amazon Prime Video', 'Paramount+']
        NPS_labels = ['Netflix_NPS', 'Disney_NPS', 'Amazon_NPS', 'Paramount_NPS']
        for i in range(len(codes_for_NPS)):
                df[NPS_labels[i]] = NPS(df[codes_for_NPS[i]])
        
        return df

def S8_STACKING(df:pd.DataFrame) -> pd.DataFrame:
        # Since the 'needed_cols' pulls ["UNIQUE_ID","WAVE","DATE","MONTH","YEAR"] into the new export df,
        # We want to remove MONTH, YEAR and DATE prior to unpivoting.
        # Normally, this type of transformation isn't happening so these columns get quietly removed
        # in steps following the custom transformation seen in the generate_sheet function and 
        # so never need to be explicitly handled like they are here
        df_prepped = df.drop(columns=["MONTH","YEAR","DATE"])

        # TO RECREATE STACKING, WE WILL MELT/UNPIVOT (wide-to-long) THE S8 COLUMNS INTO JUST ONE COLUMN
        # THE VALUES OF ALL THESE UNPIVOTED COLUMNS GO INTO A "value" COLUMN
        # THEN SINCE THE S8 COLUMN HEADERS WERE ALL OF THE FORM 'service_name - code',
        # WE CAN SPLIT THEM INTO TWO COLUMNS: 'service_name' AND 'codes'
        # WE WANT TO KEEP THE CODES IN ONE COLUMN, AND THE SERVICES TO THEN EACH HAVE THEIR OWN COLUMN
        # SO AT THIS POINT WE CAN PIVOT (long-to-wide) ON THE SERVICE COLUMN. THIS SHOULD THEN MATCH THE STACKED OUTPUT
        # UNPIVOT/MELT --> SPLIT THE STRING --> PIVOT THE SERVICES

        # MELT / UNPIVOT, the column names of this df will be ["UNIQUE_ID","WAVE","variable","value"]
        res = df_prepped.melt(id_vars=["UNIQUE_ID","WAVE"])

        # SPLIT
        #  .str.split(" - ",expand=True) lets each part of the split be in its own column in a dataframe
        # so with expand=True, you get two columns, ie the services and the codes. 
        # to match the pre-existing excel, I am naming the "codes" column "Attribute"
        res[["services","Attribute"]] = res["variable"].str.split(" - ",expand=True)
        res.drop(columns=["variable"],inplace=True) # remove the original "service - code" col now we have our separated service and code cols

        # PIVOT
        res = res.pivot(index=["UNIQUE_ID","WAVE","Attribute"], columns=["services"],values="value").reset_index()

        return res
