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
  
  df_cleaned = df2.dropna(subset=matching_columns, how='all')
  
  return(df_cleaned)
