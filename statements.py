#!/usr/bin/env python
# coding: utf-8
# In[2]:
import json
import os
from pprint import pprint
import tweepy
import requests
headers = {
    'X-API-Key': os.environ["PP_API_KEY"],,
}
# ### load members we want to track
member_list = []
with open('/home/fparis/member_data.json', 'r') as ofile:
    member_list = json.loads(ofile.read())
ofile.close()
# ### just get member ids
member_ids = []
for member in member_list:
    member_ids.append(member["id"])



# ### pull all statements for these members
all_recent_member_statements = json.loads(requests.get("https://api.propublica.org/congress/v1/statements/latest.json",headers=headers).text)["results"]
### get CA statements
all_statements = []
for statement in all_recent_member_statements:
    if statement["member_id"] in member_list:
        all_statements.append(statement)


# ### identify statements made since last statement tracked
prev_statements = []
with open('/home/fparis/old_statements.json', 'r') as ofile:
    prev_statements = json.loads(ofile.read())
ofile.close()


new_statements = []
for statement in all_statements:
    statement_id = statement["date"] + statement["member_id"] + statement["title"]
    if statement_id not in prev_statements:
        new_statements.append(statement)

# ### craft the tweet text
max_tweet_len = 280
link_len = 23
allowed_text_length = max_tweet_len - link_len - 5
for statement in new_statements:
    t_text=""
    member_dict = [x for x in member_list if x["id"] == statement["member_id"]][0]
    try:
        full_name = ".@" + member_dict["twitter_id"] + " (" + member_dict["party"] + ")"
    except:
        full_name = member_dict["role"][0:3] + ". " + member_dict["name"] + " (" + member_dict["party"] + ")"
    t_text = t_text + full_name + ' made a statement: "' + statement["title"]
    t_text = t_text + '" '
    if len(t_text) > allowed_text_length:
        t_text = t_text[0:allowed_text_length] + "... " 
    t_text = t_text + statement["url"]

    statement["t_text"] = t_text
# print(len(new_statements))
# send tweets here
auth = tweepy.OAuthHandler(os.environ["T_CONSUMER_KEY"],os.environ["T_CONSUMER_SECRET"])
auth.set_access_token(os.environ["T_ACCESS_TOKEN"],os.environ["T_ACCESS_TOKEN_SECRET"])
api = tweepy.API(auth)
for statement in new_statements:
    print(statement["t_text"])
    print()
#   api.update_status(status=statement["t_text"])
print(len(new_statements))
### track the statements already tweeted
for statement in new_statements:
    statement_id = statement["date"] + statement["member_id"] + statement["title"]
    prev_statements.append(statement_id)
with open('/home/fparis/old_statements.json', 'w') as ofile:
    ofile.write(json.dumps(prev_statements))
ofile.close()