#!/usr/bin/env python
# coding: utf-8

# ## Ayima N-Grams Script
# 
# Takes in SQR data and outputs data split into one, two and 3 word phrases
# 
# Script produced by Ayima Limited (www.ayima.com)
# 
# © 2022. This work is licensed under a CC BY SA 4.0 license (https://creativecommons.org/licenses/by-sa/4.0/).
# 
# Version 1.1
# 
# ### Instructions
# 
# Download an SQR from within the reports section of Google ads. 
# 
# The report must contain the following metrics:
# + Search term
# + Campaign
# + Campaign state
# + Currency code
# + Impressions
# + Clicks 
# + Cost
# + Conversions
# + Conv. value
# 
# Then, complete the setting section as instructed and run the whole script
# 
# The script may take some time. Ngrams are computationally difficult, particularly for larger accounts. But, give it enough time to run, and it will log if it is running correctly.

# ### Settings

# In[1]:


file_name = "N-Grams input - SQR.csv"  #The name of the file to run this script on. By default, looks for this file in a "Data" folder in the same place as this script (e.g. your downloads folder)



grams_to_run = [1,2,3]                  #What length phrases you want to retrieve for. Recommended is < 4 max. Longer phrases retrieves far more results.
campaigns_to_exclude = ""               #input strings contained by campaigns you want to EXCLUDE, separated by commas if multiple (e.g. "DSA,PLA"). Case Insensitive
campaigns_to_include = "PLA"            #input strings contained by campaigns you want to INCLUDE, separated by commas if multiple (e.g. "DSA,PLA"). Case Insensitive
character_limit = 3                     #minimum number of characters in an ngram e.g. to filter out "a" or "i". Will filter everything below this limit
client_name = "SAMPLE CLIENT"           #Client name, to label on the final file
enabled_campaigns_only = True           #Whether to only run the script for enabled campaigns
save_location = f"Outputs/"             #Where you want to save the file. By default, creates and folder in the same place as this script
impressions_column_name = "Impr."       #Google consistently flip between different names for their impressions column. Just to annoy us. This spelling was correct at time of writing
brand_terms = ["BRAND_TERM_2",          #Labels brand and non-brand search terms. Can add as many as you want. Case insensitive. If none, leave as [""]
               "BRAND_TERM_2"]          #e.g. ["Adidas","Addidas"]


# In[2]:


import pandas as pd
from nltk import ngrams
import numpy as np
import time
import re


# In[ ]:





# In[ ]:





# In[3]:


def read_file(file_name):
    #find the file format and import
    if file_name.strip().split('.')[-1] == "xlsx":
        return pd.read_excel(f"{file_name}",skiprows = 2, thousands =",")
    elif file_name.strip().split('.')[-1] == "csv":
        return pd.read_csv(f"{file_name}",skiprows = 2, thousands =",")


# In[4]:


df = read_file(file_name)


# In[5]:


df.head()


# In[6]:


def filter_campaigns(df, to_ex = campaigns_to_exclude,to_inc = campaigns_to_include):
    to_ex = to_ex.split(",")
    to_inc = to_inc.split(",")
    
    if to_inc != ['']:
        to_inc = [word.lower() for word in to_inc]
        df = df[df["Campaign"].str.lower().str.strip().str.contains('|'.join(to_inc))]
    if to_ex != ['']:
        to_ex = [word.lower() for word in to_ex]
        df = df[~df["Campaign"].str.lower().str.strip().str.contains('|'.join(to_ex))]
    
    if enabled_campaigns_only:
        try:
            df = df[df["Campaign state"].str.contains("Enabled")]
        except KeyError:
            print("Couldn't find 'Campaign state' column")
        
    return df


# In[7]:


def generate_ngrams(list_of_terms, n):
    """
    Turns a list of search terms into a set of unique n-grams that appear within
    """                
    # Clean the terms up first and remove special characters/commas etc.
    clean_terms = []
    for st in list_of_terms:
        clean_terms.append(re.sub(r'[^a-zA-Z0-9\s]', '', st))
        #split into grams
                    
    unique_ngrams = set()
      
    for term in clean_terms:
        grams = ngrams(term.split(" "), n)
        [unique_ngrams.add(gram) for gram in grams]
    all_grams = set([' '.join(tups) for tups in unique_ngrams])
    
    if character_limit > 0:
        n_grams_list = [ngram for ngram in all_grams if len(ngram) > character_limit]
    
    return n_grams_list
        


# In[ ]:





# In[8]:


def _collect_stats(term):
    
    #Slice the dataframe to the terms at hand
    sliced_df = df[df["Search term"].str.match(fr'.*{re.escape(term)}.*')]
        
    #add our metrics
    raw_data = list(np.sum(sliced_df[[impressions_column_name,"Clicks","Cost","Conversions","Conv. value"]]))
    
    return raw_data


# In[9]:


def _generate_metrics(df):
    #generate metrics
    try:
        df["CTR"] = df["Clicks"]/df[f"{impressions_column_name}"]
        df["CVR"] = df["Conversions"]/df["Clicks"]
        df["CPC"] = df["Cost"]/df["Clicks"]
        df["ROAS"] = df[f"Conv. value"]/df["Cost"]
        df["CPA"] = df["Cost"]/df["Conversions"]
    except KeyError:
        print("Couldn't find a column")
    
    #replace infinites with NaN and replace with 0
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.fillna(0, inplace= True)
    df.round(2)
    
    return df


# In[10]:


def build_ngrams_df(df, sq_column_name ,ngrams_list, character_limit = 0):
    """
    Takes in n-grams and df and returns df of those metrics
    
    df - dataframe in question
    sq_column_name - str. Name of the column containing search terms
    ngrams_list - list/set of unique ngrams, already generated
    character_limit - Words have to be over a certain length, useful for single word grams
    
    Outputs a dataframe
    """
    
    #set up metrics lists to drop values
    array = []
    
    
    
    raw_data = map(_collect_stats, ngrams_list)    
    
    #stack into an array
    data = np.array(list(raw_data))  

    #turn the above into a dataframe
    columns = ["Impressions","Clicks","Cost","Conversions", "Conv. value"]

    ngrams_df = pd.DataFrame(columns= columns, 
                              data=data, 
                              index = list(ngrams_list), 
                              dtype = float)
    
    ngrams_df.sort_values(by = "Cost", ascending = False, inplace = True)
    #calculate additional metrics and return
    return _generate_metrics(ngrams_df)


# In[11]:


def group_by_sqs(df):
    df = df.groupby("Search term", as_index = False).sum()
    return df
df = group_by_sqs(df)


# In[12]:


writer = pd.ExcelWriter(f"{save_location}{client_name} N-Grams.xlsx", 
                            engine='xlsxwriter')

df.to_excel(writer, sheet_name='Raw Searches')

writer.close()


# In[ ]:





# In[13]:


def find_brand_terms(df, brand_terms = brand_terms):
    brand_terms = [str.lower(term) for term in brand_terms]
    st_brand_bool = []
    for i, row in df.iterrows():
        term = row["Search term"]
        
        #runs through the term and if any of our brand strings appear, labels the column brand
        
        if any([brand_term in term for brand_term in brand_terms]):
            st_brand_bool.append("Brand")
        else:
            st_brand_bool.append("Generic")
    return st_brand_bool

df["Brand label"] = find_brand_terms(df)


# In[14]:


#This is necessary for larger search volumes to cut down the very outlier terms with extremely few searches
i = 1
while len(df)> 40000:
    print(f"DF too long, at {len(df)} rows, filtering to impressions greater than {i}")
    df = df[df[impressions_column_name] > i]
    i+=1


# In[ ]:


writer = pd.ExcelWriter(f"{save_location}{client_name} N-Grams.xlsx", engine='xlsxwriter')

for n in grams_to_run:
    print("Working on ",n, "-grams")
    n_grams = generate_ngrams(df["Search term"], n)
    print(f"Found {len(n_grams)} n_grams, building stats (may take some time)")
    n_gram_df = build_ngrams_df(df,"Search term", n_grams, character_limit)
    print("Adding to file")

    n_gram_df.to_excel(writer, sheet_name=f'{n}-Gram',)

    writer.close()
    


# In[ ]:





# In[ ]:




