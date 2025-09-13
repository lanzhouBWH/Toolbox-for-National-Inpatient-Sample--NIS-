import pyreadstat
import multiprocessing
import pandas as pd
import numpy as np
import copy
import os

Study_Name="HipKnees_Proc_v0.3 Date 7-16-24"

#### Define Directories ########################################################
Data_Path="/data/cci_radiology/CCI/TRG/NIS_Database/NIS_SAS/"
CodeSet_Path="/data/cci_radiology/CCI/TRG/John_Sam_Asprin/File/"
Function_Path="/data/cci_radiology/CCI/TRG/NIS_R_functions/"
MetaData_Path="/data/cci_radiology/CCI/TRG/John_Sam_Asprin/Meta_Data/"
################################################################################


Type="core"
Year=int(os.getenv('SLURM_ARRAY_TASK_ID'))
Vars=["AGE","HOSP_NIS","KEY_NIS","I10_PR","WT"]
vv=["I10_PR"]



CodeSet = pd.read_excel(CodeSet_Path+Study_Name+'.xlsx', sheet_name = 'Sheet1')




##### Step 1: Reading Data ##############################
def NIS_Data_Reader(Type,Year,Vars,Data_Path):
  num_processes = multiprocessing.cpu_count()
  File_Name=Data_Path+"nis_"+str(Year)+"_"+Type+".sas7bdat"
  metadf= (pyreadstat.read_sas7bdat(File_Name, metadataonly=True))
  column_names = metadf[0].columns
  matching_columns = [col for col in column_names if any(var in col for var in Vars)]
  df= pyreadstat.read_file_multiprocessing(pyreadstat.read_sas7bdat, File_Name,num_processes=num_processes,usecols=matching_columns)
  return(df[0])

df=NIS_Data_Reader(Type,Year,Vars,Data_Path)
#########################################################


##### Step 2: Finding Mathes ############################
ICD10_CODE=CodeSet['ICD-10CODE'].to_numpy()

def Only_Matched(df,vv,ICD10_CODE):
  df2=copy.deepcopy(df)
  column_names = df.columns
  matching_columns = [col for col in column_names if any(var in col for var in vv)]
  
  # Define the function to check for substring matches
  def match_icd(code):
    if pd.isna(code):
      return np.nan
    if any(icd_code in code for icd_code in ICD10_CODE):
      return code
    return np.nan
  
  for col in matching_columns:
    print(col)
    if col in df2.columns:
      df2[col] = df2[col].apply(match_icd)
  return(df2)

df2=Only_Matched(df,vv,ICD10_CODE)
df2.to_csv(MetaData_Path+Study_Name+str(Year)+".csv")
#########################################################
