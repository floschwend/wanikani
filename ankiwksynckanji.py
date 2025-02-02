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

def fetchSubjects():

    url = "https://api.wanikani.com/v2/assignments"
    params = {"srs_stages": ','.join(str(i) for i in range(1,10)), "subject_types":"kanji"}

    assignments = fetchAssignmentsPage(url, params)

    subjectIds = jmespath.search("[*].subject_id", assignments)
    subjects = fetchSubjectsDetails(subjectIds)

    return subjects

def fetchSubjectsDetails(ids):

    subjects = []

    chunkSize = 300
    for i in range(0, len(ids), chunkSize):
        inclfrom = i
        exclto = min(i+chunkSize, len(ids))
        subids = list(ids[inclfrom:exclto])
        subjdata = fetchSubjectsDetailsPage(subids)
        subjects = subjects + subjdata

    print("Found total subjects: {subjtotal}".format(subjtotal = len(subjects)))

    return subjects


def fetchSubjectsDetailsPage(ids):

    url = "https://api.wanikani.com/v2/subjects"
    params = {"ids":",".join(map(str, ids))}

    data = fetchAndParseUrl(url, params)
    subjects = jmespath.search('data[*].{type: object, data: data}', data)

    print("Found subjects in page: {subjpage}".format(subjpage=len(subjects)))

    return subjects

def getNoteInfo(col, note_id):

    note = col.get_note(note_id)
    return note["Character"]


def createMissingNotes(col, subjects, existing_characters):

    note_type = col.models.get(col.models.id_for_name("FloKanjiOnly"))
    did = col.decks.id("Kanji")

    missing_subjects = [v for v in subjects if v["data"]["slug"] not in existing_characters]
    for subj in missing_subjects:

        print("Adding new Kanji: {character}".format(character = subj["data"]["slug"]))

        note_new = col.newNote(note_type)
        note_new["Character"] = subj["data"]["slug"]
        #note_new["Radicals"] = subj["data"]["slug"]
        
        note_new["Meaning"] = next((v["meaning"] for v in subj["data"]["meanings"] if v["primary"] == True), "")
        note_new["MeaningMnemonic"] = subj["data"]["meaning_mnemonic"] or ""
        note_new["MeaningHint"] = subj["data"]["meaning_hint"] or ""
        note_new["Reading"] = next((v["reading"] for v in subj["data"]["readings"] if v["primary"] == True), "")
        note_new["ReadingMnemonic"] = subj["data"]["reading_mnemonic"] or ""
        note_new["ReadingHint"] = subj["data"]["reading_hint"] or ""
        note_new["OtherMeanings"] = ", ".join([v["meaning"] for v in subj["data"]["meanings"] if v["primary"] == False])
        note_new["OtherReadings"] = ", ".join([v["reading"] for v in subj["data"]["readings"] if v["primary"] == False and v["type"] == "onyomi"])
        #note_new["SimilarKanjis"] = subj["data"]["slug"]

        col.add_note(note_new, did)


# Get Kanjis from WK
subjects = fetchSubjects()

# Open Anki Collection
col = Collection("{userhome}\\AppData\\Roaming\\Anki2\\User 1\\collection.anki2".format(userhome = Path.home()))
note_ids = col.find_notes("Deck:Kanji")
existing_characters = [getNoteInfo(col, v) for v in note_ids]
createMissingNotes(col, subjects, existing_characters)
col.close()