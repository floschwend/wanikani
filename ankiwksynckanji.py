from anki.collection import Collection
from datetime import datetime, timedelta, date
import itertools
import jmespath
from collections import namedtuple
from pathlib import Path
import requests
import yaml


config = yaml.safe_load(open("config.yaml"))

def fetchAndParseUrl(url, params):

    print("Fetching: {url}".format(url= url))
    
    headers = {"Wanikani-Revision": "20170710", "Authorization": "Bearer {key}".format(key= config['waniKaniKey'])}

    try:
        resp = requests.get(url=url, params=params, headers=headers)
        data = resp.json()

        return data

    except Exception as inst:
        print("Exception in fetchAndParseUrl: {msg}".format(msg = inst))
    
def fetchAssignmentsPage(url, params):  
    data = fetchAndParseUrl(url, params)

    assignments = jmespath.search('data[*].data', data)

    print("Found assignments in page: {number}".format(number= len(assignments)))

    next = data["pages"]["next_url"]
    if next is not None:
        assignments = assignments.append(fetchAssignmentsPage(next, {}))    #empty params as the URL already contains them

    return assignments

def fetchAssignments():

    url = "https://api.wanikani.com/v2/assignments"
    params = {"srs_stages": ','.join(str(i) for i in range(1,10)), "subject_types":"kanji"}

    assignments = fetchAssignmentsPage(url, params)

    subjectIds = jmespath.search("[*].subject_id", assignments)
    subjects = fetchSubjects(subjectIds)

    print(subjects)
    #fillInKanjis(subjects)

def fetchSubjects(ids):

    subjects = []

    chunkSize = 300
    for i in range(0, len(ids), chunkSize):
        inclfrom = i
        exclto = min(i+chunkSize, len(ids))
        subids = list(ids[inclfrom:exclto])
        subjdata = fetchSubjectsPage(subids)
        subjects.append(subjdata)

    print("Found total subjects: subjtotal".format(subjtotal = len(subjects)))

    return subjects


def fetchSubjectsPage(ids):

    url = "https://api.wanikani.com/v2/subjects"
    params = {"ids":",".join(map(str, ids))}

    data = fetchAndParseUrl(url, params)
    subjects = jmespath.search('data[*].{type: object, data: data}', data)

    print("Found subjects in page: {subjpage}".format(subjpage=len(subjects)))

    return subjects


# Get Kanjis from WK
fetchAssignments()

# Open Anki Collection


#
