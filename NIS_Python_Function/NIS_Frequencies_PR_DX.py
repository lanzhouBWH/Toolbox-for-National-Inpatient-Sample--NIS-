def NIS_Frequencies_PR_DX(df,CodeSet_PR,CodeSet_DX,Study_VV,Study_Name,ICD10PROC,ICD10CM):
  #### Calculating Pairs ######################################
  vv_PR=["I10_PR"]
  vv_DX=["I10_DX"]
  column_names = df.columns
  matching_columns_PR = [col for col in column_names if any(var in col for var in vv_PR)]
  matching_columns_DX = [col for col in column_names if any(var in col for var in vv_DX)]
  
  non_na_counts_PR = df[matching_columns_PR].count(axis=1)
  non_na_counts_DX = df[matching_columns_DX].count(axis=1)
  non_na_counts=non_na_counts_PR+non_na_counts_DX
  df['non_na_counts']=non_na_counts
  filtered_df = df[df['non_na_counts'] > 0]
  
  long_df_PR = pd.wide_to_long(filtered_df, ["I10_PR"], i="KEY_NIS", j="ProcNum").reset_index()
  working_long_df_PR=long_df_PR[long_df_PR['I10_PR'].notna()]
  long_df_PR_DX = pd.wide_to_long(working_long_df_PR, ["I10_DX"], i=["KEY_NIS","ProcNum"], j="DiagNum").reset_index()
  working_long_df_PR_DX=long_df_PR_DX[long_df_PR_DX['I10_DX'].notna()]
  
  
  
  working1 = pd.merge(working_long_df_PR_DX, CodeSet_PR, on='I10_PR', how='left')
  working2 = pd.merge(working1, CodeSet_DX, on='I10_DX', how='left')
  working2['MYCATEGORY1']=Study_Name
  #working2['DISCWT']=np.round(working2['DISCWT']).values
  
  
  ### Merging Dataset ###
  summary_table = working2.groupby(['I10_PR','I10_DX']).agg(
  unique_KEY_NIS=('KEY_NIS', 'nunique'),  # Count unique KEY_NIS
  #unique_DISCWT=('DISCWT', 'nunique'),  # Count unique DISCWT
  Weighted_Discharge_No=('DISCWT', lambda x: np.round(x.sum())) # Sum of DISCWT
  ).reset_index()
  #summary_table.columns = ['ICD-10CODE', 'Unique_KEY_NIS_Count','unique_DISCWT','Weighted Count of Discharges']
  
  for i in range(len(summary_table)):
    summary_table.at[i, 'DESCRIPTION_10DX'] = ICD10CM.lookup(summary_table['I10_DX'].values[i])
    summary_table.at[i, 'DESCRIPTION_10PR'] = ICD10PROC.lookup(summary_table['I10_PR'].values[i])
    summary_table.at[i, 'CATEGORY1'] = Study_Name
  
  merged_df_PR_DX = copy.deepcopy(summary_table)
  ### Merging Dataset ###
  #### Calculating Pairs ######################################
  
  
  #### Calculating Overal Counts ##############################
  ### Category Frequency ###
  category_columns = [col for col in working2.columns if col.startswith('MYCATEGORY')]
  my_dict = {}
  for cccc in category_columns:
    TEMP=working2[["KEY_NIS",'DISCWT', cccc]]
    TEMP=TEMP.drop_duplicates()
    cc_table = TEMP.groupby(cccc).agg(
    unique_KEY_NIS=('KEY_NIS', 'nunique'),  # Count unique KEY_NIS
    #unique_DISCWT=('DISCWT', 'nunique'),  # Count unique DISCWT
    Weighted_Discharge_No=('DISCWT', lambda x: np.round(x.sum())) # Sum of DISCWT
    ).reset_index()
    my_dict[cccc]=copy.deepcopy(cc_table)
  ### Category Frequency ###
  #### Calculating Overal Counts ##############################
  
  
  
  ### Summary Statistics ###
  TEMP=working2[Study_VV]
  TEMP=TEMP.drop_duplicates()
  columns_to_compute =  [item for item in Study_VV if item not in ["KEY_NIS", "DISCWT"]]
  # Calculate weighted means
  weighted_means = {}
  for col in columns_to_compute:
      valid_data = TEMP[[col, 'DISCWT']].dropna()
      weighted_mean = np.average(valid_data[col], weights=valid_data['DISCWT'])
      weighted_means[col] = weighted_mean
  
  # Create a dataframe with variable names and their weighted means
  weighted_mean_df = pd.DataFrame({
      'Variable': columns_to_compute,
      'Weighted_Mean': [weighted_means[col] for col in columns_to_compute]
  })
  ### Summary Statistics ###
  
  
  
  ### Writing File out ###
  with pd.ExcelWriter(Output_Path+Official+str(Year)+'.xlsx') as writer:
    weighted_mean_df.to_excel(writer, sheet_name='Summary_Statistics'+vv, index=False)
    for cccc in category_columns:
      my_dict[cccc].to_excel(writer, sheet_name='Weighted Count of'+cccc, index=False)
    merged_df_PR_DX.to_excel(writer, sheet_name='Weighted Count of'+vv, index=False)
  ### Category Frequency ###
