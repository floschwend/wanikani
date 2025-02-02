from anki.collection import Collection
from datetime import datetime, timedelta, date
import itertools
import jmespath
from collections import namedtuple
from pathlib import Path
import requests
import yaml


config = yaml.safe_load(open("config.yaml"))

# Get Kanjis from WK

def fetchAndParseUrl(url):

    print("Fetching: {url}".format(url= url))

    params = {"srs_stages": ','.join(str(i) for i in range(1,10)), "subject_types":"kanji"}
    
    headers = {"Wanikani-Revision": "20170710", "Authorization": "Bearer {key}".format(key= config['waniKaniKey'])}

    try:
        resp = requests.get(url=url, params=params, headers=headers)
        data = resp.json()

        return data

    except Exception as inst:
        print("Exception in fetchAndParseUrl: {msg}".format(msg = inst))
    
def fetchAssignmentsPage(url, a):  
    data = fetchAndParseUrl(url)

    assignments = jmespath.search('data[*].data', data)

    print("Found assignments in page: {number}".format(number= len(assignments)))

    next = data["pages"]["next_url"]
    if a == 1:
        return assignments
    #if next is not None:
    #    assignments = assignments.append(fetchAssignmentsPage(next))
    assignments = assignments.append(fetchAssignmentsPage(url, 1))

    return assignments

fetchAssignmentsPage("https://api.wanikani.com/v2/assignments", 2)

'''

def fetchAssignments():

  url = "https://api.wanikani.com/v2/assignments"
  params = {
    srs_stages: Array(9).fill().map((element, index) => index + 1),
    subject_types: ["kanji","radical","vocabulary"]
  };

  startUrl = url.addQuery(params).toString()
  assignments = fetchAssignmentsPage(startUrl)

  subjectIds = jmespath.search(assignments, "[*].subject_id")
  subjects = fetchSubjects(subjectIds)

  fillInKanjis(subjects)



# Open Anki Collection


#
'''