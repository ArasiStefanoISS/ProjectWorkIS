import pandas as pd

df = pd.read_csv('./Dataset_2.csv', encoding='ISO-8859-1')


#Expected RAL elaboration


valid_ral = df[df['Expected Ral'].notna()].drop_duplicates(subset='ID', keep='last')

ral_dict = dict(zip(valid_ral['ID'], valid_ral['Expected Ral']))

# Fill function
def fill_expected_ral_from_dict(df, ral_dict): 
    df_filled = df.copy()
    df_filled['Expected Ral'] = df_filled['ID'].map(ral_dict)
    return df_filled

df_filled = fill_expected_ral_from_dict(df, ral_dict)

df_filled['Expected Ral'] = df_filled['ID'].map(ral_dict).fillna("Not Given")






#Duplicates
df_nodup = df_filled.drop_duplicates(subset='ID', keep='last')





#Unuseful Columns

#added spaces and changed some capital letters
columns_to_drop = ['ID', ' Last Role', ' Year of insertion', ' Assumption Headquarters', ' linked_search__key', ' Akkodis headquarters']

df_no_useless = df_nodup.drop(columns=columns_to_drop)

#print(df_no_useless)

# Keep only columns with at least 40% non-null values
df_no_low_data = df_no_useless.loc[:, df_no_useless.notna().mean() >= 0.4]

#print(df_no_low_data)



#NaNs Handling
df_no_low_data[' Residence'] = df_no_low_data[' Residence'].fillna('Not Specified')

df_no_low_data[' Study area'] = df_no_low_data[' Study area'].fillna('Not Specified')

df_no_low_data[' Sector'] = df_no_low_data[' Sector'].fillna('Not Specified')

df_no_low_data[' event_type__val'] = df_no_low_data[' event_type__val'].fillna('Not Specified')


#print(df_no_low_data)


#df_no_low_data.to_csv('cleaned_data_2.csv', index=False)





#Feature Mapping

state_list= ['ALBANIA', 'ALGERIA', 'AUSTRIA', 'BELARUS', 'BELGIUM', 'BRAZIL', 'BULGARIA', 'CHILE', "CHINA PEOPLE'S REPUBLIC", 'COLOMBIA', 'CROATIA', 'CZECH REPUBLIC', 'EGYPT', 'ERITREA', 'FRANCE', 'GERMANY', 'GREAT BRITAIN-NORTHERN IRELAND', 'GREECE', 'GRENADA', 'HAITI', 'INDIA', 'INDONESIA', 'IRAN', 'ITALY', 'KUWAIT', 'LEBANON', 'LIBYA', 'LITHUANIA', 'MALAYSIA', 'MALTA', 'MEXICO', 'MONACO', 'MOROCCO', 'NETHERLANDS', 'NIGERIA', 'OMAN', 'PAKISTAN', 'PHILIPPINES', 'PORTUGAL', 'QATAR', 'REPUBLIC OF POLAND', 'ROMANIA', 'RUSSIAN FEDERATION', 'SAINT LUCIA', 'SAINT PIERRE ET MIQUELON (ISLANDS)', 'SAN MARINO', 'SERBIA AND MONTENEGRO', 'SINGAPORE', 'SLOVAKIA', 'SOUTH AFRICAN REPUBLIC', 'SPAIN', 'SRI LANKA', 'SWEDEN', 'SWITZERLAND', 'SYRIA', 'TONGA', 'TUNISIA', 'Türkiye', 'UKRAINE', 'UNITED ARAB EMIRATES', 'UNITED STATES OF AMERICA', 'USSR', 'UZBEKISTAN', 'VENEZUELA', 'YUGOSLAVIA']

italy_list= ['Abruzzo', 'Aosta Valley', 'Basilicata', 'Calabria', 'Campania', 'Emilia Romagna', 'Friuli Venezia Giulia', 'Lazio', 'Liguria', 'Lombardy', 'Marche', 'Molise', 'Not Specified', 'Piedmont', 'Puglia', 'Sardinia', 'Sicily', 'Trentino Alto Adige', 'Tuscany', 'Umbria', 'Veneto']

def map_residence(value):
    for region in italy_list:
        if region in value:
          return region
    for state in state_list:
        if state in value:
          return state
    return 'Not Specified'


df_no_low_data[' Residence'] = df_no_low_data[' Residence'].apply(map_residence)
df_no_low_data[' Residence'] = df_no_low_data[' Residence'].replace('Türkiye', 'TURKEY')
df_no_low_data[' Residence'] = df_no_low_data[' Residence'].replace('USSR', 'RUSSIAN FEDERATION')

#df_no_low_data.to_csv('cleaned_data_2.csv', index=False)

def getState(value):
    for region in italy_list:
        if region in value:
            return 'ITALY'
    for state in state_list:
        if state in value:
            return state
    return 'Not Specified'


def getItalianRegion(value):
    for region in italy_list:
        if region in value:
          return region
    return 'Not Italian Region'


df_no_low_data[' Residence State']=df_no_low_data[' Residence'].apply(getState)
df_no_low_data[' Residence Italian Region']=df_no_low_data[' Residence'].apply(getItalianRegion)

european_countries = [
    'ALBANIA', 'AUSTRIA', 'BELARUS', 'BELGIUM', 'BULGARIA', 'CROATIA', 'CZECH REPUBLIC',
    'FRANCE', 'GERMANY', 'GREAT BRITAIN-NORTHERN IRELAND', 'GREECE', 'ITALY', 'LATVIA',
    'LITHUANIA', 'LUXEMBOURG', 'MALTA', 'MOLDOVA', 'MONACO', 'MONTENEGRO', 'NETHERLANDS',
    'NORWAY', 'POLAND', 'PORTUGAL', 'ROMANIA', 'RUSSIA', 'SAN MARINO', 'SERBIA', 'SLOVAKIA',
    'SLOVENIA', 'SPAIN', 'SWEDEN', 'SWITZERLAND', 'UKRAINE'
]
df_no_low_data[' European Residence'] = df_no_low_data[' Residence State'].apply(lambda x: 'Yes' if x in european_countries else 'No')

df_no_low_data = df_no_low_data.drop(columns=[' Residence'])

#print(df_no_low_data)

for column in df_no_low_data.columns:
            array = df_no_low_data[column].unique()
            print(f"Column {column}: {array}")

old_age_ranges=['< 20 years', '20 - 25 years', '26 - 30 years', '31 - 35 years', '36 - 40 years', '40 - 45 years', '> 45 years']
new_age_ranges=["less than 20 years","early 20s","late 20s","early 30s","late 30s","early 40s","more than 45 years"]

old_years_experience=["[0]","[0-1]","[1-3]","[3-5]","[5-7]","[7-10]","[+10]"]
new_years_experience=["none","between 0 and 1","between 1 and 3","between 3 and 5","between 5 and 7","between 7 and 10","more than 10"]

age_mapping = dict(zip(old_age_ranges, new_age_ranges))
years_mapping = dict(zip(old_years_experience, new_years_experience))


df_years_clean=df_no_low_data
df_years_clean[' Age Range']=df_years_clean[' Age Range'].map(age_mapping).tolist()
df_years_clean[' Years Experience']=df_years_clean[' Years Experience'].map(years_mapping).tolist()

#print(df_years_clean[' Age Range'],df_years_clean[' Years Experience'])

df_years_clean.to_csv('cleaned_data_2.csv', index=False)