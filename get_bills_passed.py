#!/usr/bin/env python
# coding: utf-8

# In[22]:


import json
import os
from pprint import pprint
from datetime import datetime, date, timedelta
import time

import tweepy
import requests

headers = {
    'X-API-Key': os.environ["PP_API_KEY"],
}


# ### get members

# In[23]:


member_list = []

with open('data/member_data.json', 'r') as ofile:
    member_list = json.loads(ofile.read())
ofile.close()


# ### just get member ids

# In[24]:


member_ids = []

for member in member_list:
    member_ids.append(member["id"])


# ### get most recent bills passed

# In[25]:


future_cong = True
this_cong = 123

while future_cong == True:
    resp_json = json.loads(requests.get("https://api.propublica.org/congress/v1/"+ str(this_cong) +"/house/bills/passed.json", headers=headers).text)
    if resp_json["status"] == "500":
        this_cong = this_cong - 1
    else:
        future_cong = False


# ### filter to just this state bills AND that have not been tweeted

# In[26]:


this_state_bills = []

tweeted_bill_ids = []

with open('data/tweeted_bills_passed.json', "r") as ofile:
    tweeted_bill_ids = json.loads(ofile.read())
ofile.close()

for bill in resp_json["results"][0]['bills']:
    if bill["sponsor_id"] in member_ids and bill["bill_id"] not in tweeted_bill_ids:
        this_state_bills.append(bill)


# In[27]:


this_state_bills


# ### craft tweets

# In[28]:


congress_conversions = {'115': '115th', '116': '116th', '117': '117th', '118': '118th', '119': '119th', '120': '120th', '121': '121st', '122': '122nd', '123': '123rd'}

max_tweet_len = 280
link_len = 23
allowed_text_length = max_tweet_len - link_len - 5

for bill in this_state_bills:
    member_dict = [x for x in member_list if x["id"] == bill["sponsor_id"]][0]
    
    try:
        full_name = "@" + member_dict["twitter_id"] + " (" + member_dict["party"] + ")" 
    except:
        full_name = member_dict["role"][0:3] + ". " + member_dict["name"] + " (" + member_dict["party"] + ")" 
    
    house_pass = False
    sen_pass = False
    
    if bill['house_passage'] != None:
        house_pass = True
    if bill['senate_passage'] != None:
        sen_pass = True
        
    
    today_format = datetime.strftime(date.today(), "%Y-%m-%d")
    yesterday_format = datetime.strftime(date.today() - timedelta(1), "%Y-%m-%d")
        
        
    if today_format not in [bill['house_passage'], bill['senate_passage']] and yesterday_format not in [bill['house_passage'], bill['senate_passage']]:
        continue
    
        
        
        
    t_text = ""
    
    t_text = t_text + bill["number"] + ", introduced by "
    t_text = t_text + full_name + ", "
    
    if house_pass == True and sen_pass == True:
        t_text = t_text + "has passed the House and the Senate."
    elif house_pass == True:
        t_text = t_text + "has passed the House."
    elif sen_pass == True:
        t_text = t_text + "has passed the Senate."
    else:
        continue
        
    
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

# In[29]:


# send tweets here
auth = tweepy.OAuthHandler(os.environ["T_CONSUMER_KEY"],os.environ["T_CONSUMER_SECRET"])
auth.set_access_token(os.environ["T_ACCESS_TOKEN"],os.environ["T_ACCESS_TOKEN_SECRET"])
api = tweepy.API(auth)
    
    
for bill in this_state_bills:
    if "t_text" in bill:
        api.update_status(status=bill["t_text"])
        time.sleep(60)
    


# ### log that the bills been tweeted

# In[30]:


bill_ids = []

for bill in this_state_bills:
    bill_ids.append(bill["bill_id"]) 
    
tweeted_bill_ids = tweeted_bill_ids + bill_ids

with open('data/tweeted_bills_passed.json', 'w') as ofile:
    ofile.write(json.dumps(tweeted_bill_ids))
ofile.close()


# In[ ]:





# In[ ]:





# In[ ]:




