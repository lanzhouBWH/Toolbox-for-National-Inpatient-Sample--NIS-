def NIS_Data_Reader(Type,Year,Vars,Data_Path):
  num_processes = multiprocessing.cpu_count()
  File_Name=Data_Path+"nis_"+str(Year)+"_"+Type+".sas7bdat"
  metadf= (pyreadstat.read_sas7bdat(File_Name, metadataonly=True))
  column_names = metadf[0].columns
  matching_columns = [col for col in column_names if any(var in col for var in Vars)]
  #df= pyreadstat.read_file_multiprocessing(pyreadstat.read_sas7bdat, File_Name,num_processes=num_processes,usecols=matching_columns)
  df= pyreadstat.read_sas7bdat( File_Name,usecols=matching_columns)
  return(df[0])
