#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

sqm = pd.read_csv('C:/Users/zacharias/Desktop/Glyfada_sqm.csv')
energy = pd.read_csv('C:/Users/zacharias/Desktop/Glyfada_energy.csv')
age = pd.read_csv('C:/Users/zacharias/Desktop/Glyfada_age.csv')


# In[2]:


col_rename_dict = {'-49': '0-49',
                   ' 50-  74': '50-74',
                   ' 75- 99': '75-99',
                   '100-124': '100-124',
                   '125-149': '125-149',
                   '150-174': '150-174',
                   '175-199': '175-199',
                   '200-224': '200-224',
                   '225-249': '225-249',
                   '250-274': '250-274',
                   '275-299': '275-299',
                   '300+': '300+'}

# rename the columns using the dictionary
sqm = sqm.rename(columns=col_rename_dict)


# In[3]:


sqm['code'] = sqm['Γεωγραφικός κωδικός'].astype(str) + '-' + sqm['Οικοδομικό τετράγωνο'].astype(str)


# In[4]:


new_sqm = sqm.groupby('code').agg({'Αριθμός δωματίων': 'sum'}).reset_index()


# In[5]:


ranges = ['0-49', '50-74', '75-99', '100-124', '125-149',
       '150-174', '175-199', '200-224', '225-249', '250-274', '275-299',
       '300+']
for r in ranges:
    new_sqm[r] = sqm.groupby('code')[r].sum().reset_index()[r]


# In[6]:


# split the 'code' column into two separate columns based on the hyphen
new_sqm[['geo_code', 'square_code']] = new_sqm['code'].str.split('-', expand=True)

# convert the 'square_code' column to integer data type
new_sqm['square_code'] = new_sqm['square_code'].astype(int)

# sort the dataframe based on the 'square_code' column
new_sqm = new_sqm.sort_values('square_code')

# concatenate the 'geo_code' and 'square_code' columns back into the 'code' column
new_sqm['code'] = new_sqm['geo_code'] + '-' + new_sqm['square_code'].astype(str)

# drop the 'geo_code' and 'square_code' columns
new_sqm = new_sqm.drop(['geo_code', 'square_code'], axis=1)

# reset the index of the dataframe
new_sqm = new_sqm.reset_index(drop=True)


# In[7]:


# Define the ranges and their midpoints (except for 300+)
ranges = ['0-49', '50-74', '75-99', '100-124', '125-149', '150-174', '175-199', '200-224', '225-249', '250-274', '275-299', '300+']
midpoints = [24.5, 62, 87, 112, 137, 162, 187, 212, 237, 262, 287, 300]

# Calculate the weighted sum for each area code
def weighted_sum(row):
    return sum([row[range_str] * midpoint for range_str, midpoint in zip(ranges, midpoints)])

new_sqm['weighted_sum'] = new_sqm.apply(weighted_sum, axis=1)

# Calculate the weighted average for each area code using the weighted sum and total apartments
new_sqm['weighted_average_sqm'] = new_sqm['weighted_sum'] / new_sqm['Αριθμός δωματίων']


# In[8]:


new_sqm["weighted_sum"] = new_sqm["weighted_sum"].round().astype(int)
new_sqm["weighted_average_sqm"] = new_sqm["weighted_average_sqm"].round().astype(int)


# In[11]:


def calculate_energy_scores(energy):
    energy_sources = {
        'Ηλεκτρισμός': 1 * 10/6,
        'Πετρέλαιο': 2 * 10/6,
        'Φυσικό αέριο': 3 * 10/6,
        'Άλλη': 4 * 10/6,
        'Βιομάζα': 5 * 10/6,
        'Ηλιακή ενέργεια': 6 * 10/6
    }

    weights = {
        'Θέρμανση': 6.98,
        'Ζεστό νερό': 1.84,
        'Μαγείρεμα': 1.18
    }

    def category_score(row, category_prefix):
        total_residences = 0
        weighted_sum = 0
        for energy_source, score in energy_sources.items():
            column = f'{energy_source} {category_prefix}'
            weighted_sum += row[column] * score
            total_residences += row[column]
        
        if total_residences == 0:
            return None
        return weighted_sum / total_residences

    energy['Θέρμανση_score'] = energy.apply(lambda row: category_score(row, 'Θέρμανση'), axis=1)
    energy['Ζεστό νερό_score'] = energy.apply(lambda row: category_score(row, 'Ζεστό νερό'), axis=1)
    energy['Μαγείρεμα_score'] = energy.apply(lambda row: category_score(row, 'Μαγείρεμα'), axis=1)

    energy['total_score'] = (
        energy['Θέρμανση_score'] * weights['Θέρμανση'] +
        energy['Ζεστό νερό_score'] * weights['Ζεστό νερό'] +
        energy['Μαγείρεμα_score'] * weights['Μαγείρεμα']
    ) / sum(weights.values())

    return energy


# In[12]:


calculate_energy_scores(energy)


# In[32]:


def calculate_energy_upgrade_cost(energy):
    energy['energy_upgrade_cost'] = (
        energy['Ηλεκτρισμός Θέρμανση'] +
        energy['Φυσικό αέριο Θέρμανση'] +
        energy['Πετρέλαιο Θέρμανση']
    ) * 12500
    return energy


# In[33]:


energy = calculate_energy_upgrade_cost(energy)


# In[34]:


energy['code'] = energy['Γεωγραφικός κωδικός'].astype(str) + '-' + energy['Οικοδομικό τετράγωνο'].astype(str)


# In[35]:


# Create a dictionary for the age bucket weights
age_bucket_weights = {
    'Προ του 1919': 1,
    '1919 - 1945': 2,
    '1946 -1960': 3,
    '1961 - 1970': 4,
    ' 1971 - 1980 ': 5,
    '1981 - 1985 ': 6,
    '1986 - 1990': 7,
    '1991 - 1995': 8,
    '1996 -2000': 9,
    '2001 - 2005': 10,
    '2006 και μετά': 11,
    'Υπό κατασκευή': 12
}

# Define a function to calculate the weighted age score
def calculate_age_score(row):
    total_buildings = row['Σύνολο κτιρίων']
    weighted_sum = 0
    for age_bucket, weight in age_bucket_weights.items():
        weighted_sum += row[age_bucket] * weight
    age_score = (weighted_sum / total_buildings) * (10 / 12) # Scaling to range 1-10
    return age_score

# Apply the function to each row of the dataframe
age['age_score'] = age.apply(calculate_age_score, axis=1)


# In[36]:


# Create a dictionary for the average age of each bucket
average_age_buckets = {
    'Προ του 1919': 1919,
    '1919 - 1945': (1919 + 1945) / 2,
    '1946 -1960': (1946 + 1960) / 2,
    '1961 - 1970': (1961 + 1970) / 2,
    ' 1971 - 1980 ': (1971 + 1980) / 2,
    '1981 - 1985 ': (1981 + 1985) / 2,
    '1986 - 1990': (1986 + 1990) / 2,
    '1991 - 1995': (1991 + 1995) / 2,
    '1996 -2000': (1996 + 2000) / 2,
    '2001 - 2005': (2001 + 2005) / 2,
    '2006 και μετά': (2006 + 2023) / 2,
    'Υπό κατασκευή': 2023
}

# Define a function to calculate the weighted average age
def calculate_average_age(row):
    total_buildings = row['Σύνολο κτιρίων']
    weighted_sum = 0
    for age_bucket, average_age in average_age_buckets.items():
        weighted_sum += row[age_bucket] * average_age
    avg_age = weighted_sum / total_buildings
    return avg_age

# Apply the function to each row of the dataframe
age['average_age'] = age.apply(calculate_average_age, axis=1)


# In[37]:


age['code'] = age['Γεωγραφικός κωδικός'].astype(str) + '-' + age['Οικοδομικό τετράγωνο'].astype(str)


# In[38]:


# merge sqm and energy on the common column(s)
merged_df = pd.merge(new_sqm, energy, on=['code', 'code'])

# merge the merged_df and age on the common column(s)
new_df = pd.merge(merged_df, age, on=['code', 'code'])

# print the new dataframe
print(new_df)


# In[39]:


# select the columns to keep and rename them
datathon = new_df.loc[:, ['code', 'Αριθμός δωματίων', 'weighted_sum', 'weighted_average_sqm', 'Γεωγραφικός κωδικός_x', 'Περιγραφή_x', 'Οικοδομικό τετράγωνο_x', 'total_score', 'energy_upgrade_cost', 'age_score', 'average_age']]
datathon = datathon.rename(columns={'Αριθμός δωματίων': 'Αριθμός κατοικιών', 'weighted_sum': 'Αθροισμα τετραγωνικών', 'weighted_average_sqm': 'Μέσος όρος τετραγωνικών μέτρων', 'Γεωγραφικός κωδικός_x': 'Γεωγραφικός κωδικός', 'Περιγραφή_x': 'Περιγραφή', 'Οικοδομικό τετράγωνο_x': 'Οικοδομικό τετράγωνο', 'total_score': 'Ενεργειακό σκορ', 'energy_upgrade_cost': 'Κόστος ενεργειακής αναβάθμισης', 'age_score': 'Σκορ έτους κατασκευής', 'average_age': 'Μέσος όρος έτους κατασκευής'})


# In[40]:


# select the columns in the desired order
datathon = datathon.loc[:, ['code', 'Γεωγραφικός κωδικός', 'Περιγραφή', 'Οικοδομικό τετράγωνο', 'Αριθμός κατοικιών', 'Αθροισμα τετραγωνικών', 'Μέσος όρος τετραγωνικών μέτρων', 'Ενεργειακό σκορ', 'Κόστος ενεργειακής αναβάθμισης', 'Σκορ έτους κατασκευής', 'Μέσος όρος έτους κατασκευής']]


# In[41]:


cooking = pd.read_csv('C:/Users/zacharias/Desktop/cooking_join.csv')

# get the number of rows in each dataframe
datathon_rows = len(datathon)
cooking_rows = len(cooking)

# set the number of rows to merge as the minimum of the two dataframes
n_rows = min(datathon_rows, cooking_rows)

# randomly shuffle the datathon dataframe
datathon = datathon.sample(frac=1).reset_index(drop=True)

# merge the two dataframes on the common columns
merged = pd.concat([cooking.iloc[:n_rows], datathon.iloc[:n_rows][['Αριθμός κατοικιών', 'Αθροισμα τετραγωνικών', 'Μέσος όρος τετραγωνικών μέτρων', 'Ενεργειακό σκορ', 'Κόστος ενεργειακής αναβάθμισης', 'Σκορ έτους κατασκευής', 'Μέσος όρος έτους κατασκευής']]], axis=1)

# calculate the average values for the columns in datathon that were not merged
averages = datathon.iloc[:n_rows][['Αριθμός κατοικιών', 'Αθροισμα τετραγωνικών', 'Μέσος όρος τετραγωνικών μέτρων', 'Ενεργειακό σκορ', 'Κόστος ενεργειακής αναβάθμισης', 'Σκορ έτους κατασκευής', 'Μέσος όρος έτους κατασκευής']].mean()

# add the average values as a new row to the merged dataframe for any remaining rows in cooking
if cooking_rows > n_rows:
    for i in range(n_rows, cooking_rows):
        merged.loc[i] = [np.nan] * len(merged.columns)
        merged.iloc[i]['Αριθμός κατοικιών'] = averages['Αριθμός κατοικιών']
        merged.iloc[i]['Αθροισμα τετραγωνικών'] = averages['Αθροισμα τετραγωνικών']
        merged.iloc[i]['Μέσος όρος τετραγωνικών μέτρων'] = averages['Μέσος όρος τετραγωνικών μέτρων']
merged.iloc[i]['Ενεργειακό σκορ'] = averages['Ενεργειακό σκορ']
merged.iloc[i]['Κόστος ενεργειακής αναβάθμισης'] = averages['Κόστος ενεργειακής αναβάθμισης']
merged.iloc[i]['Σκορ έτους κατασκευής'] = averages['Σκορ έτους κατασκευής']
merged.iloc[i]['Μέσος όρος έτους κατασκευής'] = averages['Μέσος όρος έτους κατασκευής']


# In[42]:


merged.dropna(inplace=True)


# In[43]:


index = pd.read_csv('C:/Users/zacharias/Desktop/Index_apts_athens.csv')

index_q4_2021 = index[(index['Reference_quarter'] == 4) & (index['Reference_year'] == 2021)]
index_q4_2022 = index[(index['Reference_quarter'] == 4) & (index['Reference_year'] == 2022)]

index_2021 = index_q4_2021['New_index_of_apartment_prices_by_geographical_area_Athens'].values[0]
index_2022 = index_q4_2022['New_index_of_apartment_prices_by_geographical_area_Athens'].values[0]

percentage_difference = (index_2022 - index_2021) / index_2021

merged['Value_q4_2022'] = merged['Value'] * (1 + percentage_difference)


# In[44]:


# Calculate the "Αξία τετραγώνου" column
merged["Αξία τετραγώνου"] = merged["Value_q4_2022"] * merged["Αθροισμα τετραγωνικών"]

# Calculate the "Μέσος όρος αξίας κατοικίας" column
merged["Μέσος όρος αξίας κατοικίας"] = merged["Value_q4_2022"] * merged["Μέσος όρος τετραγωνικών μέτρων"]


# In[45]:


merged["Αναλογία τιμής/ κόστους"] = merged["Κόστος ενεργειακής αναβάθμισης"] / merged["Αξία τετραγώνου"]


# In[46]:


merged["Αναλογία τιμής/ κόστους"]


# In[47]:


merged.describe()


# In[48]:


output = "datathon_all.csv"
merged.to_csv(output, index=False, encoding="utf-8-sig")


# In[49]:


print(merged.columns)


# In[ ]:




