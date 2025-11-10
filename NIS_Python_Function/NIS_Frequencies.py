def NIS_Frequencies(df,CodeSet,vv,Study_VV):
  from pyhealth.medcode import InnerMap
  # Initialize an empty list to store processed chunks
  chunks = []
  chunk_size = 1000
  
  # Use tqdm to create a progress bar
  for start in tqdm(range(0, len(df), chunk_size), desc="Processing chunks"):
      # Select the chunk of the DataFrame
      df_chunk = df.iloc[start:start+chunk_size]
      
      # Reshape the chunk to long format
      long_df_chunk = pd.wide_to_long(df_chunk, [vv], i="KEY_NIS", j="ProcNum").reset_index()
      
      # Filter out rows where the value in the 'vv' column is NaN
      working_chunk = long_df_chunk[long_df_chunk[vv].notna()]
      
      # Append the filtered chunk to the list
      chunks.append(working_chunk)
  
  # Concatenate all the processed chunks into a single DataFrame
  working = pd.concat(chunks)
  working2 = pd.merge(working, CodeSet, on=vv, how='left')
  
  #working2['DISCWT']=np.round(working2['DISCWT']).values
  
  
  
  
  
  ### Merging Dataset ###
  summary_table = working2.groupby(vv).agg(
  unique_KEY_NIS=('KEY_NIS', 'nunique'),  # Count unique KEY_NIS
  #unique_DISCWT=('DISCWT', 'nunique'),  # Count unique DISCWT
  Weighted_Discharge_No=('DISCWT', lambda x: np.round(x.sum())) # Sum of DISCWT
  ).reset_index()
  #summary_table.columns = ['ICD-10CODE', 'Unique_KEY_NIS_Count','unique_DISCWT','Weighted Count of Discharges']
  #merged_df = pd.merge(summary_table, CodeSet, on=vv, how='left')
  ICD10CM = InnerMap.load("ICD10CM")
  ICD10PROC = InnerMap.load("ICD10PROC")
  for i in range(len(summary_table)):
    if vv=="I10_DX":
      summary_table.at[i, 'DESCRIPTION'] = ICD10CM.lookup(summary_table['I10_DX'].values[i])
    elif vv=="I10_PR":
      summary_table.at[i, 'DESCRIPTION'] = ICD10PROC.lookup(summary_table['I10_PR'].values[i])
    summary_table.at[i, 'CATEGORY1'] = Study_Name
  merged_df = copy.deepcopy(summary_table)
  ### Merging Dataset ###
  
  ### ICD Frequency ###
  TEMP=working2[["KEY_NIS",'DISCWT', vv]]
  TEMP=TEMP.drop_duplicates()
  summary_table = TEMP.groupby(vv).agg(
  unique_KEY_NIS=('KEY_NIS', 'nunique'),  # Count unique KEY_NIS
  #unique_DISCWT=('DISCWT', 'nunique'),  # Count unique DISCWT
  Weighted_Discharge_No=('DISCWT', lambda x: np.ceil(x.sum())) # Sum of DISCWT
  ).reset_index()
  ### ICD Frequency ###
  
  
  ### Category Frequency ###
  category_columns = [col for col in working2.columns if col.startswith('CATEGORY')]
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
  
  
  ### Writing File out ###
  with pd.ExcelWriter(Output_Path+Official+str(Year)+'.xlsx') as writer:
    weighted_mean_df.to_excel(writer, sheet_name='Summary_Statistics'+vv, index=False)
    for cccc in category_columns:
      my_dict[cccc].to_excel(writer, sheet_name='Weighted Count of'+cccc, index=False)
    merged_df.to_excel(writer, sheet_name='Weighted Count of'+vv, index=False)
  ### Category Frequency ###
