from anki.collection import Collection
import jmespath
from pathlib import Path
import requests
import yaml


config = yaml.safe_load(open("config.yaml"))

def fetchAndParseUrl(url, params, return_method, bearer):

    print("Fetching: {url} with params {params}".format(url= url, params = params))
    
    headers = {"Wanikani-Revision": "20170710", "Authorization": "Bearer {key}".format(key= bearer)}

    try:
        resp = requests.get(url=url, params=params, headers=headers)
        data = return_method(resp)

        return data

    except Exception as inst:
        print("Exception in fetchAndParseUrl: {msg}".format(msg = inst))
    
def fetchAssignmentsPage(url, params, bearer):  
    data = fetchAndParseUrl(url, params, lambda p: p.json(), bearer)

    assignments = jmespath.search('data[*].data', data)

    print("Found assignments in page: {number}".format(number= len(assignments)))

    next = data["pages"]["next_url"]
    if next is not None:
        newAssignments = fetchAssignmentsPage(next, {}, bearer)   #empty params as the URL already contains them
        assignments += newAssignments 

    return assignments

def fetchSubjects(types, bearer):

    url = "https://api.wanikani.com/v2/assignments"
    params = {"srs_stages": ','.join(str(i) for i in range(1,10)), "subject_types":types}

    assignments = fetchAssignmentsPage(url, params, bearer)

    subjectIds = jmespath.search("[*].subject_id", assignments)
    subjects = fetchSubjectsDetails(subjectIds, bearer)

    return subjects

def fetchSubjectsDetails(ids, bearer):

    subjects = []

    chunkSize = 300
    for i in range(0, len(ids), chunkSize):
        inclfrom = i
        exclto = min(i+chunkSize, len(ids))
        subids = list(ids[inclfrom:exclto])
        subjdata = fetchSubjectsDetailsPage(subids, bearer)
        subjects = subjects + subjdata

    print("Found total subjects: {subjtotal}".format(subjtotal = len(subjects)))

    return subjects


def fetchSubjectsDetailsPage(ids, bearer):

    url = "https://api.wanikani.com/v2/subjects"
    params = {"ids":",".join(map(str, ids))}

    data = fetchAndParseUrl(url, params, lambda p: p.json(), bearer)
    subjects = jmespath.search('data[*].{id: id, type: object, data: data}', data)

    radicals = [v for v in subjects if v["type"] == "radical"]
    for radical in radicals:
        subjchars = radical["data"]["characters"]
        if subjchars is None or len(subjchars) == 0:
            url = next((v["url"] for v in radical["data"]["character_images"] if v["content_type"] == "image/svg+xml"), "")
            svgcode = fetchAndParseUrl(url, {}, lambda p: p.text, bearer)
            radical["data"]["svgcode"] = svgcode

    print("Found subjects in page: {subjpage}".format(subjpage=len(subjects)))

    return subjects



