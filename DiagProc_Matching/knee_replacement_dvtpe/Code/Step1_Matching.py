import simple_icd_10_cm as cm
import pyreadstat
import multiprocessing
import pandas as pd
import numpy as np
import copy
import os
import xlsxwriter
from tqdm import tqdm
from pyhealth.medcode import InnerMap

Study_Name="knee_replacement_dvtpe"
Version="v0.1"
Study_Type="DiagProc"

Official=Study_Name+"_"+Study_Type+"_"+Version


#### Define Directories ########################################################
Function_Path="/data/cci_radiology/CCI/TRG/NIS_Study_Codes/NIS_Python_Function/"
Data_Path="/data/cci_radiology/CCI/TRG/NIS_Database/NIS_SAS/"
CodeSet_Path="/data/cci_radiology/CCI/TRG/NIS_Study_Codes/"+Study_Type+"_Matching/"+Study_Name+"/File/"
MetaData_Path="/data/cci_radiology/CCI/TRG/NIS_Study_Codes/"+Study_Type+"_Matching/"+Study_Name+"/Meta/"
################################################################################

Files_all=os.listdir(Function_Path)
for filename in Files_all:
    exec(open(Function_Path + filename).read())

Type="core"
Year=int(os.getenv('SLURM_ARRAY_TASK_ID'))
Vars=["AGE","HOSP_NIS","KEY_NIS","I10_PR","I10_DX","WT","DIED","LOS","RACE","FEMALE","TOTCHG"]
vv_PR=["I10_PR"]
vv_DX=["I10_DX"]


CodeSet_PR = pd.read_excel(CodeSet_Path+Official+'.xlsx', sheet_name = 'Proc')
CodeSet_DX = pd.read_excel(CodeSet_Path+Official+'.xlsx', sheet_name = 'Diag')



##### Step 1: Reading Data ##############################
df=NIS_Data_Reader(Type,Year,Vars,Data_Path)
#########################################################


##### Step 2: Finding Mathes ############################
ICD10_CODE_PR=CodeSet_PR['I10_PR'].to_numpy()
df_PR=Only_Matched(df,vv_PR,ICD10_CODE_PR)

## DX
ICD10_CODE_DX=CodeSet_DX['I10_DX'].to_numpy()
df_PR_DX=Only_Matched(df_PR,vv_DX,ICD10_CODE_DX)

df= copy.deepcopy(df_PR_DX)

df.to_pickle(MetaData_Path+Official+str(Year)+".pkl")
#########################################################
