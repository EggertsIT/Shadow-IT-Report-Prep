import pandas as pd

# Import CSV with the ID and the Name of the Application from the "light" App export
df_App_IDs = pd.read_csv('app_id.csv',index_col=False,dtype={'id': 'str'})
#Convert the name to lower to adjust for GitHub vs Github Application naming
df_App_IDs['name'] = df_App_IDs['name'].str.lower()

#Import CSV from Applications export (shadowIT Report)
df_Applications_in_use = pd.read_csv('shadow_it_report.csv',index_col=False)
#Convert the name to lower to adjust for GitHub vs Github Application naming
df_Applications_in_use['Application'] = df_Applications_in_use['Application'].str.lower()

#Merge the Dataframes to mach name with the ID
df_Applications_in_use_with_ID = pd.merge(df_Applications_in_use, df_App_IDs, left_on='Application', right_on='name', how='left')

# Filter out applications where the ID is missing and save to CSV
df_Applications_in_use_with_ID[df_Applications_in_use_with_ID['id'].isna()].to_csv('./Output/Apps_with_missmatch.csv', columns=['Application'], index=False)

# Filter out applications where the ID is present and save to CSV
df_Applications_in_use_with_ID[df_Applications_in_use_with_ID['id'].notna()].to_csv('./Output/Apps_with_ID.csv', index=False)

