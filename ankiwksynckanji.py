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
    

fetchAndParseUrl("https://api.wanikani.com/v2/assignments")

'''
def fetchAssignmentsPage(url):  
    const data = fetchAndParseUrl(url);

    var assignments = jmespath.search(data, 'data[*].data');

    Logger.log("Found assignments in page: " + assignments.length)

    if (data.pages.next_url?.length > 0) {
        assignments = assignments.concat(fetchAssignmentsPage(data.pages.next_url));
    }

    return assignments;


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