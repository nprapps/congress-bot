#!/usr/bin/env python
# coding: utf-8

# In[2]:


import json
import os
from pprint import pprint
import time

import tweepy
import requests

headers = {
    'X-API-Key': os.environ["PP_API_KEY"],
}


# ### load members we want to track

# In[4]:


member_list = []

with open('data/member_data.json', 'r') as ofile:
    member_list = json.loads(ofile.read())
ofile.close()


# ### just get member ids

# In[5]:


member_ids = []

for member in member_list:
    member_ids.append(member["id"])


# ### pull all votes for these members

# In[21]:


all_recent_member_votes = []

for member_id in member_ids:
    recent_member_votes = json.loads(requests.get("https://api.propublica.org/congress/v1/members/"+ member_id +"/votes.json", headers=headers).text)["results"]
    recent_member_votes = recent_member_votes[0]["votes"]
#     pprint(recent_member_votes)
    all_recent_member_votes.append(recent_member_votes)                                 
    
    
    


# ### identify votes cast since last vote tracked

# In[7]:


last_votes = {}

with open('data/last_votes.json', 'r') as ofile:
    last_votes = json.loads(ofile.read())
ofile.close()


new_votes = []

for member in all_recent_member_votes:
    for vote in member:
        if vote["roll_call"] > last_votes[vote["member_id"]]:
            new_votes.append(vote)


# ### craft the tweet text from vote dit

# In[30]:


congress_conversions = {'115': '115th', '116': '116th', '117': '117th', '118': '118th', '119': '119th', '120': '120th', '121': '121st', '122': '122nd', '123': '123rd'}

max_tweet_len = 280
link_len = 23
allowed_text_length = max_tweet_len - link_len - 5

for vote in new_votes:
    t_text = ""
    member_dict = [x for x in member_list if x["id"] == vote["member_id"]][0]
#     full_name = member_dict["role"][0:3] + ". " + member_dict["name"] + " (" + member_dict["party"] + ")" 
    try:
        full_name = ".@" + member_dict["twitter_id"] + " (" + member_dict["party"] + ")" 
    except:
        full_name = member_dict["role"][0:3] + ". " + member_dict["name"] + " (" + member_dict["party"] + ")" 
    if vote["position"].lower() != "not voting":
        t_text = t_text + full_name + " voted "
        t_text = t_text + vote['position'].lower()
    else:
        t_text = t_text = t_text + full_name + " did not vote"
    t_text = t_text + " on "
    t_text = t_text + vote["bill"]['number']  
    if vote['bill']['title'] != None:
        t_text = t_text + ', ' + vote['bill']['title'].replace("A bill", "a bill")
    
#     if this is a nomination
    if 'nomination' in vote:
        t_text = t_text + ": the nomination of " + vote["description"]
    
    if len(t_text) > allowed_text_length:
        t_text = t_text[0:allowed_text_length] + "... "
        
    congress_ord = congress_conversions[vote["congress"]]
    bill_nums =  [x for x in list(vote["bill"]["number"]) if x.isdigit()]
    bill_num = "".join(bill_nums)
    bill_chamber = "senate"
    if "H" in vote['bill']['number'].upper():
        bill_chamber = "house"
    congress_gov_url = "https://www.congress.gov/bill/"+ congress_ord +"-congress/" + bill_chamber + "-bill/"+ bill_num
    if 'nomination' in vote:
        congress_gov_url = "https://www.congress.gov/nomination/"+ congress_ord +"-congress/" + vote["nomination"]["number"][2:]
    
    t_text = t_text + " " + congress_gov_url
    vote["t_text"] = t_text
    


# ### send the tweets

# In[24]:


# send tweets here
auth = tweepy.OAuthHandler(os.environ["T_CONSUMER_KEY"],os.environ["T_CONSUMER_SECRET"])
auth.set_access_token(os.environ["T_ACCESS_TOKEN"],os.environ["T_ACCESS_TOKEN_SECRET"])
api = tweepy.API(auth)
    
    
sleep_time = (30 * 60)/len(new_votes)
if sleep_time > 30:
    sleep_time = 30



for vote in new_votes:
    try:
        api.update_status(status=vote["t_text"])
    except:
        pass
    time.sleep(sleep_time)
    


# ### track the last vote for each member

# In[18]:


most_recent_roll_calls = {}

for member in all_recent_member_votes:
    most_recent_roll_calls[member[0]["member_id"]] = member[0]["roll_call"]
    
with open('data/last_votes.json', 'w') as ofile:
    ofile.write(json.dumps(most_recent_roll_calls))
ofile.close()


# In[ ]:




