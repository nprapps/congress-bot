#!/usr/bin/env python
# coding: utf-8

# In[38]:


import json
import os
import time
from pprint import pprint


import tweepy
import requests

headers = {
    'X-API-Key': os.environ["PP_API_KEY"],
}


# ### get members

# In[14]:


member_list = []

with open('data/member_data.json', 'r') as ofile:
    member_list = json.loads(ofile.read())
ofile.close()


# ### just get member ids

# In[15]:


member_ids = []

for member in member_list:
    member_ids.append(member["id"])


# ### get most recent bills

# In[16]:


future_cong = True
this_cong = 123

while future_cong == True:
    resp_json = json.loads(requests.get("https://api.propublica.org/congress/v1/"+ str(this_cong) +"/house/bills/introduced.json", headers=headers).text)
    if resp_json["status"] == "500":
        this_cong = this_cong - 1
    else:
        future_cong = False


# ### filter to just this state bills that have not been tweeted

# In[17]:


this_state_bills = []

tweeted_bill_ids = []

with open('data/tweeted_bills.json', "r") as ofile:
    tweeted_bill_ids = json.loads(ofile.read())
ofile.close()

for bill in resp_json["results"][0]['bills']:
    if bill["sponsor_id"] in member_ids and bill["bill_id"] not in tweeted_bill_ids:
        this_state_bills.append(bill)


# In[18]:


this_state_bills


# ### craft tweets

# In[19]:


congress_conversions = {'115': '115th', '116': '116th', '117': '117th', '118': '118th', '119': '119th', '120': '120th', '121': '121st', '122': '122nd', '123': '123rd'}

max_tweet_len = 280
link_len = 23
allowed_text_length = max_tweet_len - link_len - 5

for bill in this_state_bills:
    member_dict = [x for x in member_list if x["id"] == bill["sponsor_id"]][0]
    t_text = ""
    
    try:
        full_name = ".@" + member_dict["twitter_id"] + " (" + member_dict["party"] + ")" 
    except:
        full_name = member_dict["role"][0:3] + ". " + member_dict["name"] + " (" + member_dict["party"] + ")" 
        
        
    t_text = t_text + full_name + " introduced " + bill["number"]
    t_text = t_text + ", a bill to " + bill["short_title"].replace('To ', '', 1)
    
    
    if len(t_text) > allowed_text_length:
        t_text = t_text[0:allowed_text_length] + "... "
        
        
    congress_ord = congress_conversions[str(this_cong)]
    bill_nums =  [x for x in list(bill["number"]) if x.isdigit()]
    bill_num = "".join(bill_nums)
    bill_chamber = "senate"
    if "H" in bill['number'].upper():
        bill_chamber = "house"
    congress_gov_url = "https://www.congress.gov/bill/"+ congress_ord +"-congress/" + bill_chamber + "-bill/"+ bill_num
    
    t_text = t_text + " " + congress_gov_url
    
    
    bill["t_text"] = t_text


# ### send the tweets

# In[20]:


# send tweets here
auth = tweepy.OAuthHandler(os.environ["T_CONSUMER_KEY"],os.environ["T_CONSUMER_SECRET"])
auth.set_access_token(os.environ["T_ACCESS_TOKEN"],os.environ["T_ACCESS_TOKEN_SECRET"])
api = tweepy.API(auth)
    
    
for bill in this_state_bills:

    api.update_status(status=bill["t_text"])
    time.sleep(60)
    


# ### log that the bills been tweeted

# In[21]:


bill_ids = []

for bill in this_state_bills:
    bill_ids.append(bill["bill_id"]) 
    
tweeted_bill_ids = tweeted_bill_ids + bill_ids

with open('data/tweeted_bills.json', 'w') as ofile:
    ofile.write(json.dumps(tweeted_bill_ids))
ofile.close()


# In[48]:


json.loads(requests.get("https://api.propublica.org/congress/v1/statements/date/2018-10-05.json?offset=200", headers=headers).text)


# In[ ]:




