# Congress Leg (_lej_) Bot

Contributors: Sean McMinn, Frankie Paris, Sara Wise, Maite Fernandez and Sean Mussenden

Developed at [NPR Serendipity Days](https://www.npr.org/sections/inside/2011/10/14/141312774/happy-accidents-the-joy-of-serendipity-days) and [Hacks/Hackers DC](https://www.meetup.com/Hacks-Hackers-DC/).

-----------

This is a Twitter bot to track activity by members of Congress from a specific state.

The bot is currently prototyped on California (1): because Sean is from that golden state, and (2): because if this works California's 55-member delegation, it should be fine with, say, West Virginia's four-person delegation. 

The Python scripts are set up to regularly ping [ProPublica's Congress API](https://projects.propublica.org/api-docs/congress-api/). They check for new data, then compose tweets based on the the information returned.

This uses the [Tweepy](http://www.tweepy.org/) Python library to post tweets.


### Current functionality:

- Tweet votes by senators and House members
- Tweet statements by senators and House members
- Tweet bills introduced by senators and House members

### Future (aspirational) functionality:

- Tweet cosponsorships by senators and House members
- Tweet TV/radio appearances by senators and House members
- Tweet amendments offered by senators and House members
- Tweet when a  bill passes that was introduced by a senator or House member from a specific state