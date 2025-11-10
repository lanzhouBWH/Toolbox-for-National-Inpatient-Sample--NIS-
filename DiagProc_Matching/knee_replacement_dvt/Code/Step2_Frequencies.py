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

Study_Name="knee_replacement_dvt"
Version="v0.1"
Study_Type="DiagProc"

Official=Study_Name+"_"+Study_Type+"_"+Version

#### Define Directories ########################################################
Data_Path="/data/cci_radiology/CCI/TRG/NIS_Database/NIS_SAS/"
Function_Path="/data/cci_radiology/CCI/TRG/NIS_Study_Codes/NIS_Python_Function/"
CodeSet_Path="/data/cci_radiology/CCI/TRG/NIS_Study_Codes/"+Study_Type+"_Matching/"+Study_Name+"/File/"
MetaData_Path="/data/cci_radiology/CCI/TRG/NIS_Study_Codes/"+Study_Type+"_Matching/"+Study_Name+"/Meta/"
Output_Path="/data/cci_radiology/CCI/TRG/NIS_Study_Codes/"+Study_Type+"_Matching/"+Study_Name+"/Output/"
################################################################################


Files_all=os.listdir(Function_Path)
for filename in Files_all:
    exec(open(Function_Path + filename).read())

vv_PR=["I10_PR"]
vv_DX=["I10_DX"]
Year=int(os.getenv('SLURM_ARRAY_TASK_ID'))

vv=vv_PR[0]
#### Processing CodeSet ####################################
CodeSet= pd.read_excel(CodeSet_Path+Official+'.xlsx', sheet_name = 'Proc')
# Create an empty column for the new data
CodeSet['DESCRIPTION'] = ""
CodeSet['CATEGORY1'] = ""
# Use a for loop to populate the new column
# Create an empty column for the new data
CodeSet['DESCRIPTION'] = ""
CodeSet['CATEGORY1'] = ""
ICD10PROC = InnerMap.load("ICD10PROC")
# Use a for loop to populate the new column
for i in range(len(CodeSet)):
      CodeSet.at[i, 'DESCRIPTION'] = ICD10PROC.lookup(CodeSet.at[i,vv])
      CodeSet.at[i, 'CATEGORY1'] = Study_Name

CodeSet_PR= copy.deepcopy(CodeSet)
##############################################################




vv=vv_DX[0]
#### Processing CodeSet ####################################
CodeSet= pd.read_excel(CodeSet_Path+Official+'.xlsx', sheet_name = 'Diag')
# Create an empty column for the new data
CodeSet['DESCRIPTION'] = ""
CodeSet['CATEGORY1'] = ""
# Use a for loop to populate the new column
# Create an empty column for the new data
CodeSet['DESCRIPTION'] = ""
CodeSet['CATEGORY1'] = ""
ICD10CM = InnerMap.load("ICD10CM")
# Use a for loop to populate the new column
for i in range(len(CodeSet)):
      CodeSet.at[i, 'DESCRIPTION'] = ICD10CM.lookup(CodeSet.at[i,vv])
      CodeSet.at[i, 'CATEGORY1'] = Study_Name

CodeSet_DX= copy.deepcopy(CodeSet)
##############################################################


### Applyting Exclusion Criteria
import pickle
with open(MetaData_Path+Official+str(Year)+".pkl", 'rb') as f:
    df = pickle.load(f)
###
df= df[df["AGE"] >= 65]

Study_VV=["KEY_NIS",'DISCWT','AGE',"DIED","LOS","FEMALE","TOTCHG"]

NIS_Frequencies_PR_DX(df,CodeSet_PR,CodeSet_DX,Study_VV,Study_Name,ICD10PROC,ICD10CM)
