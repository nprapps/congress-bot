#!/usr/bin/env python
# coding: utf-8

# In[10]:


import json

import requests


import os


# ## set api header

# In[5]:


headers = {
    'X-API-Key': os.environ["PP_API_KEY"],
}


# ## make api call to get delegation (with requests)

# In[6]:

state_postal = "CA"

senate_resp = requests.get('https://api.propublica.org/congress/v1/members/senate/'+ state_postal +'/current.json', headers=headers)
house_resp = requests.get('https://api.propublica.org/congress/v1/members/house/'+ state_postal +'/current.json', headers=headers)


# ## set list of all members w all data

# In[7]:


all_members_list = json.loads(senate_resp.text)["results"] + json.loads(house_resp.text)["results"]


# ## function to extract data we want

# In[8]:


member_data = []

def get_member_data(member_list):
    for member in member_list:
        d = {}
        d["twitter_id"] = member["twitter_id"]
        d["party"] = member["party"]
        d["id"] = member["id"]
        d["role"] = member["role"]
        d["name"] = member["name"]
        member_data.append(d)
        
get_member_data(all_members_list)


# In[9]:


with open('../data/member_data.json', 'w') as ofile:
    ofile.write(json.dumps(member_data))
ofile.close()

