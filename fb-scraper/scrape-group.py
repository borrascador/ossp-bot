# --*-- coding: UTF--8 --*--

import urllib.request
import urllib.error
import json
import datetime
import csv
import time
from secret import *


ACCESS_TOKEN = APP_ID + "|" + APP_SECRET

def request_until_succeed(url):
    req = urllib.request.Request(url)
    success = False
    while success is False:
        try: 
            response = urllib.request.urlopen(req)
            if response.getcode() == 200:
                success = True
        except Exception as e:
            print(e)
            print("Error for URL {} at {}".format(url, datetime.datetime.now()))
            print("Error for URL {} at {}".format(url, datetime.datetime.now()))
            time.sleep(5)
            print("Retrying.")
    return response.read().decode('UTF-8')

# Needed to write tricky unicode correctly to csv
def unicode_normalize(text):
    return text.translate({ 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22,
                            0xa0:0x20 })

def getFacebookPageFeedData(GROUP_ID, ACCESS_TOKEN, num_statuses):

    # Construct the URL string; see 
    # http://stackoverflow.com/a/37239851 for Reactions parameters
    base = "https://graph.facebook.com/v2.6"
    node = "/"+ GROUP_ID + "/feed"  
    fields = "/?fields=message,link,created_time,type,name,id," + \
            "comments.limit(0).summary(true),shares,reactions." + \
            "limit(0).summary(true),from"
    parameters = "&limit={}&access_token={}".format(num_statuses, ACCESS_TOKEN)
    url = base + node + fields + parameters

    # retrieve data
    data = json.loads(request_until_succeed(url), encoding='UTF-8')

    return data

def getReactionsForStatus(status_id, ACCESS_TOKEN):

    # See http://stackoverflow.com/a/37239851 for Reactions parameters
        # Reactions are only accessable at a single-post endpoint

    base = "https://graph.facebook.com/v2.6"
    node = "/{}".format(status_id)
    reactions = "/?fields=" \
            "reactions.type(LIKE).limit(0).summary(total_count).as(like)" \
            ",reactions.type(LOVE).limit(0).summary(total_count).as(love)" \
            ",reactions.type(WOW).limit(0).summary(total_count).as(wow)" \
            ",reactions.type(HAHA).limit(0).summary(total_count).as(haha)" \
            ",reactions.type(SAD).limit(0).summary(total_count).as(sad)" \
            ",reactions.type(ANGRY).limit(0).summary(total_count).as(angry)"
    parameters = "&access_token={}".format(ACCESS_TOKEN)
    url = base + node + reactions + parameters

    # retrieve data
    data = json.loads(request_until_succeed(url), encoding='UTF-8')

    return data


def processFacebookPageFeedStatus(status, ACCESS_TOKEN):

    # The status is now a Python dictionary, so for top-level items,
    # we can simply call the key.

    # Additionally, some items may not always exist,
    # so must check for existence first
    status_id = status['id']
    status_message = '' if 'message' not in status.keys() else \
            unicode_normalize(status['message'])
    link_name = '' if 'name' not in status.keys() else \
            unicode_normalize(status['name'])
    status_type = status['type']
    status_link = '' if 'link' not in status.keys() else \
            unicode_normalize(status['link'])
    status_author = unicode_normalize(status['from']['name'])

    # Time needs special care since a) it's in UTC and
    # b) it's not easy to use in statistical programs.

    status_published = datetime.datetime.strptime(\
            status['created_time'],'%Y-%m-%dT%H:%M:%S+0000')
    status_published = status_published + datetime.timedelta(hours=-5) # EST
    # best time format for spreadsheet programs:
    status_published = status_published.strftime('%Y-%m-%d %H:%M:%S')

    # Nested items require chaining dictionary keys.

    num_reactions = 0 if 'reactions' not in status else \
            status['reactions']['summary']['total_count']
    num_comments = 0 if 'comments' not in status else \
            status['comments']['summary']['total_count']
    num_shares = 0 if 'shares' not in status else \
            status['shares']['count']

    # Counts of each reaction separately; good for sentiment
    # Only check for reactions if past date of implementation:
    # http://newsroom.fb.com/news/2016/02/reactions-now-available-globally/

    reactions = getReactionsForStatus(status_id, ACCESS_TOKEN) \
            if status_published > '2016-02-24 00:00:00' else {}

    num_likes = 0 if 'like' not in reactions else \
            reactions['like']['summary']['total_count']

    # Special case: Set number of Likes to Number of reactions for pre-reaction
    # statuses

    num_likes = num_reactions if status_published < '2016-02-24 00:00:00' else \
            num_likes

    def get_num_total_reactions(reaction_type, reactions):
        if reaction_type not in reactions:
            return 0
        else:
            return reactions[reaction_type]['summary']['total_count']

    num_loves = get_num_total_reactions('love', reactions)
    num_wows = get_num_total_reactions('wow', reactions)
    num_hahas = get_num_total_reactions('haha', reactions)
    num_sads = get_num_total_reactions('sad', reactions)
    num_angrys = get_num_total_reactions('angry', reactions)

    # return a tuple of all processed data
    return (status_id, status_message, status_author, link_name, status_type, 
            status_link, status_published, num_reactions, num_comments, 
            num_shares, num_likes, num_loves, num_wows, num_hahas, num_sads,
            num_angrys)

def scrapeFacebookPageFeedStatus(GROUP_ID, ACCESS_TOKEN):
    csv.register_dialect
    with open('{}_facebook_statuses.csv'.format(GROUP_ID), 'w', newline='', \
              encoding='UTF-8') as file:
        w = csv.writer(file)
        w.writerow(["status_id", "status_message", "status_author", 
            "link_name", "status_type", "status_link",
            "status_published", "num_reactions", "num_comments", 
            "num_shares", "num_likes", "num_loves", "num_wows", 
            "num_hahas", "num_sads", "num_angrys"])

        has_next_page = True
        num_processed = 0   # keep a count on how many we've processed
        scrape_starttime = datetime.datetime.now()

        print("Scraping {} Facebook Group at {}".format(
                GROUP_ID, scrape_starttime))

        statuses = getFacebookPageFeedData(GROUP_ID, ACCESS_TOKEN, 100)

        while has_next_page:
            for status in statuses['data']:
                
                # Ensure it is a status with the expected metadata
                if 'reactions' in status:
                    w.writerow(processFacebookPageFeedStatus(status, ACCESS_TOKEN))

                # output progress occasionally to make sure code is not
                # stalling
                num_processed += 1
                if num_processed % 100 == 0:
                    print("{} Statuses Processed: {}".format(
                            num_processed, datetime.datetime.now()))

            # if there is no next page, we're done.
            if 'paging' in statuses.keys():
                statuses = json.loads(request_until_succeed(\
                        statuses['paging']['next']), encoding='UTF-8')
            else:
                has_next_page = False


        print("\nDone!\n{} Statuses Processed in {}".format(
                num_processed, datetime.datetime.now() - scrape_starttime))


if __name__ == '__main__':
    scrapeFacebookPageFeedStatus(GROUP_ID, ACCESS_TOKEN)


# The CSV can be opened in all major statistical programs. Have fun! :)
