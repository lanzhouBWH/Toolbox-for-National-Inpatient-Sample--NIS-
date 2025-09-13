import pyreadstat
import multiprocessing
import pandas as pd
import numpy as np
import copy
import os
import xlsxwriter

Study_Name="HipKnees_Proc_v0.3 Date 7-16-24"

#### Define Directories ########################################################
Data_Path="/data/cci_radiology/CCI/TRG/NIS_Database/NIS_SAS/"
CodeSet_Path="/data/cci_radiology/CCI/TRG/John_Sam_Asprin/File/"
Function_Path="/data/cci_radiology/CCI/TRG/NIS_R_functions/"
MetaData_Path="/data/cci_radiology/CCI/TRG/John_Sam_Asprin/Meta_Data/"
Output_Path="/data/cci_radiology/CCI/TRG/John_Sam_Asprin/Output/"
################################################################################

os.makedirs(os.path.join(Output_Path, Study_Name), exist_ok=True)


Year=int(os.getenv('SLURM_ARRAY_TASK_ID'))
CodeSet = pd.read_excel(CodeSet_Path+Study_Name+'.xlsx', sheet_name = 'Sheet1')

df = pd.read_csv(MetaData_Path+Study_Name+str(Year)+".csv")
df_65 = df[df["AGE"] >= 65]
long_df_65 = pd.wide_to_long(df_65, ["I10_PR"], i="KEY_NIS", j="ProcNum").reset_index()
working=long_df_65[long_df_65['I10_PR'].notna()]


summary_table = working.groupby('I10_PR').agg(
    unique_KEY_NIS=('KEY_NIS', 'nunique'),   # Count unique KEY_NIS
    unique_DISCWT=('DISCWT', 'nunique'),     # Count unique DISCWT
    sum_DISCWT=('DISCWT', lambda x: np.ceil(x.sum()))            # Sum of DISCWT
).reset_index()

#result = working.groupby('I10_PR')['KEY_NIS'].nunique().reset_index()
summary_table.columns = ['ICD-10CODE', 'Unique_KEY_NIS_Count','unique_DISCWT','Weighted Count of Discharges']
merged_df = pd.merge(summary_table, CodeSet, on='ICD-10CODE', how='outer')


with pd.ExcelWriter(Output_Path+Study_Name+"/Weighted_Adjusted"+str(Year)+'.xlsx') as writer:
  merged_df.to_excel(writer, sheet_name='Year'+str(Year), index=False)

  
