#!/usr/bin/env python
# coding: utf-8

# # N-Grams for Google Shopping
# 
# This script looks to find patterns and trends in product feed data for Google shopping. It will help you find what words and phrases have been performing best for you
# 
# Script produced by Ayima Limited (www.ayima.com)
# 
# © 2022. This work is licensed under a CC BY SA 4.0 license (https://creativecommons.org/licenses/by-sa/4.0/).
# 
# Version 1.1
# 
# ## Instructions
# 
# Download an SQR from within the reports section of Google ads. 
# 
# The report must contain the following metrics:
# + Item ID
# + Product title
# + Impressions
# + Clicks
# 
# Then, complete the setting section as instructed and run the whole script
# 
# The script may take some time. Ngrams are computationally difficult, particularly for larger accounts. But, give it enough time to run, and it will log if it is running correctly.

# ## Settings

# In[1]:


#First, enter the name of the file to run this script on
#By default, the script only looks in the folder it is in for the file. So, place this script in your downloads folder for ease.
file_name = "Product report for N-Grams (1).csv"       
grams_to_run = [1,2,3]                                    #The number of words in a phrase to run this for (e.g. 3 = three-word phrases only)
character_limit = 0                                       #Words have to be over a certain length, useful for single word grams to rule out tiny words/symbols
title_column_name = "Product Title"                       #Name of our product title column
desc_column_name = ""                                     #Name of our product description column, if we have one
file_label = "Sample Client Name"                         #The label you want to add to the output file (e.g. the client name, or the run date)
impressions_column_name = "Impr."                         #Google consistently flip between different names for their impressions column. We think just to annoy us. This spelling was correct at time of writing
client_name = "SAMPLE"


# ## The Script
# #### You should not need to make changes below here

# In[2]:


#First import all of the relevant modules/packages
import pandas as pd
from nltk import ngrams
import numpy as np
import time
import re


# In[3]:


#import our data file
def read_file(file_name):
    #find the file format and import
    if file_name.strip().split('.')[-1] == "xlsx":
        return pd.read_excel(f"{file_name}",skiprows = 2, thousands =",")
    elif file_name.strip().split('.')[-1] == "csv":
        return pd.read_csv(f"{file_name}",skiprows = 2, thousands =",")#
    
df = read_file(file_name)


# In[4]:


df.head()


# In[5]:


def generate_ngrams(list_of_terms, n):
    """
    Turns our list of product titles into a set of unique n-grams that appear within
    """                             
    unique_ngrams = set()
      
    for term in list_of_terms:
        grams = ngrams(term.split(" "), n)
        [unique_ngrams.add(gram) for gram in grams if ' ' not in gram]
    ngrams_list = set([' '.join(tups) for tups in unique_ngrams])
    
    return ngrams_list


# In[6]:


def _collect_stats(term):
    
    #Slice the dataframe to the terms at hand
    sliced_df = df[df[title_column_name].str.match(fr'.*{re.escape(term)}.*')]
        
    #add our metrics
    raw_data = [len(sliced_df),                                           #number of products
                np.sum(sliced_df[impressions_column_name]),               #total impressions
                np.sum(sliced_df["Clicks"]),                              #total clicks
                np.mean(sliced_df[impressions_column_name]),              #average number of impressions
                np.mean(sliced_df["Clicks"]),                             #average number of clicks
                np.median(sliced_df[impressions_column_name]),            #median impressions
                np.std(sliced_df[impressions_column_name])]               #standard deviation 
    
    return raw_data


# In[7]:


def build_ngrams_df(df, title_column_name, ngrams_list, character_limit = 0, desc_column_name = ''):
    """
    Takes in n-grams and df and returns df of those metrics
    
    df - our dataframe
    title_column_name - str. Name of the column containing product titles
    ngrams_list - list/set of unique ngrams, already generated
    character_limit - Words have to be over a certain length, useful for single word grams to rule out tiny words/symbols
    desc_column_name =  str. Name of the column containing product descriptions, if applicable

    
    Outputs a dataframe
    """
    
    
    #first cut it to only grams longer than our minimum
    if character_limit > 0:
        ngrams_list = [ngram for ngram in ngrams_list if len(ngram) > character_limit]
        
    raw_data = map(_collect_stats, ngrams_list)
        
    #stack into an array
    data = np.array(list(raw_data))
    
    #data[np.isnan(data)] = 0
    columns = ["Product Count","Impressions","Clicks","Avg. Impressions", "Avg. Clicks","Median Impressions","Spread (Standard Deviation)"]

    #turn the above into a dataframe
    ngrams_df = pd.DataFrame(columns= columns, 
                              data=data, 
                              index = list(ngrams_list))
    
    #clean the dataframe and add other key metrics
    ngrams_df["CTR"] = ngrams_df["Clicks"]/ ngrams_df["Impressions"]
    ngrams_df.fillna(0, inplace=True)
    ngrams_df.round(2)
    ngrams_df[["Impressions","Clicks","Product Count"]] = ngrams_df[["Impressions","Clicks","Product Count"]].astype(int)
    
    ngrams_df.sort_values(by = "Avg. Impressions", ascending = False, inplace = True)
    #calculate additional metrics and return
    return ngrams_df


# In[8]:


df


# In[ ]:


writer = pd.ExcelWriter(f"{client_name} Product Feed N-Grams.xlsx", engine='xlsxwriter')
start_time = time.time()
for n in grams_to_run:
    print("Working on ",n, "-grams")
    n_grams = generate_ngrams(df["Product Title"], n)
    print(f"Found {len(n_grams)} n_grams, building stats (may take some time)")
    n_gram_df = build_ngrams_df(df,"Product Title", n_grams, character_limit)
    print("Adding to file")
    
    n_gram_df.to_excel(writer, sheet_name=f'{n}-Gram',)

time_taken = time.time() - start_time
print("Took "+str(time_taken) + " Seconds")
writer.close()


# In[ ]:





# In[ ]:




