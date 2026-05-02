#!/usr/bin/env python
# coding: utf-8

# # HFM Data to ACE Transformation

# ## Jupyter Notebook Prerequesites

# In[13]:





# ## Python Script Prerequesites

# In[14]:
import pytz
from datetime import datetime, timedelta

from HFM_Initialization import *


def add_zero(x):
     
   
    return  "0"*(8-len(x)) + x

# ## Execution

# ### User Parameters
SG_Time = datetime.now(pytz.timezone('Asia/Singapore')).date()




CurrentWeekNum  = SG_Time.isocalendar()[1]
# In[15]:
    
    






df_updatedate = read_from_adl_DataFrame(adl,
                                        pbi_data_path + 'UPDATEDATE.csv',
                                        dtype_dict=object)

today_date = pd.to_datetime(
    df_updatedate['UPDATEDATE'][0],
    format='%Y-%m-%d').replace(tzinfo=timezone('Asia/Singapore'))

week_start = today_date - pd.to_timedelta(today_date.weekday(), unit='D')
startdate_parameter = week_start



today_date_hour = pd.to_datetime(
    datetime.now()).replace(tzinfo=timezone('Asia/Singapore')) + pd.to_timedelta(8, unit='h')

print("today_date_hour: " + str(today_date_hour))

today_date_hour = today_date_hour.strftime("%H")

today_date_hour = int(today_date_hour)

print("Current Hour : ",today_date_hour)

# if today_date_hour == 12 or today_date_hour == 9 or today_date_hour == 15   :
#     df_shipment_updated_sharepoint = read_from_adl_DataFrame(
#     adl, shipment_updated_sharepoint_filepath, dtype_dict=object)
#     upload_to_adl_DataFrame(adl, df_shipment_updated_sharepoint, shipment_updated_filepath)   
#     print("HFM Shipment Updated in 03_Updated updated")

# else:
#     pass
#     print("Is time for Cw1 refresh")
    
 

# In[16]:


print(today_date)


# In[17]:


print(week_start)


# ### Data Ingestion & Transformation

# #### Master

# In[18]:


# with adl.open(SIMs_filepath) as f:
#     df_SIMs = pd.read_csv(f, dtype=object)
    
df_SIMs = read_from_adl_DataFrame(adl,SIMs_filepath, dtype_dict=object)    

df_SIMs = df_SIMs[[
    'WRIN', 'PRODUCT_DESCRIPTION', 'PRODUCT_CATEGORY', 'PRODUCT_SUB-CATEGORY1',
    'PRODUCT_SUB-CATEGORY2', 'PRODUCT_SUB-CATEGORY3', 'ASSEMBLY_ITEM'
]]


# ##### Market in Scope for Manual

# In[19]:


# with adl.open(market_scope_filepath) as f:
#     df_marketscope = pd.read_csv(f)
    
df_marketscope = read_from_adl_DataFrame(adl,market_scope_filepath, dtype_dict=object)    
    

countries_in_scope_cw1 = df_marketscope[df_marketscope['IN_SCOPE'] ==
                                    0]['COUNTRY_NAME'].unique().tolist()

countries_in_scope_spo = df_marketscope[df_marketscope['IN_SCOPE'] !=
                                    0]['COUNTRY_NAME'].unique().tolist()+['HONG KONG']


# In[20]:


df_country_code = read_from_adl_DataFrame(adl, country_code_filepath)

df_country_code['COUNTRY_NAME'] = [
    str(i).upper() for i in df_country_code['COUNTRY_NAME']
]

countrycode_columns = df_country_code.columns.tolist()


# ##### Adjustment on ETA for Market to DC

# In[21]:


market_dc_filepath = master_data_path + 'Market_DC_ETA_Add.csv'

# with adl.open(market_dc_filepath) as f:
#     df_dc_eta_addition = pd.read_csv(f)
    
df_dc_eta_addition =  read_from_adl_DataFrame(adl, market_dc_filepath)    

df_dc_eta_addition = df_dc_eta_addition.fillna(0)


# In[22]:


df_dc_eta_addition


# ##### SIMS Manual

# In[23]:


df_SIMs_Manual = read_from_adl_DataFrame(adl,
                                         SIMs_manual_filepath,
                                         dtype_dict=object)
# df_SIMs_Manual['WRIN'] = [i.zfill(8) for i in df_SIMs_Manual['WRIN']]
# for i in df_SIMs_Manual.columns.tolist():
#     df_SIMs_Manual[i] = [i.upper() for i in df_SIMs_Manual[i]]

# df_SIMs_Manual['MATCH_MESSAGE'] = 'FOUND IN Manual SIMs'


# In[24]:


df_SIMs_Manual


# #### Shipment

# In[25]:


shipment_updated_filepath


# ##### PowerApps Feed Input

# In[26]:
df_shipment_updated = read_from_adl_DataFrame(adl,shipment_updated_filepath) 


#---------------Data Ingestion---------------
# with adl.open(shipment_updated_filepath) as f:
#     df_shipment_updated = pd.read_csv(f)






# df_shipment_updated = df_shipment_updated.append(df_shipment_raw_Addtional_Info)



   

#---------------Data Transformation---------------
df_shipment_updated = df_shipment_updated.rename(columns={'TITLE': 'INDEX'})
df_shipment_updated['SELCTED_ETA'] = None

#---------------Time Transformation---------------
df_shipment_updated = convert_column_to_datetime_Dataframe(
    df_shipment_updated,
    ['ETD_POL_OVERRIDE', 'ETA_POD_OVERRIDE', 'ATD_OVERRIDE', 'ATA_OVERRIDE'],
    '%Y-%m-%d')

df_shipment_updated = convert_column_to_datetime_Dataframe(
    df_shipment_updated, [
        'REQUIRED_IN_STORE','ETD_POL', 'ETD_POL_OVERRIDE', 'ETA_POD', 'ETA_POD_OVERRIDE', 'ATD',
        'ATD_OVERRIDE', 'ATA', 'ATA_OVERRIDE', 'SELCTED_ETA'
    ])

df_shipment_updated = add_timezone_DataFrame(df_shipment_updated, [
    'ETD_POL', 'ETD_POL_OVERRIDE', 'ETA_POD', 'ETA_POD_OVERRIDE', 'ATD',
    'ATD_OVERRIDE', 'ATA', 'ATA_OVERRIDE', 'SELCTED_ETA'
], 'Asia/Singapore')

#---------------Selected Time Logic---------------
df_shipment_updated = override_column_DataFrame(
    df_shipment_updated, 'SELCTED_ETA',
    ['ATA_OVERRIDE', 'ATA', 'ETA_POD_OVERRIDE', 'ETA_POD'])

df_shipment_updated = df_shipment_updated[
    df_shipment_updated['PLACEOFDELIVERY_COUNTRY'].isin(countries_in_scope_spo)]


# In[27]:


evaluate_duplicates_exisit(df_shipment_updated)












# ##### Manual Feed Input

# In[16]:


#---------------Data Ingestion---------------
# with adl.open(shipment_processed_manual_filepath) as f:
#     df_shipment_manual_processed = pd.read_csv(f, dtype=object)

# manual_date_columns = [
#     'ETD_POL_MANUAL', 'ETA_POD_MANUAL', 'ATD_MANUAL', 'ATA_MANUAL'
# ]
# for i in manual_date_columns:
#     df_shipment_manual_processed[i] = None

# #---------------Time Transformation---------------
# df_shipment_manual_processed = convert_column_to_datetime_Dataframe(
#     df_shipment_manual_processed, [
#         'REQUIRED_IN_STORE',
#         'ETD_POL',
#         'ETD_POL_OVERRIDE',
#         'ETA_POD',
#         'ETA_POD_OVERRIDE',
#         'ATD',
#         'ATD_OVERRIDE',
#         'ATA',
#         'ATA_OVERRIDE',
#     ] + manual_date_columns)

# df_shipment_manual_processed = add_timezone_DataFrame(
#     df_shipment_manual_processed, [
#         'ETD_POL',
#         'ETD_POL_OVERRIDE',
#         'ETA_POD',
#         'ETA_POD_OVERRIDE',
#         'ATD',
#         'ATD_OVERRIDE',
#         'ATA',
#         'ATA_OVERRIDE',
#     ] + manual_date_columns, 'Asia/Singapore')

# ##----- Take Overrides

# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_manual_processed, 'ETD_POL_MANUAL',
#     ['ETD_POL_OVERRIDE', 'ETD_POL'])
# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_manual_processed, 'ETA_POD_MANUAL',
#     ['ETA_POD_OVERRIDE', 'ETA_POD'])
# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_manual_processed, 'ATD_MANUAL', ['ATD_OVERRIDE', 'ATD'])
# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_manual_processed, 'ATA_MANUAL', ['ATA_OVERRIDE', 'ATA'])

# df_shipment_manual_processed = df_shipment_manual_processed[
#     ['SHIPMENT_ID', 'CONSOL_ID', 'CONTAINER_NO', 'PLACEOFDELIVERY_COUNTRY'] +
#     manual_date_columns].drop_duplicates().reset_index(drop=True)


# In[17]:


#evaluate_duplicates_exisit(df_shipment_manual_processed)


# In[18]:


#df_shipment_manual_processed.head()


# ##### Cargowise Feed Input

# In[45]:


#---------------Data Ingestion---------------
# with adl.open(shipment_processed_filepath) as f:
#     df_shipment_processed = pd.read_csv(f)
    
df_shipment_processed = read_from_adl_DataFrame_new(adl,shipment_processed_filepath,hearder_capitalized= False ,dtype_dict={"INTERNAL_PO" :"str"}  )      

#---------------Data Transformation---------------
df_shipment_processed['SELCTED_ETA'] = None

#---------------Time Transformation---------------
df_shipment_processed = convert_column_to_datetime_Dataframe(
    df_shipment_processed, [
        'REQUIRED_IN_STORE','ETD_POL', 'ETD_POL_OVERRIDE', 'ETA_POD', 'ETA_POD_OVERRIDE', 'ATD',
        'ATD_OVERRIDE', 'ATA', 'ATA_OVERRIDE', 'SELCTED_ETA'
    ])

#---------------Countries Slicing---------------
df_shipment_processed = df_shipment_processed[
    df_shipment_processed['PLACEOFDELIVERY_COUNTRY'].isin(countries_in_scope_spo)].reset_index(
        drop=True)


# In[46]:


evaluate_duplicates_exisit(df_shipment_processed)


# In[47]:


df_shipment_processed['PLACEOFDELIVERY_COUNTRY']


# ##### Combination of Shipment Files

# In[49]:


#---------------Merging Cargowise + Manual Inputs--------------
# df_shipment_processed = df_shipment_processed.merge(
#     df_shipment_manual_processed,
#     on=['SHIPMENT_ID', 'CONSOL_ID', 'CONTAINER_NO', 'PLACEOFDELIVERY_COUNTRY'],
#     how='left')

# #---------------Selected Time Logic---------------
# df_shipment_processed = override_column_DataFrame(
#     df_shipment_processed, 'SELCTED_ETA', [
#         'ATA_MANUAL', 'ETD_POL_MANUAL', 'ATA_OVERRIDE', 'ATA',
#         'ETA_POD_OVERRIDE', 'ETA_POD'
#     ])

# #---------------Manual replaces the CW1 Processed Overrides ---------------
# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_processed, 'ETD_POL_OVERRIDE', ['ETD_POL_MANUAL'])
# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_processed, 'ETA_POD_OVERRIDE', ['ETA_POD_MANUAL'])
# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_processed, 'ATD_OVERRIDE', ['ATD_MANUAL'])
# df_shipment_manual_processed = override_column_DataFrame(
#     df_shipment_processed, 'ATA_OVERRIDE', ['ATA_MANUAL'])

# #---------------Drop Unnecessary Columns---------------
# df_shipment_processed = df_shipment_processed.drop(
#     columns=['ETD_POL_MANUAL', 'ETA_POD_MANUAL', 'ATD_MANUAL', 'ATA_MANUAL'])

#---------------Merging Cargowise + Power Apps Inputs--------------
#df_shipment_eta = df_shipment_updated.append(
#    df_shipment_processed).reset_index(drop=True)

#Save the Process file Column Name List for ordering the column after the process file left join updated file
ListOfColumns = list(df_shipment_processed.columns)

#drop the column in process file that need the value from updated file and it will create prefix when doing left join with upadated file
df_shipment_processed = df_shipment_processed.drop(['ETD_POL_OVERRIDE','ETA_POD_OVERRIDE','ATD_OVERRIDE','ATA_OVERRIDE','COMMENT',
                                                    'COMMENT_MODIFIED','COMMENT_MODIFIED_BY','INTERNAL_COMMENT','INTERNAL_COMMENT_MODIFIED','INTERNAL_COMMENT_MODIFIED_BY'], axis = 1) 

#Merge process file and updated file
df_shipment_merge = pd.merge(df_shipment_processed, df_shipment_updated,  how='left', left_on=['SHIPMENT_ID','CONTAINER_NO','CONSOL_ID','CUSTOMER_PO'], right_on = ['SHIPMENT_ID','CONTAINER_NO','CONSOL_ID','CUSTOMER_PO'],indicator=True)

#drop the column with prefix '_y' which is from updated file
df_shipment_merge = df_shipment_merge[df_shipment_merge.columns.drop(list(df_shipment_merge.filter(regex='_y')))]


 
#remove the column with prefix '_x' which is the column from process file
df_shipment_merge.columns = df_shipment_merge.columns.str.rstrip('_x')


#remove the column ['ID','_merge'] and frop the duplicateds because of the duplicated record from the updated file which enlarge the rows after merge
df_shipment_merge = df_shipment_merge.drop(['ID','_merge'], axis = 1).drop_duplicates()

#use the orignal columns name list from process file to order the after-merged file and also check if the column is missing or not 
df_shipment_merge = df_shipment_merge[ListOfColumns]

#use the orignal columns name list from process file to order the after-merged file and also check if the column is missing or not 
evaluate_duplicates_exisit(df_shipment_merge)


#df_shipment_processed.to_csv(r'C:\Users\danny.huang\Downloads\df_process2.csv') 
#df_shipment_updated.to_csv(r'C:\Users\danny.huang\Downloads\df_updated2.csv') 

# rename df_shipment_merge to df_shipment_eta  for futher use 
df_shipment_eta = df_shipment_merge
df_shipment_eta

df_shipment_raw_Addtional_Info = read_from_adl_DataFrame_new(adl, shipment_processed_path + 'df_shipment_raw_Addtional_Info.csv')  


df_shipment_raw_Addtional_Info_col =  df_shipment_raw_Addtional_Info.columns
df_shipment_eta_Col = df_shipment_updated.columns

col_missing = []
for i in df_shipment_eta_Col:
    if i in df_shipment_raw_Addtional_Info_col :
         pass
    else : 
        col_missing.append(i)
        
for i in  col_missing:
      df_shipment_raw_Addtional_Info[i] = np.nan 


df_shipment_raw_Addtional_Info['CUSTOMER_PO'] =  df_shipment_raw_Addtional_Info['CUSTOMER_PO'].astype(str)          
      
df_shipment_raw_Addtional_Info['INTERNAL_PO'] = df_shipment_raw_Addtional_Info['CUSTOMER_PO']      



df_shipment_raw_Addtional_Info['CUSTOMER_PO'] = df_shipment_raw_Addtional_Info.apply(
    lambda x: x['CUSTOMER_PO'][:3]+ '   '+ x['CUSTOMER_PO'][-7:]
    if x['PLACEOFDELIVERY_COUNTRY'] == 'TAIWAN' else x['CUSTOMER_PO'], axis =1 )


df_shipment_raw_Addtional_Info = df_shipment_raw_Addtional_Info[df_shipment_eta_Col]

df_shipment_raw_Addtional_Info["POL_COUNTRY"] = 'TAIWAN'


df_shipment_raw_Addtional_Info = df_shipment_raw_Addtional_Info.replace("?",np.nan)


df_shipment_eta.columns


List_of_HFM_PO =  df_shipment_eta['CUSTOMER_PO'].tolist()


df_shipment_raw_Addtional_Info = df_shipment_raw_Addtional_Info[~(df_shipment_raw_Addtional_Info['CUSTOMER_PO'].isin(List_of_HFM_PO))]









# df_shipment_eta = df_shipment_eta.append(df_shipment_raw_Addtional_Info)















df_shipment_eta['SHIPPER_NAME'] = [
    str(i).replace(', ', ' ').replace(',', '')
    for i in df_shipment_eta['SHIPPER_NAME']
]


# In[50]:


df_shipment_eta.columns


# In[51]:


df_shipment_eta['PLACEOFDELIVERY_COUNTRY'].unique()


# In[52]:


evaluate_duplicates_exisit(df_shipment_eta)


# ##### Add in DCA Logic

# In[53]:

'ETD_POL', 'ETD_POL_OVERRIDE'
df_shipment_eta['DC_ETA_ADJUST'] = None



############Delayed ETA#############################

Col_df_shipment_eta = df_shipment_eta.columns  
# with adl.open('HAVI/HAVI_Freight_Management/00_Master_Data/Country_Continent.csv') as f:
#       df_Country_Continent = pd.read_csv(f)
      
df_Country_Continent =  read_from_adl_DataFrame_new(adl,'HAVI/HAVI_Freight_Management/00_Master_Data/Country_Continent.csv',hearder_capitalized= False )      
df_Country_Continent['CountryName'] = df_Country_Continent['CountryName'].str.upper()

# In[54]:
# df_shipment_eta  =  df_shipment_eta.merge(df_Country_Continent, how='left', left_on  = "POL_COUNTRY" , right_on = "CountryName")

# df_shipment_eta.replace(np.nan,'',inplace = True) 



# df_shipment_eta['Len_ETA_POD_OVERRIDE'] = df_shipment_eta['ETA_POD_OVERRIDE'].astype(str).str.len()
# df_shipment_eta['Len_ETA_POD'] = df_shipment_eta['ETA_POD'].astype(str).str.len()


# #Get the count of the string lenght for ETD_POL_OVERRIDE and ETD_POL Columns
# df_shipment_eta['Len_ETD_POL_OVERRIDE'] = df_shipment_eta['ETD_POL_OVERRIDE'].astype(str).str.len()
# df_shipment_eta['Len_ETD_POL'] = df_shipment_eta['ETD_POL'].astype(str).str.len()


# #Logic in If else statment to pick which date will be selected for Applied_ETA Column
# def get_Right_ETA(df) :
#     if df['Len_ETA_POD_OVERRIDE'] > 1 :
#         return df['ETA_POD_OVERRIDE']
#     elif df['Len_ETA_POD'] > 1 :
#         return df['ETA_POD']
    
# #Logic in If else statment to pick which date will be selected for Applied_ETA Column
# def get_Right_ETD(df) :
#     if df['Len_ETD_POL_OVERRIDE'] > 1 :
#         return df['ETD_POL_OVERRIDE']
#     elif df['Len_ETD_POL'] > 1 :
#         return df['ETD_POL']


# #Logic in If else statment to pick which date will be selected for Applied_ETA Column
# def get_Right_ATA(df) :
#     if df['Len_ATA_OVERRIDE'] > 1 :
#         return df['ATA_OVERRIDE']
#     elif df['Len_ATA'] > 1 :
#         return df['ATA']


# #Logic in If else statment to pick which date will be selected for Applied_ETA Column
# def get_Right_ATD(df) :
#     if df['Len_ATD_OVERRIDE'] > 1 :
#         return df['ATD_OVERRIDE']
#     elif df['Len_ATD'] > 1 :
#         return df['ATD']

# #create Latest ETD Column
# df_shipment_eta['Latest ETD POL'] = df_shipment_eta.apply(get_Right_ETD, axis = 1)


# # df_shipment_eta['Latest ETD POL'] = np.where(
# #     df_shipment_eta['ETD_POL_OVERRIDE'].isna(),
# #      df_shipment_eta['ETD_POL_OVERRIDE'],
# #     df_shipment_eta['ETD_POL'] )


# # df_shipment_eta['Latest ETA POD'] =  df_shipment_eta['ETA_POD_OVERRIDE']
    
    
# df_shipment_eta['Latest ETA POD'] = df_shipment_eta.apply(get_Right_ETA, axis = 1)
# #Add Is_Override_ETA to check if Latest ETA from Override ETA
# # df_shipment_sharepoint['Is_Override_ETA'] = df_s.isna()
# # np.where(
# #     df_shipment_eta['ETA_POD_OVERRIDE'].isna(),
# #      df_shipment_eta['ETA_POD_OVERRIDE'],
# #     df_shipment_eta['ETA_POD'])

# # df_shipment_sharepoint_POL.columns

# # df_shipment_sharepoint_POL['Continent'] 

# df_shipment_eta = df_shipment_eta.rename(columns = {'Continent':'POL_Continent'})

# df_shipment_eta = df_shipment_eta.drop(columns=["CountryName"])

# df_shipment_eta =  df_shipment_eta.merge(df_Country_Continent, how='left', left_on  = "PLACEOFDELIVERY_COUNTRY" , right_on = "CountryName")

# df_shipment_eta = df_shipment_eta.rename(columns = {'Continent':'POD_Continent'})

# df_shipment_eta = df_shipment_eta.drop(columns=["CountryName"])


# df_shipment_sharepoint_Region = df_shipment_eta


# df_shipment_sharepoint_Region['IsIntraAsia'] =  (df_shipment_sharepoint_Region['POL_Continent'] == "Asia")  &  (df_shipment_sharepoint_Region['POD_Continent'] == "Asia")

# df_shipment_sharepoint_Region['IsPOL_Oceania'] = df_shipment_sharepoint_Region['POL_Continent'] == "Oceania"

# df_shipment_sharepoint_Region['Latest ETD POL'] = pd.to_datetime(df_shipment_sharepoint_Region['Latest ETD POL'],utc=True).dt.tz_convert(tz='Asia/Singapore')

# df_shipment_sharepoint_Region['ETD_WeekNum'] = df_shipment_sharepoint_Region['Latest ETD POL'].dt.week

# df_shipment_sharepoint_Region['WeekNum_Diff'] =  df_shipment_sharepoint_Region['ETD_WeekNum']  - CurrentWeekNum



# # df_shipment_sharepoint_Region = df_shipment_sharepoint_Region[df_shipment_sharepoint_Region['WeekNum_Diff'].isnull() == False ]
# # df_shipment_sharepoint_Region['WeekNum_Diff'] = df_shipment_sharepoint_Region[['WeekNum_Diff']].astype(float)

# # df_shipment_sharepoint_Region_No_week_Diff = df_shipment_sharepoint_Region[df_shipment_sharepoint_Region['WeekNum_Diff'].isnull()]


# df_shipment_sharepoint_Region = df_shipment_sharepoint_Region.fillna('')
# df_shipment_sharepoint_Region['Latest ETA POD'] = pd.to_datetime(df_shipment_sharepoint_Region['Latest ETA POD'],utc=True).dt.tz_convert(tz='Asia/Singapore')



# #build condition
# for index, row in df_shipment_sharepoint_Region.iterrows():
#     if row['PLACEOFDELIVERY_COUNTRY'] == 'MALAYSIA':
#       if len(row['CONTAINER_NO']) > 0 :
#           df_shipment_sharepoint_Region.at[index, 'Delay_Condition'] = "1" 
#       elif len(row['CONTAINER_NO']) == 0 and  len(row['CARRIER_BKG._REF']) > 0 : 
#           df_shipment_sharepoint_Region.at[index, 'Delay_Condition'] = "2" 
#       elif len(row['CONTAINER_NO']) == 0 and  len(row['CARRIER_BKG._REF']) == 0 : 
#           df_shipment_sharepoint_Region.at[index, 'Delay_Condition'] = "3"     
          
# #Apply ETA Delayed      
# for index, row in df_shipment_sharepoint_Region.iterrows():
#    try  :   
#       if (row['WeekNum_Diff'] == 0) & (row['Delay_Condition'] == "1") :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=14)   
#       elif (row['WeekNum_Diff'] == 0) & (row['Delay_Condition'] == "2") :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=21)   
#       elif (row['WeekNum_Diff'] == 0) & (row['Delay_Condition'] == "3" ) :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=28)   
           
#       elif (row['WeekNum_Diff'] == 1) & (row['Delay_Condition'] == "1") :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=14)   
#       elif (row['WeekNum_Diff'] == 1) & (row['Delay_Condition'] == "2") :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=21)   
#       elif (row['WeekNum_Diff'] == 1) & (row['Delay_Condition'] == "3") :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=28)  
           
           
#       # if (row['WeekNum_Diff'] == 2) & (row['Delay_Condition'] == "1") :   
#       #      df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=14)   
#       elif (row['WeekNum_Diff'] == 2) & (row['Delay_Condition'] == "2") :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=21)   
#       elif (row['WeekNum_Diff'] == 2) & (row['Delay_Condition'] == "3") :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=28)  
      
#       elif (row['WeekNum_Diff']  > 2) & (row['WeekNum_Diff']  <  9) :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=28)     
#       else: 
#           df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  
           
#    except:
#       print(row['SHIPMENT_ID'] + "  No Week Diff")
#       df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =  row['Latest ETA POD']        
      
           
# #Apply Region Delay  
# for index, row in df_shipment_sharepoint_Region.iterrows():  
#    if row['PLACEOFDELIVERY_COUNTRY'] == 'MALAYSIA': 
#       if row['IsIntraAsia'] == True :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=14)       
#       if row['IsPOL_Oceania'] == True :   
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=21)            

# ###NewAdjusted ETA 2023/04/14



# for index, row in df_shipment_sharepoint_Region.iterrows():
#     if row['PLACEOFDELIVERY_COUNTRY'] == 'MALAYSIA':    
#       if row['Latest ETA POD']  > SG_Time :
#           df_shipment_sharepoint_Region.at[index, 'Delay_Condition'] = "1" 
          
#       elif len(row['CONTAINER_NO']) > 0 :
#           df_shipment_sharepoint_Region.at[index, 'Delay_Condition'] = "2" 
#       elif len(row['CONTAINER_NO']) == 0 and  len(row['CARRIER_BKG._REF']) > 0 : 
#           df_shipment_sharepoint_Region.at[index, 'Delay_Condition'] = "3" 
#       elif len(row['CONTAINER_NO']) == 0 and  len(row['CARRIER_BKG._REF']) == 0 : 
#           df_shipment_sharepoint_Region.at[index, 'Delay_Condition'] = "4"     


# for index, row in df_shipment_sharepoint_Region.iterrows():
    
#       if row['IsIntraAsia']  == True :
#           df_shipment_sharepoint_Region.at[index, 'POL_Continent'] = "IntraAsia" 
          
# # with adl.open(Adjusted_ETA_Days_Setting_filepath) as f:
# #       df_Adjusted_ETA_Days_Setting = pd.read_csv(f)    


# df_Adjusted_ETA_Days_Setting = read_from_adl_DataFrame_new(adl,Adjusted_ETA_Days_Setting_filepath,hearder_capitalized= False )      
      
# df_Adjusted_ETA_Days_Setting.columns      
        
# Shipment_Condition_Dic = {"Shipment has departed" : "1",
#                           "Have container,Not departed" : "2",
#                           "Have booking, NO container" : "3",
#                           "NO booking, NO Container" : "4",}      

# df_Adjusted_ETA_Days_Setting["Delay_Condition"] = df_Adjusted_ETA_Days_Setting['Shipment_Condition'].replace(Shipment_Condition_Dic)

# df_Adjusted_ETA_Days_Setting.columns




# df_shipment_sharepoint_Region =  df_shipment_sharepoint_Region.merge( df_Adjusted_ETA_Days_Setting, how = "left", on = ['Delay_Condition','POD_COUNTRY','POL_Continent'])



# df_shipment_sharepoint_Region['Delay_Days'] = df_shipment_sharepoint_Region['Delay_Days'].fillna(0)


# for index, row in df_shipment_sharepoint_Region.iterrows():
#            df_shipment_sharepoint_Region.at[index, 'ETA_POD_OVERRIDE'] =   row['Latest ETA POD']  +  timedelta(days=row['Delay_Days'])
            


# df_shipment_sharepoint_Region.to_csv(r'C:\Users\danny.huang\Downloads\regiontest.csv')
# df_shipment_eta.to_csv(r'C:\Users\danny.huang\Downloads\region.csv')
df_shipment_eta 


df_shipment_eta.replace('',np.nan,inplace = True)

###########################################################################################################
df_shipment_eta = df_shipment_eta.merge(df_country_code,
                                        left_on='PLACEOFDELIVERY_COUNTRY',
                                        right_on='COUNTRY_NAME')


#--------------ETA POD +1 Day , Required in Store +1 Day Logic--------------

market_inscope_1 = ['HKG', 'SGP']
makert_inscope_dayadd_1 = 1

###-------------ETA Adjust with ETA POD--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_1)) &
    (~df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD'] + pd.Timedelta(days=makert_inscope_dayadd_1),
    df_shipment_eta['DC_ETA_ADJUST'])
###-------------ETA Adjust with ETA POD OVERRIDE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_1)) &
    (~df_shipment_eta['ETA_POD'].isna()) &
    (~df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD_OVERRIDE'] +
    pd.Timedelta(days=makert_inscope_dayadd_1),
    df_shipment_eta['DC_ETA_ADJUST'])

###------------ETA Adjust with ETA REQUIRED IN STORE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_1)) &
    (df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['REQUIRED_IN_STORE'] +
    pd.Timedelta(days=makert_inscope_dayadd_1),
    df_shipment_eta['DC_ETA_ADJUST'])

#--------------ETA POD +2 Day , Required in Store +2 Day Logic--------------

market_inscope_2 = ['KOR']
makert_inscope_dayadd_2 = 2

###-------------ETA Adjust with ETA POD--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_2)) &
    (~df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD'] + pd.Timedelta(days=makert_inscope_dayadd_2),
    df_shipment_eta['DC_ETA_ADJUST'])

###-------------ETA Adjust with ETA POD OVERRIDE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_2)) &
    (~df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD_OVERRIDE'] +
    pd.Timedelta(days=makert_inscope_dayadd_2),
    df_shipment_eta['DC_ETA_ADJUST'])

###------------ETA Adjust with ETA REQUIRED IN STORE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_2)) &
    (df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['REQUIRED_IN_STORE'] +
    pd.Timedelta(days=makert_inscope_dayadd_2),
    df_shipment_eta['DC_ETA_ADJUST'])

#--------------ETA POD +3 Day , Required in Store +3 Day Logic--------------

market_inscope_3 = ['PHL', 'MYS', 'IDN']
makert_inscope_dayadd_3 = 3

###-------------ETA Adjust with ETA POD--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_3)) &
    (~df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD'] + pd.Timedelta(days=makert_inscope_dayadd_3),
    df_shipment_eta['DC_ETA_ADJUST'])

###-------------ETA Adjust with ETA POD OVERRIDE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_3)) &
    (~df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD_OVERRIDE'] +
    pd.Timedelta(days=makert_inscope_dayadd_3),
    df_shipment_eta['DC_ETA_ADJUST'])

###------------ETA Adjust with ETA REQUIRED IN STORE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_3)) &
    (df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['REQUIRED_IN_STORE'] +
    pd.Timedelta(days=makert_inscope_dayadd_3),
    df_shipment_eta['DC_ETA_ADJUST'])

#--------------ETA POD +7 Day , Required in Store +7 Day Logic--------------

market_inscope_4 = ['TWN']
makert_inscope_dayadd_4 = 7

###-------------ETA Adjust with ETA POD--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
    (~df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD'] + pd.Timedelta(days=makert_inscope_dayadd_4),
    df_shipment_eta['DC_ETA_ADJUST'])

###-------------ETA Adjust with ETA POD OVERRIDE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
    (~df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD_OVERRIDE'] +
    pd.Timedelta(days=makert_inscope_dayadd_4),
    df_shipment_eta['DC_ETA_ADJUST'])

###------------ETA Adjust with ETA REQUIRED IN STORE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
    (df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['REQUIRED_IN_STORE'] +
    pd.Timedelta(days=makert_inscope_dayadd_4),
    df_shipment_eta['DC_ETA_ADJUST'])


#--------------ETA Adjustment for Taiwan Day Logic--------------
# market_inscope_4 = ['TWN']
# list_longhaul_country_twn = [
#     'POLAND', 'UNITED STATES', 'NEW ZEALAND', 'UNITED KINGDOM', 'NETHERLANDS'
# ]

# ###------------ETA Adjust with ATA--------------
# df_shipment_eta['DC_ETA_ADJUST'] = np.where(
#     (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
#     (~df_shipment_eta['ATA'].isna()) & (df_shipment_eta['ATA_OVERRIDE'].isna())
#     & (df_shipment_eta['DC_ETA_ADJUST'].isna()),
#     df_shipment_eta['ATA'] + pd.Timedelta(days=7),
#     df_shipment_eta['DC_ETA_ADJUST'])

# ###------------ETA Adjust with ATA OVERRIDE--------------
# df_shipment_eta['DC_ETA_ADJUST'] = np.where(
#     (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
#     (~df_shipment_eta['ATA_OVERRIDE'].isna())
#     & (df_shipment_eta['DC_ETA_ADJUST'].isna()),
#     df_shipment_eta['ATA_OVERRIDE'] + pd.Timedelta(days=7),
#     df_shipment_eta['DC_ETA_ADJUST'])

# ###------------ETA Adjust with ETA POD--------------
# df_shipment_eta['DC_ETA_ADJUST'] = np.where(
#     (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
#     (df_shipment_eta['ATA'].isna()) & (~df_shipment_eta['ATD'].isna()) &
#     (df_shipment_eta['ETA_POD_OVERRIDE'].isna()) &
#     (df_shipment_eta['DC_ETA_ADJUST'].isna()),
#     df_shipment_eta['ETA_POD'] + pd.Timedelta(days=7),
#     df_shipment_eta['DC_ETA_ADJUST'])

# ###------------ETA Adjust with ETA POD OVERRIDE--------------
# df_shipment_eta['DC_ETA_ADJUST'] = np.where(
#     (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
#     (df_shipment_eta['ATA'].isna()) & (~df_shipment_eta['ATD'].isna()) &
#     (~df_shipment_eta['ETA_POD_OVERRIDE'].isna()) &
#     (df_shipment_eta['DC_ETA_ADJUST'].isna()),
#     df_shipment_eta['ETA_POD_OVERRIDE'] + pd.Timedelta(days=7),
#     df_shipment_eta['DC_ETA_ADJUST'])

# ###-----------ETA Adjust for Long Haul and No Booking Reference--------
# df_shipment_eta['DC_ETA_ADJUST'] = np.where(
#     (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
#     (df_shipment_eta['ATA'].isna()) & (df_shipment_eta['ATD'].isna()) &
#     (df_shipment_eta['CARRIER_BKG._REF'].isna()) &
#     (df_shipment_eta['POL_COUNTRY'].isin(list_longhaul_country_twn)) &
#     (df_shipment_eta['DC_ETA_ADJUST'].isna()),
#     df_shipment_eta['ETA_POD'] + pd.Timedelta(days=21),
#     df_shipment_eta['DC_ETA_ADJUST'])

# ###-----------ETA Adjust for Long Haul with Booking Reference--------
# df_shipment_eta['DC_ETA_ADJUST'] = np.where(
#     (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
#     (df_shipment_eta['ATA'].isna()) & (df_shipment_eta['ATD'].isna()) &
#     (~df_shipment_eta['CARRIER_BKG._REF'].isna()) &
#     (df_shipment_eta['POL_COUNTRY'].isin(list_longhaul_country_twn)) &
#     (df_shipment_eta['DC_ETA_ADJUST'].isna()),
#     df_shipment_eta['ETA_POD'] + pd.Timedelta(days=14),
#     df_shipment_eta['DC_ETA_ADJUST'])

# ###-----------ETA Adjust for Short Haul ---------
# df_shipment_eta['DC_ETA_ADJUST'] = np.where(
#     (df_shipment_eta['ISO_3166-1_3CODE'].isin(market_inscope_4)) &
#     (df_shipment_eta['ATA'].isna()) & (df_shipment_eta['ATD'].isna()) &
#     (~df_shipment_eta['POL_COUNTRY'].isin(list_longhaul_country_twn)) &
#     (df_shipment_eta['DC_ETA_ADJUST'].isna()),
#     df_shipment_eta['ETA_POD'] + pd.Timedelta(days=14),
#     df_shipment_eta['DC_ETA_ADJUST'])

#--------------General: ETA POD +3 Day , Required in Store +3 Day Logic--------------

makert_inscope_dayadd_5 = 3

###-------------ETA Adjust with ETA POD--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['DC_ETA_ADJUST'].isna()) & 
    (~df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD'] + pd.Timedelta(days=makert_inscope_dayadd_5),
    df_shipment_eta['DC_ETA_ADJUST'])

###-------------ETA Adjust with ETA POD OVERRIDE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['DC_ETA_ADJUST'].isna()) & 
    (~df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['ETA_POD_OVERRIDE'] +
    pd.Timedelta(days=makert_inscope_dayadd_5),
    df_shipment_eta['DC_ETA_ADJUST'])

###------------ETA Adjust with ETA REQUIRED IN STORE--------------
df_shipment_eta['DC_ETA_ADJUST'] = np.where(
    (df_shipment_eta['DC_ETA_ADJUST'].isna()) & 
    (df_shipment_eta['ETA_POD'].isna()) &
    (df_shipment_eta['ETA_POD_OVERRIDE'].isna()),
    df_shipment_eta['REQUIRED_IN_STORE'] +
    pd.Timedelta(days=makert_inscope_dayadd_5),
    df_shipment_eta['DC_ETA_ADJUST'])


#Define file path to ADL csv file, load data into dataframe
df_hfm_offset_eta_datapath = 'HAVI/HAVI_Freight_Management/03_Updated_Data/Shipment/HFM_OFFSET_ETA_BY_CUSTOMER.csv'
# with adl.open(df_hfm_offset_eta_datapath) as g:
#      df_hfm_offset_eta = pd.read_csv(g)
     
df_hfm_offset_eta = read_from_adl_DataFrame_new(adl,df_hfm_offset_eta_datapath,hearder_capitalized= False )     
     
df_hfm_offset_eta = df_hfm_offset_eta[df_hfm_offset_eta['CUSTOMER'] == "MCD"]     
df_country_code     
df_hfm_offset_eta = df_hfm_offset_eta.merge(df_country_code, how='left', left_on='COUNTRY', right_on='COUNTRY_NAME'  )    

df_hfm_offset_eta['COUNTRY'] = df_hfm_offset_eta['ISO_3166-1_3CODE']

df_hfm_offset_eta = df_hfm_offset_eta[['COUNTRY','OFFSET_DAYS']]
# df_shipment_eta.rename(columns = {'ISO_3166-1_3CODE':'COUNTRY'},inplace = True)


###Import po for knowing the region 20230908
df_po_processed = read_from_adl_DataFrame(adl,
                                          po_processed_filepath,
                                          dtype_dict=object)



# with adl.open(DC_WSI_TO_REGION_file_path) as f:
#         df_DC_WSI_TO_REGION = pd.read_csv(f)
        
df_DC_WSI_TO_REGION = read_from_adl_DataFrame_new(adl,DC_WSI_TO_REGION_file_path,hearder_capitalized= False )            

df_DC_WSI_TO_REGION['DC_FACILITY_WSI'] = df_DC_WSI_TO_REGION['DC_FACILITY_WSI'].astype(str)

df_po_processed = df_po_processed.merge(df_DC_WSI_TO_REGION , how='left', left_on = ['DC_FACILITY_WSI','CUSTOMER','DC_FACILITY_COUNTRY'], right_on=['DC_FACILITY_WSI','CUSTOMER','DC_FACILITY_COUNTRY'])

df_po_processed.columns


HFM_OFFSET_ETA_By_Region_Customer_file_path =  "HAVI/HAVI_Freight_Management/03_Updated_Data/Shipment/HFM_OFFSET_ETA_By_Region_Customer.csv"


# with adl.open(HFM_OFFSET_ETA_By_Region_Customer_file_path) as f:
#         df_OFFSET_ETA_By_Region_Customer = pd.read_csv(f)
        
df_OFFSET_ETA_By_Region_Customer = read_from_adl_DataFrame_new(adl,HFM_OFFSET_ETA_By_Region_Customer_file_path,hearder_capitalized= False )           
        
df_OFFSET_ETA_By_Region_Customer.columns        
        
df_OFFSET_ETA_By_Region_Customer = df_OFFSET_ETA_By_Region_Customer[['DC_FACILITY_WSI','OFFSET_DAYS']]        
        
        
df_OFFSET_ETA_By_Region_Customer['DC_FACILITY_WSI'] = df_OFFSET_ETA_By_Region_Customer['DC_FACILITY_WSI'].astype(str)


df_po_processed_WSI = df_po_processed.merge(df_OFFSET_ETA_By_Region_Customer,on = ['DC_FACILITY_WSI'], how = 'left').dropna(subset = ['OFFSET_DAYS'])


df_po_processed_WSI.columns


df_po_processed_WSI = df_po_processed_WSI[['PO_NUMBER_UPDATE','OFFSET_DAYS']].drop_duplicates()

df_po_processed_WSI

#merge the dataframes 
df_shipment_eta_offset = pd.merge(df_shipment_eta, df_hfm_offset_eta, how='left', left_on='ISO_3166-1_3CODE', right_on='COUNTRY')
#remove NaN
df_shipment_eta_offset['OFFSET_DAYS'] = df_shipment_eta_offset['OFFSET_DAYS'].fillna(0)
#replace NaN to Zero for futher calculation
df_shipment_eta_offset['OFFSET_DAYS'] = df_shipment_eta_offset['OFFSET_DAYS'].astype(int)

#Get the length of ETA_POD_OVERRIDE to check if there is ETA_POD_OVERRIDE
df_shipment_eta_offset['Len_ETA_POD_OVERRIDE'] = df_shipment_eta_offset.ETA_POD_OVERRIDE.astype(str)
df_shipment_eta_offset['Len_ETA_POD_OVERRIDE'] = df_shipment_eta_offset.Len_ETA_POD_OVERRIDE.apply(lambda x : "" if x=="NaT" else x)
df_shipment_eta_offset['Len_ETA_POD_OVERRIDE']  = df_shipment_eta_offset.Len_ETA_POD_OVERRIDE.str.len() 


df_shipment_eta_offset['Len_ETA_POD'] = df_shipment_eta_offset.ETA_POD.astype(str)
df_shipment_eta_offset['Len_ETA_POD'] = df_shipment_eta_offset.Len_ETA_POD.apply(lambda x : "" if x=="NaT" else x)
df_shipment_eta_offset['Len_ETA_POD']  = df_shipment_eta_offset.Len_ETA_POD.str.len() 

for index, row in df_shipment_eta_offset.iterrows(): 
    #if user did not input the offset days then take the original DC_ETA_Adjust
    if row['OFFSET_DAYS'] == 0 :
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['DC_ETA_ADJUST']
    #if user input the offset days then check if there is override eta, if so then use the override eta add the offest day
    elif row['Len_ETA_POD_OVERRIDE'] > 0 and row['Len_ETA_POD'] > 0:
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['ETA_POD_OVERRIDE'] + pd.Timedelta(days=row['OFFSET_DAYS'])         
    elif  row['Len_ETA_POD_OVERRIDE']  == 0 and row['Len_ETA_POD'] > 0  :
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['ETA_POD'] + pd.Timedelta(days=row['OFFSET_DAYS'])   
    else :
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['REQUIRED_IN_STORE'] + pd.Timedelta(days=row['OFFSET_DAYS'])



print("Start Adding Regional Offsets Day to ETA_DC")

df_shipment_eta_offset.columns
        
df_shipment_eta_offset.drop(['OFFSET_DAYS'], axis=1,inplace=True)      



df_shipment_eta_offset = df_shipment_eta_offset.merge( df_po_processed_WSI, right_on = ['PO_NUMBER_UPDATE'], left_on = ['CUSTOMER_PO'], how = 'left')

df_shipment_eta_offset['OFFSET_DAYS'] = df_shipment_eta_offset['OFFSET_DAYS'].fillna(0)


for index, row in df_shipment_eta_offset.iterrows(): 
    #if user did not input the offset days then take the original DC_ETA_Adjust
    if row['OFFSET_DAYS'] == 0 :
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['DC_ETA_ADJUST']
    #if user input the offset days then check if there is override eta, if so then use the override eta add the offest day
    elif row['Len_ETA_POD_OVERRIDE'] > 0 and row['Len_ETA_POD'] > 0:
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['ETA_POD_OVERRIDE'] + pd.Timedelta(days=row['OFFSET_DAYS'])         
    elif  row['Len_ETA_POD_OVERRIDE']  == 0 and row['Len_ETA_POD'] > 0  :
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['ETA_POD'] + pd.Timedelta(days=row['OFFSET_DAYS'])   
    else :
        df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] = row['REQUIRED_IN_STORE'] + pd.Timedelta(days=row['OFFSET_DAYS'])

























# Use ALIAS_TEXT_1 as the Shipment override level 
df_shipment_eta_offset['ALIAS_TEXT_1'] = df_shipment_eta_offset['ALIAS_TEXT_1'].fillna('')

for index, row in df_shipment_eta_offset.iterrows():
      if len(row['ALIAS_TEXT_1']) > 0  :
          print(index)
          temp_datetime = pd.to_datetime(row['ALIAS_TEXT_1'], infer_datetime_format=True)
          print(temp_datetime.replace(tzinfo=timezone('Asia/Singapore')))
          df_shipment_eta_offset.at[index, 'New_DC_ETA_ADJUST'] =  pd.to_datetime(row['ALIAS_TEXT_1'], infer_datetime_format=True).replace(tzinfo=timezone('Asia/Singapore'))

df_shipment_eta['DC_ETA_ADJUST'] = df_shipment_eta_offset['New_DC_ETA_ADJUST']

df_shipment_eta['SELCTED_ETA'] = df_shipment_eta['DC_ETA_ADJUST']        







df_shipment_eta_offset['New_DC_ETA_ADJUST']  
df_shipment_eta['DC_ETA_ADJUST'] = df_shipment_eta_offset['New_DC_ETA_ADJUST']

df_shipment_eta['SELCTED_ETA'] = df_shipment_eta['DC_ETA_ADJUST']


po_file_substring = 'OFI_openPO_'
po_filepaths = get_most_recent_files(adl, po_raw_adlstage_path, po_file_substring ,3)

import re

PO_TWN_filepath = [k for k in po_filepaths if 'TWN' in k]

print("Read the file " + PO_TWN_filepath[0])

po_spec_column_headers = ['CUSTOMER', 'WRIN', 'GTIN', 'DC_FACILITY_WSI', 'DC_FACILITY_GLN',
    'DC_FACILITY_COUNTRY', 'ORDER_DATE', 'PO_NUMBER', 'PO_ETA', 'PO_STATUS',
    'SUPPLIER_FACILITY_WSI', 'SUPPLIER_FACILITY_GLN', 'OPEN_PO_CASES', 'ITEM_DESCRIPTION','TRUCK_DATE']

print("Start Reading Taiwan PO")

try:
 # with adl.open(PO_TWN_filepath[0]) as g:
 #     df_PO_TWN = pd.read_csv(g,names=  po_spec_column_headers,dtype= object)
     
  df_PO_TWN =   read_from_adl_DataFrame(adl,PO_TWN_filepath[0],usecols_param =po_spec_column_headers )  
  # df_PO_TWN.columns
     
except:      
    print("Something else went wrong")     
print("Start drop na")
     
df_PO_TWN = df_PO_TWN.dropna(subset = ['DC_FACILITY_WSI','TRUCK_DATE'])




df_PO_TWN['DC_FACILITY_WSI'] =     df_PO_TWN['DC_FACILITY_WSI'].astype(str)  
df_PO_TWN['PO_NUMBER'] =     df_PO_TWN['PO_NUMBER'].astype(str)  
# df_PO_TWN.dropna(subset= ['DC_FACILITY_WSI'],axis = 1 )
print("Start change Po remove 'A'")
     
# df_PO_TWN['CUSTOMER_PO'] = df_PO_TWN.apply(
#     lambda x: x['DC_FACILITY_WSI']+ '   '+ x['PO_NUMBER'][-7:]
#     if x['DC_FACILITY_COUNTRY'] == 'TWN' else x['PO_NUMBER_UPDATE'], axis =1 )     


df_PO_TWN['INTERNAL_PO']  = df_PO_TWN['PO_NUMBER'] 

df_PO_TWN = df_PO_TWN[['INTERNAL_PO','TRUCK_DATE']].drop_duplicates()

df_PO_TWN['TRUCK_DATE'] = pd.to_datetime(df_PO_TWN['TRUCK_DATE']).dt.tz_localize('UTC').dt.tz_convert('Asia/Singapore')


df_PO_TWN['TRUCK_DATE'] = np.where(
    df_PO_TWN['TRUCK_DATE'] < today_date ,
    today_date,
    # df_incoming_orders['SELCTED_ETA'],
    df_PO_TWN['TRUCK_DATE'])

# df_PO_TWN.dropna(['TRUCK_DATE'])
PO_With_A_Taiwan = (df_shipment_eta['POD_COUNTRY'] ==  'TAIWAN' ) & (df_shipment_eta['INTERNAL_PO'].str.contains('A'))
print("Step1")
df_shipment_eta['INTERNAL_PO']  =  np.where(PO_With_A_Taiwan, df_shipment_eta['INTERNAL_PO'].str.replace("A", ""), df_shipment_eta['INTERNAL_PO'])
df_shipment_eta.columns

df_shipment_eta = df_shipment_eta.merge(df_PO_TWN, how = 'left' ,on = ['INTERNAL_PO'])
df_shipment_eta['TRUCK_DATE'].astype(str)
df_shipment_eta['TRUCK_DATE_check'] = df_shipment_eta['TRUCK_DATE'].dt.strftime("%d %b, %Y")

df_shipment_eta['TRUCK_DATE_check'] = df_shipment_eta['TRUCK_DATE_check'].replace(np.nan, '', regex=False)




# import numpy as np
print("Start truck date to ETA_DC")
for index, row in df_shipment_eta.iterrows():
    if len(row['TRUCK_DATE_check'])  > 0  :
        print("Truck Date to Selected ETA")
        print(row['TRUCK_DATE_check'])
        df_shipment_eta.at[index, 'SELCTED_ETA'] =  row['TRUCK_DATE'] 
          
df_shipment_eta_test = df_shipment_eta.merge( df_po_processed_WSI, right_on = ['PO_NUMBER_UPDATE'], left_on = ['INTERNAL_PO'], how = 'left')

df_shipment_eta_test.columns

print("Start truck date to ETA_DC")
for index, row in df_shipment_eta.iterrows():
    if len(row['TRUCK_DATE_check'])  > 0  :
        print("Truck Date to Selected ETA")
        print(row['TRUCK_DATE_check'])
        df_shipment_eta.at[index, 'SELCTED_ETA'] =  row['TRUCK_DATE'] 
        
        
# print("Start Adding Regional Offsets Day to ETA_DC")
# for index, row in df_shipment_eta_test.iterrows():
#     if len(row['OFFSET_DAYS'])  > 0  :
#         # print("Truck Date to Selected ETA")
#         # print(row['TRUCK_DATE_check'])
#         df_shipment_eta_test.at[index, 'SELCTED_ETA'] =  row['TRUCK_DATE']         
        
        
    

# df_shipment_eta.rename(columns = {'COUNTRY' :'ISO_3166-1_3CODE'},inplace = True)

df_shipment_eta = df_shipment_eta.drop(columns = ['COUNTRY_NAME', 'ISO_3166-1_2CODE', 'ISO_3166-1_3CODE','TRUCK_DATE','TRUCK_DATE_check'])


# #### Purchase Order

# In[55]:
print("Purchase Order")

#---------------Data Ingestion---------------
df_po_processed = read_from_adl_DataFrame(adl,
                                          po_processed_filepath,
                                          dtype_dict=object)


#---------------Data Transformation---------------
df_po_processed = df_po_processed.drop_duplicates(keep='first').reset_index(
    drop=True)

df_po_processed['OPEN_PO_CASES'] = [
    float(i) for i in df_po_processed['OPEN_PO_CASES']
]

#---------------Time Transformation---------------
df_po_processed = convert_column_to_datetime_Dataframe(
    df_po_processed, ['ORDER_DATE', 'PO_ETA'])


original_po_cases_sum = df_po_processed['OPEN_PO_CASES'].sum()

#---------------Calculation of Pct. Splits in POs---------------
df_po_processed_agg = df_po_processed.groupby(
    ['DC_FACILITY_COUNTRY', 'PO_NUMBER']).agg({
        'OPEN_PO_CASES': 'sum'
    }).reset_index().rename(columns={'OPEN_PO_CASES': 'OPEN_PO_CASES_SUM'})

df_po_processed = df_po_processed.merge(
    df_po_processed_agg, on=['DC_FACILITY_COUNTRY',
                               'PO_NUMBER'], how='left').reset_index(drop=True)

df_po_processed['SPLIT'] = df_po_processed['OPEN_PO_CASES'] / df_po_processed[
    'OPEN_PO_CASES_SUM']

new_po_cases_sum = df_po_processed['OPEN_PO_CASES'].sum()

print('No Cases Lost in Calculation of PO Splits: %s' % (original_po_cases_sum==new_po_cases_sum))


# In[56]:


# print_Nunique(df_po_processed, ['WRIN', 'DC_FACILITY_COUNTRY', 'PO_NUMBER'])


# In[57]:

    






















evaluate_duplicates_exisit(df_po_processed)


# #### Incoming Orders

# In[58]:


#---------------Data Ingestion---------------
## ---Edited by Min, 04/13, moved the fill empty columns from below to the shipment dataframe ----------
empty_columns_headers = [
    'SHIPMENT_ID', 'CONSOL_ID', 'CARRIER', 'VESSEL', 'VOYAGE/FLIGHT',
    'CONTAINER_NO', 'SHIPPER_NAME'
]

fill_columns_headers = [
    'NO SHIPMENT ASSIGNED', 'NO CONSOL ASSIGNED', 'NO CARRIER ASSIGNED',
    'NO VESSEL ASSIGNED', 'NO VOYAGE/FLIGHT ASSIGNED', 'NO CONTAINER ASSIGNED',
    'NO SHIPPER ASSIGNED'
]

df_shipment_eta = fill_in_empty_node(df_shipment_eta,
                                        empty_columns_headers,
                                        fill_columns_headers)




#---------------#Fix the different length of PO number ---------------

for index, row in df_shipment_eta.iterrows():
    if str(row['CUSTOMER_PO']) != 'nan' and  row['POD_COUNTRY']  == "TAIWAN":
        df_shipment_eta.at[index,'CUSTOMER_PO_New'] = convert_PO_string(row['CUSTOMER_PO'].replace('A',''), ' ')


for index, row in df_shipment_eta.iterrows():
    if str(row['CUSTOMER_PO_New']) != 'nan' and (str(row['CUSTOMER_PO'][0:3:1])== '895' or str(row['CUSTOMER_PO'][0:3:1]) == '871' ) :
        
        df_shipment_eta.at[index,'CUSTOMER_PO'] =  row['CUSTOMER_PO_New'][0:3:1] + '   '+ row['CUSTOMER_PO_New'][-7:]
        
        # df_shipment_eta.at[index,'CUSTOMER_PO'] = df_po_raw.apply(
        #     lambda x: x['DC_FACILITY_WSI']+ '   '+ x['PO_NUMBER'][-7:]
        #     if x['DC_FACILITY_COUNTRY'] == 'TWN' else x['PO_NUMBER_UPDATE'], axis =1 )
        


                                   
        #     # print(row['CUSTOMER_PO'])   
        #     # print(row['CUSTOMER_PO'][6:13:1])
        #     # print(len(row['CUSTOMER_PO']))
        #     df_shipment_eta.at[index,'CUSTOMER_PO_Len'] = len(row['CUSTOMER_PO'][6:13:1])
        #     if len(row['CUSTOMER_PO'][6:13:1]) == 6 :
        #            df_shipment_eta.at[index,'CUSTOMER_PO_New'] = row['CUSTOMER_PO'][0:3:1] + " "*3 + "0" + row['CUSTOMER_PO'][6:13:1]
                   
df_po_processed_Col =  df_po_processed.columns           
        
df_po_processed = df_po_processed.merge(df_PO_TWN, how='left',
 left_on=['PO_NUMBER'],
 right_on=['INTERNAL_PO'] )     

df_po_processed['TRUCK_DATE'] = df_po_processed['TRUCK_DATE'].replace(np.nan, '', regex=False)

df_po_processed['TRUCK_DATE'] = df_po_processed['TRUCK_DATE'].astype(str)

print("df_po_processed TRUCK_DATE")
for index, row in df_po_processed.iterrows():
    if row['TRUCK_DATE']  != "NaT"  :
        print("Truck Date to PO_ETA")
        # print(row['TRUCK_DATE_check'])
        df_po_processed.at[index, 'PO_ETA'] =  row['TRUCK_DATE']      
        
df_po_processed = df_po_processed[df_po_processed_Col]        


##--------------------------------------------------------------------------------------------------------
df_incoming_orders = df_po_processed.merge(df_shipment_eta,
                                           how='left',
                                           left_on=['PO_NUMBER_UPDATE'],
                                           right_on=['CUSTOMER_PO'],
                                           indicator=True)
###override all the ETA by using the ETA in TWN PO files 20220103. Truck Date is the applied ETA date.

df_incoming_orders.columns

df_Matching_PO_Stats = df_po_processed.merge(df_shipment_eta,
                                           how='left',
                                           left_on=['PO_NUMBER_UPDATE'],
                                           right_on=['CUSTOMER_PO'],
                                           indicator=True)




# print("Start Reading Taiwan PO")
# with adl.open(PO_TWN_filepath[0]) as g:
#      df_PO_TWN = pd.read_csv(g,names=  po_spec_column_headers,dtype= object )
     
# print("Start drop na")
     
# df_PO_TWN = df_PO_TWN.dropna(subset = ['DC_FACILITY_WSI','TRUCK_DATE'])

# df_PO_TWN['DC_FACILITY_WSI'] =     df_PO_TWN['DC_FACILITY_WSI'].astype(str)  
# df_PO_TWN['PO_NUMBER'] =     df_PO_TWN['PO_NUMBER'].astype(str)  
# # df_PO_TWN.dropna(subset= ['DC_FACILITY_WSI'],axis = 1 )
# print("Start change Po remove 'A'")
     
# df_PO_TWN['PO_NUMBER_UPDATE'] = df_PO_TWN.apply(
#     lambda x: x['DC_FACILITY_WSI']+ '   '+ x['PO_NUMBER'][-7:]
#     if x['DC_FACILITY_COUNTRY'] == 'TWN' else x['PO_NUMBER_UPDATE'], axis =1 ) 


# df_PO_TWN = df_PO_TWN[['PO_NUMBER_UPDATE','TRUCK_DATE']].drop_duplicates()

# df_PO_TWN['TRUCK_DATE'] = pd.to_datetime(df_PO_TWN['TRUCK_DATE']).dt.tz_localize('UTC').dt.tz_convert('Asia/Singapore')

# # df_PO_TWN.dropna(['TRUCK_DATE'])
# PO_With_A_Taiwan = (df_shipment_eta['POD_COUNTRY'] ==  'TAIWAN' ) & (df_shipment_eta['INTERNAL_PO'].str.contains('A'))



# df_incoming_orders = df_incoming_orders.merge(df_PO_TWN, how = 'left' ,on = ['PO_NUMBER_UPDATE'])


# # df_incoming_orders['TRUCK_DATE'].astype(str)
# df_incoming_orders['TRUCK_DATE_check'] = df_incoming_orders['TRUCK_DATE'].dt.strftime("%d %b, %Y")

# df_incoming_orders['TRUCK_DATE_check'] = df_incoming_orders['TRUCK_DATE_check'].replace(np.nan, '', regex=False)

# # import numpy as np
# num = 0 
# print("Start truck date to ETA_DC")
# for index, row in df_incoming_orders.iterrows():
#     if len(row['TRUCK_DATE_check'])  > 0  :
#         print("Truck Date to Selected ETA")
#         print(row['TRUCK_DATE_check'])
#         df_incoming_orders.at[index, 'SELCTED_ETA'] =  row['TRUCK_DATE'] 
#         num = num + 1
#         print(num)



df_incoming_orders.columns



# Finish the Taiwan Truck Date override






df_incoming_orders['ALLOCATED_CASES'] = df_incoming_orders[
    'NUMBER_OF_CASES'] * df_incoming_orders['SPLIT']

df_incoming_orders['ALLOCATED_CASES'] = np.where(
    df_incoming_orders['ALLOCATED_CASES'].isna(),
    df_incoming_orders['OPEN_PO_CASES'], df_incoming_orders['ALLOCATED_CASES'])

df_incoming_orders_po_wsi = df_incoming_orders[['PO_NUMBER_UPDATE','DC_FACILITY_WSI']]




#20220106 PO ETA is DC ETA in Taiwan so no need to add offset 7 days

# df_incoming_orders['SELCTED_ETA'] = np.where(
#     (df_incoming_orders['SELCTED_ETA'].isna()) &
#     (df_incoming_orders['DC_FACILITY_COUNTRY'] == 'TWN'),
#     df_incoming_orders['PO_ETA'] + pd.Timedelta(days=7),
#     df_incoming_orders['SELCTED_ETA'])

df_incoming_orders['SELCTED_ETA'] = np.where(
    df_incoming_orders['SELCTED_ETA'].isna(), df_incoming_orders['PO_ETA'],
    df_incoming_orders['SELCTED_ETA'])

df_incoming_orders = df_incoming_orders.dropna(
    subset=['SELCTED_ETA']).reset_index(drop=True)

empty_columns_headers = [
    'SHIPMENT_ID', 'CONSOL_ID', 'CARRIER', 'VESSEL', 'VOYAGE/FLIGHT',
    'CONTAINER_NO', 'SHIPPER_NAME'
]

fill_columns_headers = [
    'NO SHIPMENT ASSIGNED', 'NO CONSOL ASSIGNED', 'NO CARRIER ASSIGNED',
    'NO VESSEL ASSIGNED', 'NO VOYAGE/FLIGHT ASSIGNED', 'NO CONTAINER ASSIGNED',
    'NO SHIPPER ASSIGNED'
]

df_incoming_orders = fill_in_empty_node(df_incoming_orders,
                                        empty_columns_headers,
                                        fill_columns_headers)

## Intialize Open PO
df_incoming_orders['OPEN_PO_FLAG'] = np.where(df_incoming_orders['_merge'] == 'both', 'SHIPPED PO', 'OPEN PO')

df_incoming_orders_archive = df_incoming_orders.copy()

incoming_orders_columns = [
    'WRIN', 'DC_FACILITY_COUNTRY', 'PO_NUMBER_UPDATE', 'SHIPMENT_ID',
    'CONSOL_ID', 'CARRIER', 'VESSEL', 'VOYAGE/FLIGHT', 'CONTAINER_NO',
    'SHIPPER_NAME', 'SELCTED_ETA', 'ALLOCATED_CASES', 'OPEN_PO_FLAG'
]



df_incoming_orders = df_incoming_orders[incoming_orders_columns]

df_incoming_orders = df_incoming_orders.groupby([
    'WRIN', 'DC_FACILITY_COUNTRY', 'PO_NUMBER_UPDATE', 'SHIPMENT_ID',
    'CONSOL_ID', 'CARRIER', 'VESSEL', 'VOYAGE/FLIGHT', 'CONTAINER_NO',
    'SHIPPER_NAME', 'SELCTED_ETA', 'OPEN_PO_FLAG'
]).agg({
    'ALLOCATED_CASES': 'sum'
}).reset_index()

df_incoming_orders = add_timezone_DataFrame(df_incoming_orders,
                                            ['SELCTED_ETA'], 'Asia/Singapore')

df_incoming_orders['SELCTED_ETA'] = [
    i.normalize() for i in df_incoming_orders['SELCTED_ETA']
]

## Copy for Late Shipment
df_incoming_orders_late_shipment = df_incoming_orders[
    ~((df_incoming_orders['SHIPMENT_ID'] == 'NO SHIPMENT ASSIGNED') &
      (df_incoming_orders['CONTAINER_NO'] == 'NO CONTAINER ASSIGNED') &
      (df_incoming_orders['CONSOL_ID'] == 'NO CONSOL ASSIGNED'))
    & (df_incoming_orders['SELCTED_ETA'] < today_date)]

## Intialize Shipment Late Flag

df_incoming_orders['SHIPMENT_LATE_FLAG'] = None

## Assign Shipment Late Flag Message
df_incoming_orders['SHIPMENT_LATE_FLAG'] = np.where(
    ~((df_incoming_orders['SHIPMENT_ID'] == 'NO SHIPMENT ASSIGNED') &
      (df_incoming_orders['CONTAINER_NO'] == 'NO CONTAINER ASSIGNED') &
      (df_incoming_orders['CONSOL_ID'] == 'NO CONSOL ASSIGNED'))
    & (df_incoming_orders['SELCTED_ETA'] < today_date), 'PAST ALLOCATION',
    'FUTURE ALLOCATION')
###Change to not to set the before today ETA to Today ETA 20220628
df_incoming_orders['SELCTED_ETA'] = np.where(
    df_incoming_orders['SHIPMENT_LATE_FLAG']=='PAST ALLOCATION',
    today_date,
    # df_incoming_orders['SELCTED_ETA'],
    df_incoming_orders['SELCTED_ETA'])

# df_incoming_orders.to_csv(r"C:\Users\danny\Downloads\df_incoming_orders.csv")

# df_PO_TWN.to_csv(r"C:\Users\danny\Downloads\df_PO_TWNs.csv")

# df_po_processed.to_csv(r"C:\Users\danny\Downloads\df_po_processed.csv")

# In[59]:

## For the use of the MYS, IDN Visibility : MYS_MCD_DOS.py
df_incoming_orders_sku_level_file_path =  ace_data_path + 'SHIPMENT_ORDER_SKU_LEVEL.csv'
upload_to_adl_DataFrame(adl, df_incoming_orders, df_incoming_orders_sku_level_file_path)

df_incoming_orders_po_wsi_file_path =  ace_data_path + 'df_incoming_orders_po_wsi.csv' 

upload_to_adl_DataFrame(adl, df_incoming_orders_po_wsi, df_incoming_orders_po_wsi_file_path)



# In[60]:


df_incoming_orders['OPEN_PO_FLAG'].unique()


# In[61]:


df_incoming_orders['SHIPMENT_LATE_FLAG'].unique()


# In[62]:


df_shipment_eta[df_shipment_eta['SHIPMENT_ID']=='S00051091']['CARRIER_BKG._REF']


# In[63]:


df_shipment_eta.columns


# In[64]:


df_incoming_orders[df_incoming_orders['SHIPMENT_LATE_FLAG'] == 'LATE SHIPMENT']


# In[65]:


evaluate_duplicates_exisit(df_incoming_orders)


# In[66]:


# df_incoming_orders_po_matched = df_incoming_orders[df_incoming_orders['_merge'] == 'both']
# print(df_incoming_orders_po_matched.shape)

# df_incoming_orders_po_unmatched = df_incoming_orders[df_incoming_orders['_merge'] == 'left_only']
# print(df_incoming_orders_po_unmatched.shape)


# In[67]:


# #------------Matching Statistics----------

# df_incoming_orders = df_po_processed.merge(df_shipment_eta,
#                                            how='left',
#                                            left_on=['PO_NUMBER_UPDATE'],
#                                            right_on=['CUSTOMER_PO'],
#                                            indicator=True)

# df_incoming_orders_stats = df_incoming_orders.groupby(
#     ['DC_FACILITY_COUNTRY', '_merge'])[['PO_NUMBER']].count().dropna().reset_index()

# df_incoming_orders_stats = pd.pivot_table(df_incoming_orders_stats, values='PO_NUMBER', index=['DC_FACILITY_COUNTRY'],
#                     columns=['_merge'])

# df_incoming_orders_stats = df_incoming_orders_stats.rename(
#     columns={
#         'both': 'MATCHED',
#         'left_only': 'UNMATCHED'
#     })

# df_incoming_orders_stats['TOTAL'] = df_incoming_orders_stats[
#     'MATCHED'] + df_incoming_orders_stats['UNMATCHED']

# df_incoming_orders_stats['MATCHED_PCT'] = df_incoming_orders_stats['MATCHED']/df_incoming_orders_stats['TOTAL']
# df_incoming_orders_stats['MATCHED_PCT'] = [round(i,2) for i in df_incoming_orders_stats['MATCHED_PCT']]

# df_incoming_orders_stats = df_incoming_orders_stats.fillna(0)
# df_incoming_orders_stats.reset_index()


# In[68]:


# df_incoming_orders_po = df_incoming_orders_po[[
#     'CUSTOMER_PO', 'SELCTED_ETA', 'DC_FACILITY_COUNTRY', 'WRIN',
#     'NUMBER_OF_CASES', 'SPLIT', 'ALLOCATED_CASES'
# ]]

# df_incoming_orders_po.to_csv('PO_Orders_Matching.csv')

# df_incoming_orders_po['SELCTED_ETA'] = df_incoming_orders_po[
#     'SELCTED_ETA'].dt.tz_convert(None)
# df_incoming_orders_po.to_excel('PO_Orders_Matching.xlsx', index=False)


# In[69]:


# print_Nunique(df_incoming_orders, ['WRIN', 'DC_FACILITY_COUNTRY'])


# In[70]:


evaluate_duplicates_exisit(df_incoming_orders)


# #### Inventory

# In[71]:


# with adl.open(inventory_processed_filepath) as f:
#     df_inventory_processed = pd.read_csv(f, dtype=object)
    
df_inventory_processed =  read_from_adl_DataFrame_new(adl,inventory_processed_filepath,hearder_capitalized= False )    

df_inventory_processed['INVENTORY_CASES'] = [
    float(i) for i in df_inventory_processed['INVENTORY_CASES']
]

df_inventory_processed = convert_column_to_datetime_Dataframe(
    df_inventory_processed, ['INVENTORY_DATE'])

df_inventory = df_inventory_processed[[
    'DC_FACILITY_COUNTRY', 'WRIN', 'INVENTORY_DATE', 'INVENTORY_CASES'
]]

df_inventory = df_inventory.groupby(
    ['DC_FACILITY_COUNTRY', 'WRIN', 'INVENTORY_DATE']).agg({
        'INVENTORY_CASES':
        'sum'
    }).reset_index()


df_inventory['INVENTORY_DATE']  =  [i.normalize() for i in df_inventory['INVENTORY_DATE']]


# In[72]:


df_inventory.isna().sum()


# In[73]:


df_inventory.head()


# In[ ]:


# print_Nunique(df_inventory, ['WRIN', 'DC_FACILITY_COUNTRY'])


# In[ ]:


evaluate_duplicates_exisit(df_inventory)


# #### Demand

# In[74]:


# with adl.open(demand_processed_filepath) as f:
#     df_demand_processed = pd.read_csv(f, dtype = object)
    


df_demand_processed = read_from_adl_DataFrame_new(adl,demand_processed_filepath)  

df_demand_processed = convert_column_to_datetime_Dataframe(
    df_demand_processed, ['DATE'])

df_demand_processed['DAILY_FORECASTINCASES'] = [
    float(i) for i in df_demand_processed['DAILY_FORECASTINCASES']
]

df_demand_processed['PCT_ALLOCATION'] = [
    float(i) for i in df_demand_processed['PCT_ALLOCATION']
]

df_demand = df_demand_processed[[
    'COUNTRYCODE', 'WRIN', 'DATE', 'DAILY_FORECASTINCASES'
]]

df_demand['DATE']  =  [i.normalize() for i in df_demand['DATE']]

for col in ['WRIN']:
    df_demand[col] = [str(i).zfill(8) for i in df_demand[col]]

print(df_demand.shape)
# In[75]:


# print_Nunique(df_demand, ['COUNTRYCODE', 'WRIN'])


# In[76]:


evaluate_duplicates_exisit(df_demand)


# #### Child SKUs

# ### Wrin Grouping 

# In[77]:


# with adl.open(master_data_path + 'Sharepoint_Hub/Wrin_Group_Matrix.xlsx') as f:
#     df_wrin_sub_matrix = pd.read_excel(f)
# df_wrin_sub_matrix = stack_cols(df_wrin_sub_matrix, ['CHILD_SKU_ID'], 'WRIN')

# In[78]:

# with adl.open(master_data_path + 'Item_Attribute/OFI_ItemMaster_TWN.csv') as f:
#     df_ItemMaster_TWN = pd.read_csv(f)    













df_wrin_sub_matrix = df_SIMs[['WRIN','ASSEMBLY_ITEM']].drop_duplicates().reset_index(drop = True)
for col in ['WRIN']:
    df_wrin_sub_matrix[col] = [str(i).zfill(8) for i in df_wrin_sub_matrix[col]]
    
df_wrin_sub_matrix['CONVERSION_FACTOR'] = None
df_wrin_sub_matrix = stack_cols(df_wrin_sub_matrix, ['WRIN'], 'WRIN')
df_wrin_sub_matrix = fill_NA_in_cols(df_wrin_sub_matrix,
                                     {'CONVERSION_FACTOR': 1})

df_wrin_sub_matrix = df_wrin_sub_matrix.rename(columns = {'ASSEMBLY_ITEM':'SKU_GROUP'})

df_wrin_sub_matrix = df_wrin_sub_matrix.drop_duplicates(["WRIN"])



#Read User Defined Wrin Group
# with adl.open("HAVI/HAVI_Freight_Management/06_PowerBI/Master/HFM_Wrin_Group_User_Defined.csv") as f:
#     df_User_Wrin_Group = pd.read_csv(f)
    
df_User_Wrin_Group = read_from_adl_DataFrame_new(adl,"HAVI/HAVI_Freight_Management/06_PowerBI/Master/HFM_Wrin_Group_User_Defined.csv" ,hearder_capitalized= False )      

# df_User_Wrin_Group = df_User_Wrin_Group[(df_User_Wrin_Group['WrinGroup'] == '1911') == False]


# with adl.open("HAVI/HAVI_Freight_Management/00_Master_Data/Group_Code.csv") as f:
#     df_TW_Group_Code = pd.read_csv(f)

colnames=['WRIN', 'WRIN_DESC', 'Group_Code', 'Group_Category']

    
df_TW_Group_Code = read_from_adl_DataFrame_new(adl,"HAVI/HAVI_Freight_Management/00_Master_Data/Group_Code.csv" ,hearder_capitalized= False,usecols_param=colnames )     
    
df_TW_Group_Code    

df_TW_Group_Code.columns
df_TW_Group_Code['WrinGroup'] =  df_TW_Group_Code['Group_Code']
df_TW_Group_Code['CONVERSION_FACTOR'] = 1
df_TW_Group_Code['Market'] = 'TAIWAN'
df_TW_Group_Code['Group_Code'] = df_TW_Group_Code['Group_Code'].astype(str).str.replace(' ', '')

# df_TW_Group_Code = df_TW_Group_Code[df_TW_Group_Code['Group_Code'].isin(['1911', '3805', '2504','3522','3511','2502','2503','4131','4488 ','4402','3804','5120','1912'])]
df_TW_Group_Code = df_TW_Group_Code
df_TW_Group_Code = df_TW_Group_Code[df_User_Wrin_Group.columns]

# with adl.open("HAVI/HAVI_Freight_Management/00_Master_Data/UDF_ITEM_MASTER/MYS_UDF_ITEM_MASTER.xlsx") as f:
#     df_MYS_Group_Code = pd.read_excel(f)
    
df_MYS_Group_Code = read_from_adl_DataFrame_xlsx(adl, "HAVI/HAVI_Freight_Management/00_Master_Data/UDF_ITEM_MASTER/MYS_UDF_ITEM_MASTER.xlsx")    

for col in ['WRIN']:
    df_MYS_Group_Code[col] = [str(i).zfill(8) for i in df_MYS_Group_Code[col]]




df_MYS_Group_Code['WRIN_ORG'] = df_MYS_Group_Code['WRIN']

df_MYS_Group_Code['WrinGroup']  = df_MYS_Group_Code['DESCRIPTION']
df_MYS_Group_Code['CONVERSION_FACTOR'] = 1 
df_MYS_Group_Code['Market']      = 'MALAYSIA'

df_MYS_Group_Code = df_MYS_Group_Code.drop_duplicates(subset= ['WRIN_ORG'])   
# df_MYS_Group_Code.drop('WRIN (default)',axis = 1 ,inplace=True)

# MYS_Columns_for_unpivot = df_MYS_Group_Code.columns[:-1]

# df_MYS_Group_Code_unpivot =  pd.melt(df_MYS_Group_Code, id_vars='DESCRIPTION', value_vars=MYS_Columns_for_unpivot)

# df_MYS_Group_Code_unpivot.drop('variable',axis = 1 ,inplace=True)
# df_MYS_Group_Code_unpivot['value'] = df_MYS_Group_Code_unpivot['value'].astype(str)
# df_MYS_Group_Code_unpivot['value'].replace('-',np.nan,inplace = True)

# df_MYS_Group_Code_unpivot.dropna(subset = ['value'],inplace = True)

# df_MYS_Group_Code_unpivot['WrinGroup'] = df_MYS_Group_Code_unpivot['DESCRIPTION']
# df_MYS_Group_Code_unpivot['WRIN'] = df_MYS_Group_Code_unpivot['value'].astype(str).apply(add_zero)

# df_MYS_Group_Code_unpivot['Market'] = 'MALAYSIA'
# df_MYS_Group_Code_unpivot['CONVERSION_FACTOR'] = 1


df_MYS_Group_Code_subset = df_MYS_Group_Code[df_TW_Group_Code.columns]





# with adl.open("HAVI/HAVI_Freight_Management/00_Master_Data/UDF_ITEM_MASTER/MYS_UDF_ITEM_MASTER.xlsx") as f:
#     df_IDN_Group_Code = pd.read_excel(f)

df_IDN_Group_Code = read_from_adl_DataFrame_xlsx(adl,"HAVI/HAVI_Freight_Management/00_Master_Data/UDF_ITEM_MASTER/MYS_UDF_ITEM_MASTER.xlsx")

for col in ['WRIN']:
    df_IDN_Group_Code[col] = [str(i).zfill(8) for i in df_IDN_Group_Code[col]]




df_IDN_Group_Code['WRIN_ORG'] = df_IDN_Group_Code['WRIN']

df_IDN_Group_Code['WrinGroup']  = df_IDN_Group_Code['DESCRIPTION']
df_IDN_Group_Code['CONVERSION_FACTOR'] = 1 
df_IDN_Group_Code['Market']      = "INODNESIA"

df_IDN_Group_Code = df_IDN_Group_Code.drop_duplicates(subset= ['WRIN_ORG'])   



df_IDN_Group_Code_subset = df_IDN_Group_Code[df_TW_Group_Code.columns]





df_User_Wrin_Group = pd.concat([df_TW_Group_Code,df_MYS_Group_Code_subset,df_IDN_Group_Code_subset])



df_User_Wrin_Group = df_User_Wrin_Group.merge(df_country_code,
    left_on=['Market'],
    right_on=['COUNTRY_NAME'],
    how='left')


df_User_Wrin_Group['WrinGroup'] = df_User_Wrin_Group['ISO_3166-1_3CODE'] + '_' + df_User_Wrin_Group['WrinGroup'] 





df_User_Wrin_Group = df_User_Wrin_Group.drop(['ISO_3166-1_2CODE','COUNTRY_NAME','Market'],axis=1)

df_User_Wrin_Group['WRIN'] = df_User_Wrin_Group['WRIN'].apply(str)


df_User_Wrin_Group['WRIN'] = df_User_Wrin_Group['WRIN'].apply(add_zero)

df_User_Wrin_Group = df_User_Wrin_Group.rename(columns={'WRIN' : 'WRIN_ORG','WrinGroup': 'SKU_GROUP','ISO_3166-1_3CODE' :'COUNTRYCODE'})

df_User_Wrin_Group = df_User_Wrin_Group.dropna()
####Conversion Rate get the max packsize within the same groupcode




# with adl.open("HAVI/HAVI_Freight_Management/00_Master_Data/Item_Attribute/OFI_ItemMaster_TWN.csv") as f:
#     df_Item_Mstr = pd.read_csv(f)

df_Item_Mstr = read_from_adl_DataFrame_new(adl,"HAVI/HAVI_Freight_Management/00_Master_Data/Item_Attribute/OFI_ItemMaster_TWN.csv",hearder_capitalized= False )

for col in ['WRIN']:
    df_inventory['WRIN']  = [str(i).zfill(8) for i in df_inventory[col]]

df_inventory_WRIN_List = df_inventory[df_inventory['DC_FACILITY_COUNTRY'] == 'TWN' ]

df_inventory_WRIN_List['CountryWrin'] = df_inventory_WRIN_List['DC_FACILITY_COUNTRY'] + df_inventory_WRIN_List['WRIN']

df_inventory_WRIN_List = df_inventory_WRIN_List['CountryWrin'].unique().tolist()  


df_Item_Mstr['COUNTRYCODE'] = 'TWN'

df_Item_Mstr['CountryWrin'] = df_Item_Mstr['COUNTRYCODE'] + df_Item_Mstr['WRIN']


df_Item_Mstr = df_Item_Mstr[df_Item_Mstr['CountryWrin'].isin(df_inventory_WRIN_List)]



df_Item_Mstr_merge =  df_Item_Mstr.merge(df_TW_Group_Code ,on = 'WRIN', how = 'left')

max_packsize_per_group_code = df_Item_Mstr_merge.groupby(['COUNTRYCODE','WrinGroup'])['Case_Pack_Qty'].max().reset_index()


max_packsize_per_group_code.columns = ['COUNTRYCODE','WrinGroup', 'Max_Case_Pack_Qty']

df_Item_Mstr_merge_max_pack_size = df_Item_Mstr_merge.merge(max_packsize_per_group_code,on =['COUNTRYCODE', 'WrinGroup'], how = 'left' )

df_Item_Mstr_merge_max_pack_size['ratio'] =  df_Item_Mstr_merge_max_pack_size['Case_Pack_Qty']/df_Item_Mstr_merge_max_pack_size['Max_Case_Pack_Qty']

 
df_Item_Mstr_pack_size_ratio =  df_Item_Mstr_merge_max_pack_size[['COUNTRYCODE','WRIN','ratio']]


df_Item_Mstr_pack_size_ratio = df_Item_Mstr_pack_size_ratio.rename(columns = {'WRIN':'WRIN_ORG'})


df_Item_Mstr_pack_size_ratio.dropna(subset = ['ratio'],inplace = True)

# In[79]:


## get the final aggregated columns for each df
demand_cols = [
    col for col in df_demand.columns if col not in ['DAILY_FORECASTINCASES']
] + ['AI_Type'] 
inventory_cols = [
    col for col in df_inventory.columns if col not in ['INVENTORY_CASES']
] + ['AI_Type'] 
incoming_orders_cols = [
    col for col in df_incoming_orders.columns
    if col not in ['ALLOCATED_CASES']
] + ['AI_Type'] 

#-----------DEMAND----------------
# df_demand.to_csv(r"C:\Users\danny.huang\Downloads\df_demand.csv")


df_demand = subsitute_col_from_another_df(df_demand, df_wrin_sub_matrix,
                                          ['WRIN'], 'WRIN', 'SKU_GROUP', True,
                                          True)

# df_demand.to_csv("demand.csv")


df_demand_User_Defind = df_demand.merge(df_User_Wrin_Group , left_on=['COUNTRYCODE','WRIN_ORG'],
                                        right_on=['COUNTRYCODE','WRIN_ORG'],how='inner')
##---------df_demand--User Defined-------------
df_demand_User_Defind.columns.str.endswith('x')
df_demand_User_Defind = df_demand_User_Defind.loc[:,~df_demand_User_Defind.columns.str.endswith('x')]
df_demand_User_Defind.columns  = df_demand_User_Defind.columns.str.rstrip('_y')



df_demand_User_Defind = df_demand_User_Defind[['COUNTRYCODE', 'WRIN', 'DATE', 'DAILY_FORECASTINCASES', 'WRIN_ORG',
       'SKU_GROUP', 'CONVERSION_FACTOR']]






df_demand_User_Defind['WRIN'] = df_demand_User_Defind['SKU_GROUP'] 

df_demand['AI_Type'] = 'SIM'
df_demand_User_Defind['AI_Type'] = 'USER' 

df_demand = pd.concat([df_demand,df_demand_User_Defind]).reset_index(drop = True)




df_demand = df_demand.merge(df_Item_Mstr_pack_size_ratio,how = 'left',on = ['COUNTRYCODE','WRIN_ORG'] )

print("Conversion Rate for Demand")


df_demand['ratio'] = df_demand['ratio'].fillna(1)

df_demand['CONVERSION_FACTOR'] = df_demand['ratio'] 


df_demand_org = df_demand.copy()


df_demand = convert_qty_by_factor(df_demand, 'CONVERSION_FACTOR',
                                  ['DAILY_FORECASTINCASES'], 1, True)
df_demand = aggregate_qty(df_demand, demand_cols ,
                          {'DAILY_FORECASTINCASES': 'sum'})

# demand_cols 

df_demand['DAILY_FORECASTINCASES'] = [
    float(i) for i in df_demand['DAILY_FORECASTINCASES']
]




list_demand_columns_subset = df_demand.columns.tolist() + [
    i for i in df_demand_org.columns if '_ORG' in i
]
df_demand_org = df_demand_org[list_demand_columns_subset]

# print(df_demand_org[df_demand_org['WRIN_ORG'] == '00311152'])
#-----------Inventory----------------
df_inventory = subsitute_col_from_another_df(df_inventory, df_wrin_sub_matrix,
                                             ['WRIN'], 'WRIN', 'SKU_GROUP',
                                             True, True)

df_User_Wrin_Group = df_User_Wrin_Group.rename(columns= {'COUNTRYCODE' : 'DC_FACILITY_COUNTRY'})



df_inventory_User_Defind = df_inventory.merge(df_User_Wrin_Group , left_on=['DC_FACILITY_COUNTRY','WRIN_ORG'],
                                        right_on=['DC_FACILITY_COUNTRY','WRIN_ORG'],how='inner')
df_inventory_User_Defind['INVENTORY_DATE'] = today_date

##----------df_inventory--User Defined-------------
df_inventory_User_Defind.columns.str.endswith('x')
df_inventory_User_Defind = df_inventory_User_Defind.loc[:,~df_inventory_User_Defind.columns.str.endswith('x')]
df_inventory_User_Defind.columns  = df_inventory_User_Defind.columns.str.rstrip('_y')
df_inventory_User_Defind = df_inventory_User_Defind[['DC_FACILITY_COUNTRY', 'WRIN', 'INVENTORY_DATE', 'INVENTORY_CASES', 'WRIN_ORG',
       'SKU_GROUP', 'CONVERSION_FACTOR']]


df_inventory_User_Defind['AI_Type'] = 'USER' 
df_inventory['AI_Type'] = 'SIM' 

df_inventory['INVENTORY_DATE'] = today_date


df_inventory_User_Defind['WRIN'] = df_inventory_User_Defind['SKU_GROUP']
df_inventory = pd.concat([df_inventory,df_inventory_User_Defind]).reset_index(drop = True)




df_inventory = df_inventory.merge(df_Item_Mstr_pack_size_ratio,how = 'left',left_on = ['DC_FACILITY_COUNTRY','WRIN_ORG'],right_on = ['COUNTRYCODE','WRIN_ORG']  )
print("Conversion Rate for Inventory")

df_inventory['ratio'] = df_inventory['ratio'].fillna(1)

df_inventory['CONVERSION_FACTOR'] = df_inventory['ratio'] 




df_inventory_org = df_inventory.copy()


df_inventory = convert_qty_by_factor(df_inventory, 'CONVERSION_FACTOR',
                                  ['INVENTORY_CASES'], 1, True)



df_inventory = aggregate_qty(df_inventory, inventory_cols  ,
                          {'INVENTORY_CASES': 'sum'})




list_inventory_columns_subset = df_inventory.columns.tolist() + [
    i for i in df_inventory_org.columns if '_ORG' in i
]




df_inventory_org = df_inventory_org[list_inventory_columns_subset]

#-----------Incoming Orders-----------------
df_incoming_orders = subsitute_col_from_another_df(df_incoming_orders,
                                                   df_wrin_sub_matrix,
                                                   ['WRIN'], 'WRIN',
                                                   'SKU_GROUP', True, True)
df_incoming_orders_User_Defind = df_incoming_orders.merge(df_User_Wrin_Group , left_on=['DC_FACILITY_COUNTRY','WRIN_ORG'],
                                        right_on=['DC_FACILITY_COUNTRY','WRIN_ORG'],how='inner')

#-----------df_incoming_orders--User Defined-------------
df_incoming_orders_User_Defind.columns.str.endswith('x')
df_incoming_orders_User_Defind = df_incoming_orders_User_Defind.loc[:,~df_incoming_orders_User_Defind.columns.str.endswith('x')]
df_incoming_orders_User_Defind.columns  = df_incoming_orders_User_Defind.columns.str.rstrip('_y')
df_incoming_orders_User_Defind = df_incoming_orders_User_Defind[df_incoming_orders.columns]
	   
df_incoming_orders_User_Defind['WRIN'] =  df_incoming_orders_User_Defind['SKU_GROUP']

df_incoming_orders_User_Defind['AI_Type'] = 'USER' 
df_incoming_orders['AI_Type'] = 'SIM'


df_incoming_orders = pd.concat([df_incoming_orders,df_incoming_orders_User_Defind]).reset_index(drop = True)



# df_incoming_orders.to_csv(r"C:\Users\danny.huang\Downloads\df_incoming_orders.csv")
df_incoming_orders  = df_incoming_orders.merge(df_Item_Mstr_pack_size_ratio,how = 'left',left_on = ['DC_FACILITY_COUNTRY','WRIN_ORG'],right_on = ['COUNTRYCODE','WRIN_ORG']  )


df_incoming_orders['ratio'] = df_incoming_orders['ratio'].fillna(1)

df_incoming_orders['CONVERSION_FACTOR'] = df_incoming_orders['ratio'] 


df_incoming_orders = convert_qty_by_factor(df_incoming_orders, 'CONVERSION_FACTOR',
                                  ['ALLOCATED_CASES'], 1, True)
df_incoming_orders.columns
df_incoming_orders_org = df_incoming_orders.copy()
df_incoming_orders = aggregate_qty(df_incoming_orders, incoming_orders_cols ,
                          {'ALLOCATED_CASES': 'sum'})
print("Conversion Rate for Order")

list_incoming_order_columns_subset = df_incoming_orders.columns.tolist() + [
    i for i in df_incoming_orders_org.columns if '_ORG' in i
]
df_incoming_orders_org = df_incoming_orders_org[list_incoming_order_columns_subset]





# ### Subset by Time

# In[80]:


df_incoming_orders_subset = slice_by_time_DataFrame(df_incoming_orders,
                                                    'SELCTED_ETA',
                                                    startdate_parameter,
                                                    slice_type='after')

df_incoming_orders_subset = df_incoming_orders_subset.drop('AI_Type', axis=1)

df_inventory_subset = slice_by_time_DataFrame(df_inventory,
                                              'INVENTORY_DATE',
                                              startdate_parameter,
                                              slice_type='after')


df_inventory_subset = df_inventory_subset.drop('AI_Type', axis=1)


df_demand_subset = slice_by_time_DataFrame(df_demand,
                                           'DATE',
                                           startdate_parameter,
                                           slice_type='after')

df_demand_subset = df_demand_subset.drop('AI_Type', axis=1)




df_incoming_orders_subset_org = slice_by_time_DataFrame(df_incoming_orders_org,
                                                    'SELCTED_ETA',
                                                    startdate_parameter,
                                                    slice_type='after')

df_inventory_subset_org = slice_by_time_DataFrame(df_inventory_org,
                                              'INVENTORY_DATE',
                                              startdate_parameter,
                                              slice_type='after')

df_demand_subset_org = slice_by_time_DataFrame(df_demand_org,
                                           'DATE',
                                           startdate_parameter,
                                           slice_type='after')



Link_Wrin_Type = pd.concat([df_incoming_orders_subset_org, df_inventory_subset_org, df_demand_subset_org], ignore_index=True)


Link_Wrin_Type = Link_Wrin_Type[['WRIN','AI_Type']].drop_duplicates(keep='first')



upload_to_adl_DataFrame(adl, Link_Wrin_Type, "HAVI/HAVI_Freight_Management/04_ACE_Data/LINK_WRIN_Type.csv") 



# In[81]:


df_shipment_eta.columns


# In[82]:


df_shipment_eta_subset = df_shipment_eta[['SHIPMENT_ID', 'CONSOL_ID', 'CONTAINER_NO','ETD_POL',
       'ETD_POL_OVERRIDE','PREVIOUS_ETD_POL', 'ETA_POD', 'ETA_POD_OVERRIDE','PREVIOUS_ETA_POD', 'ATD',
       'ATD_OVERRIDE','PREVIOUS_ATD', 'ATA', 'ATA_OVERRIDE','PREVIOUS_ATA', 'CARRIER_BKG._REF','COMMENT']]


# In[83]:
df_incoming_orders_subset_org = df_incoming_orders_subset_org.drop('AI_Type', axis = 1 )

df_incoming_orders_subset_org_merge = df_incoming_orders_subset_org.merge(
    df_shipment_eta_subset,
    how='left',
    on=['SHIPMENT_ID', 'CONSOL_ID', 'CONTAINER_NO']).reset_index(drop = True)


# In[84]:


df_incoming_orders_subset_org_merge.shape


# ### Node

# #### Date

# In[ ]:


list_demand_dates = [df_demand_subset['DATE'].unique()]

list_inventory_dates = [df_inventory_subset['INVENTORY_DATE'].unique()]

list_allocated_dates = [df_incoming_orders['SELCTED_ETA'].unique()]
list_total_dates = list_demand_dates + list_demand_dates + list_allocated_dates
list_total_dates = [item for sublist in list_total_dates for item in sublist]
list_total_dates = list(set(list_total_dates))


# In[ ]:


df_node_date = pd.DataFrame(columns=['DATE_ID'], data=list_total_dates)
date_filepath = ace_data_path + 'NODE_DATE.csv'
upload_to_adl_DataFrame(adl, df_node_date, date_filepath)


# In[ ]:


df_node_date.head()


# #### Week

# In[ ]:


number_of_weeks = 20

full_end_of_week_date = today_date + timedelta(weeks=20)  +  timedelta(days = 7 - today_date.weekday()-1)


time_span = pd.date_range(start=today_date,
                          periods=number_of_weeks*7,
                          freq='D')


# In[ ]:


df_node_week = pd.DataFrame(columns=['WEEK_ID'], data=create_array_ascending(number_of_weeks, 1))


# In[ ]:


week_filepath = ace_data_path + 'NODE_WEEK.csv'
upload_to_adl_DataFrame(adl, df_node_week, week_filepath)


# #### PO

# In[ ]:


list_unique_PO = df_incoming_orders_subset['PO_NUMBER_UPDATE'].unique().tolist()
df_node_PO = pd.DataFrame(columns=['PO_ID'], data=list_unique_PO)
df_node_PO.head()


# In[ ]:


po_filepath = ace_data_path + 'NODE_PO.csv'
upload_to_adl_DataFrame(adl, df_node_PO, po_filepath)


# #### Shipment

# In[ ]:


list_unique_shipment = df_incoming_orders_subset['SHIPMENT_ID'].unique()
df_node_shipment = pd.DataFrame(columns=['SHIPMENT_ID'],
                                 data=list_unique_shipment)
df_node_shipment.head()


# In[ ]:


shipment_filepath = ace_data_path + 'NODE_SHIPMENT.csv'
upload_to_adl_DataFrame(adl, df_node_shipment, shipment_filepath)


# #### Consol

# In[ ]:


list_unique_consol = df_incoming_orders_subset['CONSOL_ID'].unique()
df_node_consol = pd.DataFrame(columns=['CONSOL_ID'],
                                 data=list_unique_consol)
df_node_consol.head()


# In[ ]:


consol_filepath = ace_data_path + 'NODE_CONSOL.csv'
upload_to_adl_DataFrame(adl, df_node_consol, consol_filepath)


# #### Container

# In[ ]:


list_unique_container = df_incoming_orders_subset['CONTAINER_NO'].unique(
).tolist()
df_node_container = pd.DataFrame(columns=['CONTAINER_ID'],
                                 data=list_unique_container)
df_node_container.head()


# In[ ]:


container_filepath = ace_data_path + 'NODE_CONTAINER.csv'
upload_to_adl_DataFrame(adl, df_node_container, container_filepath)


# #### Shipper

# In[ ]:


list_unique_shipper = df_incoming_orders_subset['SHIPPER_NAME'].unique(
).tolist()
df_node_shipper = pd.DataFrame(columns=['SHIPPER_ID'],
                               data=list_unique_shipper)
df_node_shipper.head()


# In[ ]:


shipper_filepath = ace_data_path + 'NODE_SHIPPER.csv'
upload_to_adl_DataFrame(adl, df_node_shipper, shipper_filepath)


# #### Carrier

# In[ ]:


list_unique_carrier = df_incoming_orders_subset['CARRIER'].unique().tolist()
df_node_carrier = pd.DataFrame(columns=['CARRIER_ID'],
                               data=list_unique_carrier)
df_node_carrier.head()


# In[ ]:


carrier_filepath = ace_data_path + 'NODE_CARRIER.csv'
upload_to_adl_DataFrame(adl, df_node_carrier, carrier_filepath)


# #### Voyage

# In[ ]:


list_unique_voyage = df_incoming_orders_subset['VOYAGE/FLIGHT'].unique().tolist()
df_node_voyage = pd.DataFrame(columns=['VOYAGE_ID'], data=list_unique_voyage)
df_node_voyage.head()

voyage_filepath = ace_data_path + 'NODE_VOYAGE.csv'
upload_to_adl_DataFrame(adl, df_node_voyage, voyage_filepath)


# #### Vessel

# In[ ]:


list_unique_vessel = df_incoming_orders_subset['VESSEL'].unique().tolist()
df_node_vessel = pd.DataFrame(columns=['VESSEL_ID'], data=list_unique_vessel)
df_node_vessel.head()


# In[ ]:


vessel_filepath = ace_data_path + 'NODE_VESSEL.csv'

upload_to_adl_DataFrame(adl, df_node_vessel, vessel_filepath)


# #### Market

# In[ ]:


list_unique_markets = list(
    set(df_incoming_orders_subset['DC_FACILITY_COUNTRY'].unique().tolist() +
        df_inventory_subset['DC_FACILITY_COUNTRY'].unique().tolist() +
        df_demand_subset['COUNTRYCODE'].unique().tolist()))


# In[ ]:


df_node_market = pd.DataFrame(columns = ['MARKET_ID'], data =list_unique_markets )


df_node_market = df_node_market.merge(
    df_country_code,
    left_on=['MARKET_ID'],
    right_on=['ISO_3166-1_3CODE'],
    how='left')

market_filepath = ace_data_path + 'NODE_MARKET.csv'

upload_to_adl_DataFrame(adl, df_node_market,
                        market_filepath)


# In[ ]:


df_node_market


# In[ ]:


df_node_market.head()


# #### SKU

# In[ ]:



list_unique_wrins = list(
    set(df_incoming_orders_subset['WRIN'].unique().tolist() +
        df_inventory_subset['WRIN'].unique().tolist() +
        df_demand_subset['WRIN'].unique().tolist()))

df_node_sku = pd.DataFrame(columns=['SKU_ID'], data=list_unique_wrins)


# In[ ]:


sku_filepath = ace_data_path + 'NODE_SKU.csv'

df_node_sku['SKU_ID'] = df_node_sku['SKU_ID'].str.upper()

df_node_sku = df_node_sku.drop_duplicates()

upload_to_adl_DataFrame(adl, df_node_sku,
                        sku_filepath)


# In[ ]:


df_node_sku


# #### SKU_Child

# In[ ]:


# df_link_sku_skuchild = df_inventory_subset_org.dropna()[['WRIN', 'WRIN_ORG']].append(
#     df_incoming_orders_subset_org.dropna()[['WRIN', 'WRIN_ORG']]).append(
#         df_demand_subset_org.dropna()[['WRIN', 'WRIN_ORG']]).drop_duplicates().reset_index(drop = True)


df_link_sku_skuchild = pd.concat([df_inventory_subset_org.dropna()[['WRIN', 'WRIN_ORG']],
           df_incoming_orders_subset_org.dropna()[['WRIN', 'WRIN_ORG']],
           df_demand_subset_org.dropna()[['WRIN', 'WRIN_ORG']]
           
           ]).drop_duplicates().reset_index(drop = True)


# In[ ]:


df_node_sku_child = pd.DataFrame(
    columns=['SKU_CHILD_ID'],data = df_link_sku_skuchild['WRIN_ORG'].unique().tolist())


# In[ ]:


sku_child_filepath = ace_data_path + 'NODE_SKU_CHILD.csv'

upload_to_adl_DataFrame(adl, df_node_sku_child,
                        sku_child_filepath)


# In[ ]:


df_node_sku_child.head()


# #### Date

# In[ ]:


#TBD


# #### Property

# In[ ]:


df_node_property = pd.DataFrame(columns=['PROPERTY_ID', 'PROPERTY_NAME'])
df_node_property['PROPERTY_ID'] = [
    'ORDER_CASES', 'INVENTORY_CASES', 'DEMAND_CASES'
]
df_node_property['PROPERTY_NAME'] = df_node_property['PROPERTY_ID']


# In[ ]:


df_node_property


# ### Link

# #### Week, Date

# In[ ]:


df_link_week_date = pd.DataFrame(columns=['DATE_ID'], data=time_span)
df_link_week_date['WEEK_ID'] = create_array_ascending(number_of_weeks, 7)

df_link_week_date_min = df_link_week_date.groupby(['WEEK_ID']).agg({
    'DATE_ID': 'min'
}).reset_index()


# In[ ]:


week_date_filepath = ace_data_path + 'LINK_WEEK_DATE.csv'
upload_to_adl_DataFrame(adl, df_link_week_date, week_date_filepath)


# #### SKU, SKU Child

# In[ ]:
df_link_sku_skuchild = df_link_sku_skuchild.merge(Link_Wrin_Type, on = 'WRIN') 
print(df_link_sku_skuchild)
df_link_sku_skuchild  = df_link_sku_skuchild.rename(columns = {
    'WRIN':'SKU_ID',
    'WRIN_ORG':'SKU_CHILD_ID'
})


sku_skuchild_filepath = ace_data_path + 'LINK_SKU_SKU-CHILD.csv'
upload_to_adl_DataFrame(adl, df_link_sku_skuchild, sku_skuchild_filepath)


# In[ ]:


df_link_sku_skuchild_pbi = df_link_sku_skuchild.groupby(
    ['SKU_ID'])['SKU_CHILD_ID'].apply(list).reset_index()
# df_link_sku_skuchild_pbi['SKU_CHILD_ID'] = df_link_sku_skuchild_pbi.apply(
#     lambda x: ", ".join(x['SKU_CHILD_ID']), axis=1)


df_link_sku_skuchild_pbi['SKU_ID'] = df_link_sku_skuchild_pbi['SKU_ID'].str.upper()

df_link_sku_skuchild_pbi['SKU_ID'] = df_link_sku_skuchild_pbi['SKU_ID'].drop_duplicates()

pbi_sku_skuchild_filepath = pbi_data_path + 'LINK_SKU_SKU-CHILD_MAP.csv'
upload_to_adl_DataFrame(adl, df_link_sku_skuchild_pbi, pbi_sku_skuchild_filepath)


# #### SKU, Category

# In[ ]:


df_link_sku_category = df_node_sku.merge(df_SIMs,
                                          left_on=['SKU_ID'],
                                          right_on=['ASSEMBLY_ITEM'],
                                          how='left').drop(columns = ['WRIN'])

df_link_sku_category = fill_in_empty_node(df_link_sku_category, [
    'PRODUCT_DESCRIPTION', 'PRODUCT_CATEGORY', 'PRODUCT_SUB-CATEGORY1',
    'PRODUCT_SUB-CATEGORY2', 'PRODUCT_SUB-CATEGORY3', 'ASSEMBLY_ITEM'
], [
    'NO PRODUCT DESCRIPTION', 'NO PRODUCT CATEGORY',
    'NO PRODUCT SUB-CATEGORY1', 'NO PRODUCT SUB-CATEGORY2',
    'NOO PRODUCT SUB-CATEGORY3', 'NO ASSEMBLY ITEM'
])


# In[ ]:


df_link_sku_category = df_link_sku_category.rename(columns = {
    'PRODUCT_DESCRIPTION':'PRODUCT_DESCRIPTION',
    'PRODUCT_CATEGORY':'PRODUCT_CATEGORY_ID',
    'PRODUCT_SUB-CATEGORY1':'PRODUCT_SUBCATEGORY1_ID',
    'PRODUCT_SUB-CATEGORY2':'PRODUCT_SUBCATEGORY2_ID',
    'PRODUCT_SUB-CATEGORY3':'PRODUCT_SUBCATEGORY3_ID',
    'ASSEMBLY_ITEM':'ASSEMBLY_ITEM_ID'})


# In[ ]:


df_link_sku_category.head()


# In[ ]:


sku_category_filepath = ace_data_path + 'LINK_SKU_CATEGORY.csv'

upload_to_adl_DataFrame(adl, df_link_sku_category,
                        sku_category_filepath)


# #### Shipment Consol Container PO Carrier Vessel Voyage Shipper Market SKU SKUchild Date

# In[43]:


df_incoming_orders_subset_org_merge.columns


# In[ ]:


df_incoming_orders_subset_org_merge


# In[ ]:

df_incoming_orders_subset_org_merge.columns
df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date = df_incoming_orders_subset_org_merge.copy(
)
df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date = df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date.rename(
    columns={
        'PO_NUMBER_UPDATE': 'PO_ID',
        'SHIPMENT_ID': 'SHIPMENT_ID',
        'CONTAINER_NO': 'CONTAINER_ID',
        'CONSOL_ID': 'CONSOL_ID',
        'DC_FACILITY_COUNTRY': 'MARKET_ID',
        'WRIN': 'SKU_ID',
        'WRIN_ORG': 'SKU_CHILD_ID',
        'SELCTED_ETA': 'DATE_ID',
        'CARRIER': 'CARRIER_ID',
        'VESSEL': 'VESSEL_ID',
        'VOYAGE/FLIGHT': 'VOYAGE_ID',
        'SHIPPER_NAME': 'SHIPPER_ID'
    })

df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date.head(
)
df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date.columns


# df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date.to_csv("tsc.csv")


# In[ ]:


evaluate_duplicates_exisit(df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date)


# In[ ]:


shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date_filepath = ace_data_path + 'LINK_SHIPMENT_CONSOL_CONTAINER_PO_CARRIER_VESSEL_VOYAGE_SHIPPER_MARKET_SKU_SKUCHILD_DATE.csv'

upload_to_adl_DataFrame(adl, df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date,
                        shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_skuchild_date_filepath)


# #### Shipment Consol Container PO Carrier Vessel Voyage Shipper Market SKU Date

# In[ ]:


df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date = df_incoming_orders_subset.copy()
df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date = df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date.rename(
    columns={
        'PO_NUMBER_UPDATE': 'PO_ID',
        'SHIPMENT_ID': 'SHIPMENT_ID',
        'CONTAINER_NO': 'CONTAINER_ID',
        'CONSOL_ID': 'CONSOL_ID',
        'DC_FACILITY_COUNTRY': 'MARKET_ID',
        'WRIN': 'SKU_ID',
        'SELCTED_ETA': 'DATE_ID',
        'CARRIER': 'CARRIER_ID',
        'VESSEL': 'VESSEL_ID',
        'VOYAGE/FLIGHT': 'VOYAGE_ID',
        'SHIPPER_NAME': 'SHIPPER_ID'
    })
df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date.columns
df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date.head(
)


# In[ ]:


evaluate_duplicates_exisit(df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date)


# In[ ]:


shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date_filepath = ace_data_path + 'LINK_SHIPMENT_CONSOL_CONTAINER_PO_CARRIER_VESSEL_VOYAGE_SHIPPER_MARKET_SKU_DATE.csv'

upload_to_adl_DataFrame(adl, df_shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date,
                        shipment_consol_container_po_carrier_vessel_voyage_shipper_market_sku_date_filepath)


# #### Market, SKU, Year, Month, Day

# In[ ]:


# df_incoming_orders_ace = df_incoming_orders_subset.rename(
#     columns={
#         'DC_FACILITY_COUNTRY': 'MARKET_ID',
#         'WRIN': 'SKU_ID',
#         'SELCTED_ETA': 'DATE',
#         'ALLOCATED_CASES': 'VALUE'
#     })

# df_incoming_orders_ace['PROPERTY_ID'] = 'ORDER_CASES'
# df_incoming_orders_ace = df_incoming_orders_ace[[
#     'MARKET_ID', 'SKU_ID', 'DATE', 'PROPERTY_ID', 'VALUE'
# ]]


# In[ ]:

df_inventory_subset['INVENTORY_DATE'] = df_inventory_subset['INVENTORY_DATE'].astype(str)
df_inventory_ace = df_inventory_subset.rename(
    columns={
        'DC_FACILITY_COUNTRY': 'MARKET_ID',
        'WRIN': 'SKU_ID',
        'INVENTORY_DATE': 'DATE',
        'INVENTORY_CASES': 'VALUE'
    })

df_inventory_ace['PROPERTY_ID'] = 'INVENTORY_CASES'


# In[ ]:


df_demand_ace = df_demand_subset.rename(
    columns={
        'COUNTRYCODE': 'MARKET_ID',
        'WRIN': 'SKU_ID',
        'DATE': 'DATE',
        'DAILY_FORECASTINCASES': 'VALUE'
    })

df_demand_ace['PROPERTY_ID'] = 'DEMAND_CASES'


# In[ ]:


df_link_market_sku_year_month_day = append_DataFrames(
    [df_inventory_ace, df_demand_ace]).reset_index(drop=True)

df_link_market_sku_year_month_day = df_link_market_sku_year_month_day.rename(
    columns={
        'MARKET_ID': 'MARKET_ID',
        'SKU_ID': 'SKU_ID',
        'DATE': 'DATE_ID'
    })


# In[ ]:


evaluate_duplicates_exisit(df_link_market_sku_year_month_day)


# In[ ]:


df_link_market_sku_year_month_day


# In[ ]:


market_sku_year_month_day_filepath = ace_data_path + 'LINK_MARKET_SKU_YEAR_MONTH_DAY.csv'

upload_to_adl_DataFrame(adl, df_link_market_sku_year_month_day,
                        market_sku_year_month_day_filepath)


# #### Market, SKU, Year, Week

# In[ ]:

df_link_week_date['DATE_ID'] = df_link_week_date['DATE_ID'].astype(str)    

df_link_market_sku_year_month_day['DATE_ID'] = df_link_market_sku_year_month_day['DATE_ID'].astype(str)    

df_link_market_sku_week = df_link_market_sku_year_month_day.merge(df_link_week_date,
                                                                  on='DATE_ID',
                                                                  how='left')

df_link_market_sku_week = df_link_market_sku_week.groupby(
    ['MARKET_ID', 'SKU_ID', 'WEEK_ID', 'PROPERTY_ID']).agg({
        'VALUE': 'sum'
    }).reset_index()

df_link_market_sku_week['WEEK_ID'] = [int(i) for i in df_link_market_sku_week['WEEK_ID']]


# In[ ]:


market_sku_week_filepath = ace_data_path + 'LINK_MARKET_SKU_WEEK.csv'

upload_to_adl_DataFrame(adl, df_link_market_sku_week,
                        market_sku_week_filepath)


# #### Market, SKU, PO, Date

# In[ ]:

df_incoming_orders_subset['SELCTED_ETA'] = df_incoming_orders_subset['SELCTED_ETA'].astype(str)
df_link_po_sku_market_date = df_incoming_orders_subset[[
    'WRIN', 'DC_FACILITY_COUNTRY', 'PO_NUMBER_UPDATE', 'SELCTED_ETA',
    'ALLOCATED_CASES'
]].drop_duplicates().reset_index(drop=True).rename(
    columns={
        'WRIN': 'SKU_ID',
        'DC_FACILITY_COUNTRY': 'MARKET_ID',
        'PO_NUMBER_UPDATE': 'PO_ID',
        'SELCTED_ETA': 'DATE_ID',
        'ALLOCATED_CASES': 'VALUE'
    })

df_link_po_sku_market_date['PROPERTY_ID'] = 'ORDER_CASES'
df_link_po_sku_market_date.head()


# In[ ]:


market_sku_po_year_month_day_filepath = ace_data_path + 'LINK_MARKET_SKU_PO_YEAR_MONTH_DAY.csv'

upload_to_adl_DataFrame(adl, df_link_po_sku_market_date,
                        market_sku_po_year_month_day_filepath)


# #### Market, SKU, PO, Week

# In[ ]:


df_link_market_sku_po_week = df_link_po_sku_market_date.merge(
    df_link_week_date, on=['DATE_ID'], how='left').reset_index(drop=True)

df_link_market_sku_po_week = df_link_market_sku_po_week.groupby(
    ['MARKET_ID', 'SKU_ID', 'PO_ID', 'WEEK_ID', 'PROPERTY_ID']).agg({
        'VALUE':
        'sum'
    }).reset_index()


df_link_market_sku_po_week['WEEK_ID'] = [int(i) for i in df_link_market_sku_po_week['WEEK_ID']]


# In[ ]:


market_sku_po_week_filepath = ace_data_path + 'LINK_MARKET_SKU_PO_WEEK.csv'

upload_to_adl_DataFrame(adl, df_link_market_sku_po_week,
                        market_sku_po_week_filepath)


# ### Link Archive

# #### Shipment, Consol, Container, PO, Market, SKU, Date

# In[ ]:


# df_shipment_consol_container_po_market_sku_date = df_incoming_orders_subset[[
#     'SHIPMENT_ID', 'CONSOL_ID', 'CONTAINER_NO', 'PO_NUMBER_UPDATE', 'DC_FACILITY_COUNTRY', 'WRIN',
#     'SELCTED_ETA', 'ALLOCATED_CASES'
# ]]

# print('Any Duplicates? %s' %str(evaluate_duplicates_exisit(df_shipment_consol_container_po_market_sku_date)))

# df_shipment_consol_container_po_market_sku_date = df_shipment_consol_container_po_market_sku_date.drop_duplicates(
# ).reset_index(drop=True)


# df_shipment_consol_container_po_market_sku_date = df_shipment_consol_container_po_market_sku_date.rename(
#     columns={
#         'PO_NUMBER_UPDATE': 'PO_ID',
#         'SHIPMENT_ID': 'SHIPMENT_ID',
#         'CONTAINER_NO': 'CONTAINER_ID',
#         'CONSOL_ID':'CONSOL_ID',
#         'DC_FACILITY_COUNTRY':'MARKET_ID',
#         'WRIN':'SKU_ID', 
#         'SELCTED_ETA':'DATE_ID'
#     })

# df_shipment_consol_container_po_market_sku_date.head()


# In[ ]:


# shipment_consol_container_po_market_sku_date_filepath = ace_data_path + 'LINK_SHIPMENT_CONSOL_CONTAINER_PO_MARKET_SKU_DATE.csv'

# upload_to_adl_DataFrame(adl,
#                         df_shipment_consol_container_po_market_sku_date,
#                         shipment_consol_container_po_market_sku_date_filepath)


# #### Shipment, Consol, Container, PO

# In[ ]:


# df_link_shipment_consol_container_po = df_incoming_orders_subset[
#     [
#         'SHIPMENT_ID', 'CONSOL_ID', 'CONTAINER_NO', 'PO_NUMBER_UPDATE'
#     ]]

# df_link_shipment_consol_container_po = df_link_shipment_consol_container_po.drop_duplicates(
# ).reset_index(drop=True)

# df_link_shipment_consol_container_po = df_link_shipment_consol_container_po.rename(
#     columns={
#         'PO_NUMBER_UPDATE': 'PO_ID',
#         'SHIPMENT_ID': 'SHIPMENT_ID',
#         'CONTAINER_NO': 'CONTAINER_ID',
#         'CONSOL_ID':'CONSOL_ID'
#     })

# df_link_shipment_consol_container_po.head()


# In[ ]:


# shipment_consol_container_po_filepath = ace_data_path + 'LINK_SHIPMENT_CONSOL_CONTAINER_PO.csv'

# upload_to_adl_DataFrame(adl,
#                         df_link_shipment_consol_container_po,
#                         shipment_consol_container_po_filepath)


# #### PO, Carrier, Vessel, Voyage, Shipper

# In[ ]:


# df_link_po_carrier_vessel_voyage_shipper = df_incoming_orders_subset[
#     [
#         'PO_NUMBER_UPDATE',
#         'CARRIER', 'VESSEL', 'VOYAGE/FLIGHT',
#        'SHIPPER_NAME'
#     ]]

# df_link_po_carrier_vessel_voyage_shipper = df_link_po_carrier_vessel_voyage_shipper.drop_duplicates(
# ).reset_index(drop=True)

# df_link_po_carrier_vessel_voyage_shipper = df_link_po_carrier_vessel_voyage_shipper.rename(
#     columns={
#         'PO_NUMBER_UPDATE': 'PO_ID',
#         'CARRIER': 'CARRIER_ID',
#         'VESSEL': 'VESSEL_ID',
#         'VOYAGE/FLIGHT':'VOYAGE_ID',
#         'SHIPPER_NAME': 'SHIPPER_ID'
#     })

# df_link_po_carrier_vessel_voyage_shipper.head()


# In[ ]:


# po_carrier_vessel_voyage_shipper_filepath = ace_data_path + 'LINK_CARRIER_VESSEL_VOYAGE_SHIPPER_PO.csv'

# upload_to_adl_DataFrame(
#     adl, df_link_po_carrier_vessel_voyage_shipper,
#     po_carrier_vessel_voyage_shipper_filepath)


# #### Shipment, Consol, Container, Carrier, Vessel, Voyage, Shipper

# In[ ]:


# df_link_shipment_consol_container_carrier_vessel_voyage_shipper = df_incoming_orders_subset[
#     [
#         'SHIPMENT_ID', 'CONSOL_ID', 'CONTAINER_NO', 'CARRIER', 'VESSEL',
#         'VOYAGE/FLIGHT', 'SHIPPER_NAME'
#     ]]

# df_link_shipment_consol_container_carrier_vessel_voyage_shipper = df_link_shipment_consol_container_carrier_vessel_voyage_shipper.drop_duplicates(
# ).reset_index(drop=True)

# df_link_shipment_consol_container_carrier_vessel_voyage_shipper = df_link_shipment_consol_container_carrier_vessel_voyage_shipper.rename(
#     columns={
#         'SHIPMENT_ID': 'SHIPMENT_ID',
#         'CONSOL_ID':'CONSOL_ID',
#         'CONTAINER_NO':'CONTAINER_ID',
#         'CARRIER': 'CARRIER_ID',
#         'VESSEL': 'VESSEL_ID',
#         'VOYAGE/FLIGHT':'VOYAGE_ID',
#         'SHIPPER_NAME': 'SHIPPER_ID'
#     })

# df_link_shipment_consol_container_carrier_vessel_voyage_shipper.head()


# In[ ]:


# shipment_consol_container_carrier_vessel_voyage_shipper_filepath = ace_data_path + 'LINK_SHIPMENT_CONSOL_CONTAINER_CARRIER_VESSEL_VOYAGE_SHIPPER.csv'

# upload_to_adl_DataFrame(
#     adl, df_link_shipment_consol_container_carrier_vessel_voyage_shipper,
#     shipment_consol_container_carrier_vessel_voyage_shipper_filepath)


# #### PO, Shipment, Carrier, Vessel, Container, Shipper

# In[ ]:


# df_link_po_shipment_carrier_vessel_container_shipper = df_incoming_orders_subset[
#     [
#         'PO_NUMBER_UPDATE', 'SHIPMENT_ID', 'CARRIER', 'VESSEL',
#         'VOYAGE/FLIGHT', 'CONTAINER_NO', 'SHIPPER_NAME'
#     ]]

# df_link_po_shipment_carrier_vessel_container_shipper = df_link_po_shipment_carrier_vessel_container_shipper.drop_duplicates(
# ).reset_index(drop=True)

# df_link_po_shipment_carrier_vessel_container_shipper = df_link_po_shipment_carrier_vessel_container_shipper.rename(
#     columns={
#         'PO_NUMBER_UPDATE': 'PO_ID',
#         'SHIPMENT_ID': 'SHIPMENT_ID',
#         'CARRIER': 'CARRIER_ID',
#         'VESSEL': 'VESSEL_ID',
#         'CONTAINER_NO': 'CONTAINER_ID',
#         'SHIPPER_NAME': 'SHIPPER_ID'
#     })

# df_link_po_shipment_carrier_vessel_container_shipper.head()

# In[ ]:


# po_shipment_carrier_vessel_container_shipper_filepath = ace_data_path + 'LINK_PO_SHIPMENT_CARRIER_VESSEL_CONTAINER_SHIPPER.csv'

# upload_to_adl_DataFrame(adl, dfship_link_po_shipment_carrier_vessel_container_shipper,
#                         po_shipment_carrier_vessel_container_shipper_filepath)


# #### Market, SKU, PO

# In[ ]:


# df_link_PO_SKU_Market = df_incoming_orders_subset[[
#     'WRIN', 'DC_FACILITY_COUNTRY', 'PO_NUMBER_UPDATE'
# ]].drop_duplicates().reset_index(drop=True).rename(
#     columns={
#         'WRIN': 'SKU_ID',
#         'DC_FACILITY_COUNTRY': 'MARKET_ID',a
#         'PO_NUMBER_UPDATE': 'PO_ID'
#     })

# df_link_PO_SKU_Market.head()


# In[ ]:


# market_sku_po_filepath = ace_data_path + 'LINK_MARKET_SKU_PO.csv'

# upload_to_adl_DataFrame(adl, df_link_PO_SKU_Market,
#                         market_sku_po_filepath)


# In[ ]:


from datetime import datetime
today = datetime.now()
print("Last Run Date:", today)


# df_Matching_PO_Stats.columns
# df_Matching_PO_Stats.drop_duplicates(subset = ['PO_NUMBER'],inplace = True)




# # Total_PO  = df_Matching_PO_Stats.

# df_Matching_PO_Stats.groupby(['CUSTOMER','POD_COUNTRY'])['PO_NUMBER'].size()






















