from anki.collection import Collection
import jmespath
from pathlib import Path
import requests
import yaml
from pyquery import PyQuery as pq

config = yaml.safe_load(open("config.yaml"))

def fetchAndParseUrl(url, params, return_method):

    print("Fetching: {url} with params {params}".format(url= url, params = params))
    
    headers = {"Wanikani-Revision": "20170710", "Authorization": "Bearer {key}".format(key= config['waniKaniKeyUser2'])}

    try:
        resp = requests.get(url=url, params=params, headers=headers)
        data = return_method(resp)

        return data

    except Exception as inst:
        print("Exception in fetchAndParseUrl: {msg}".format(msg = inst))
    
def fetchAssignmentsPage(url, params):  
    data = fetchAndParseUrl(url, params, lambda p: p.json())

    assignments = jmespath.search('data[*].data', data)

    print("Found assignments in page: {number}".format(number= len(assignments)))

    next = data["pages"]["next_url"]
    if next is not None:
        newAssignments = fetchAssignmentsPage(next, {})   #empty params as the URL already contains them
        assignments += newAssignments 

    return assignments

def fetchSubjects():

    url = "https://api.wanikani.com/v2/assignments"
    params = {"srs_stages": ','.join(str(i) for i in range(1,10)), "subject_types":"kanji,radical"}

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

    data = fetchAndParseUrl(url, params, lambda p: p.json())
    subjects = jmespath.search('data[*].{id: id, type: object, data: data}', data)

    print("Found subjects in page: {subjpage}".format(subjpage=len(subjects)))

    return subjects

def getNoteInfo(col, note_id, key):

    note = col.get_note(note_id)
    return note[key]


def getPrimaryMeaning(kanji):
    return next((v["meaning"] for v in kanji["data"]["meanings"] if v["primary"] == True), "")

def createMissingKanji(col, kanjis, existing_characters, radicals):

    note_type = col.models.by_name("FloKanjiOnly")
    did = col.decks.id("Kanji")

    for subj in kanjis:

        kanjichar = subj["data"]["slug"]

        note = None
        if kanjichar in existing_characters:
            exnotesids = col.find_notes("Deck:Kanji Character:{kanjichar}".format(kanjichar=kanjichar))
            if(len(exnotesids) != 1):
                raise Exception("More than one note to update found: {kanjichar}".format(kanjichar = kanjichar))
            note = col.get_note(exnotesids[0])
            # print("Updating Kanji: {character}".format(character = kanjichar))
        else:
            note = col.new_note(note_type)
            note["Character"] = kanjichar
            col.add_note(note, did)
            print("Adding new Kanji: {character}".format(character = kanjichar))


        radicals_kanji = [v["data"]["slug"] for v in radicals if v["id"] in subj["data"]["component_subject_ids"]]
        note["Radicals"] = ", ".join(radicals_kanji)
        
        note["Meaning"] = getPrimaryMeaning(subj)
        note["MeaningMnemonic"] = subj["data"]["meaning_mnemonic"] or ""
        note["MeaningHint"] = subj["data"]["meaning_hint"] or ""
        note["Reading"] = next((v["reading"] for v in subj["data"]["readings"] if v["primary"] == True), "")
        note["ReadingType"] = next((v["type"] for v in subj["data"]["readings"] if v["primary"] == True), "")
        note["ReadingMnemonic"] = subj["data"]["reading_mnemonic"] or ""
        note["ReadingHint"] = subj["data"]["reading_hint"] or ""
        note["OtherMeanings"] = ", ".join([v["meaning"] for v in subj["data"]["meanings"] if v["primary"] == False])
        note["OtherReadings"] = ", ".join([v["reading"] for v in subj["data"]["readings"] if v["primary"] == False and v["type"] == "onyomi"])
        
        
        similar = ["{k}: {d}".format(k=v["data"]["slug"], d=getPrimaryMeaning(v)) for v in kanjis if v["id"] in subj["data"]["visually_similar_subject_ids"]]
        note["SimilarKanjis"] = ", ".join(similar)

        col.update_note(note)


def createMissingRadicals(col, radicals, existing_characters, kanjis):

    note_type = col.models.by_name("FloRadicalOnly")
    did = col.decks.id("Radicals")

    for subj in radicals:

        name = subj["data"]["slug"]

        note = None
        if name in existing_characters:
            exnotesids = col.find_notes("Deck:Radicals Name:{name}".format(name=name))
            if(len(exnotesids) != 1):
                raise Exception("More than one note to update found: {name}".format(name = name))
            note = col.get_note(exnotesids[0])
            # print("Updating Radical: {name}".format(name = name))
        else:
            note = col.new_note(note_type)
            note["Name"] = name
            col.add_note(note, did)
            print("Adding new Radical: {name}".format(name = name))


        note["Meaning"] = getPrimaryMeaning(subj)
        note["MeaningMnemonic"] = subj["data"]["meaning_mnemonic"] or ""
        
        usingkanjis = ["{k}: {d}".format(k=v["data"]["slug"], d=getPrimaryMeaning(v)) for v in kanjis if v["id"] in subj["data"]["amalgamation_subject_ids"]]
        note["Kanjis"] = ", ".join(usingkanjis)

        subjchars = subj["data"]["characters"]
        if subjchars is not None and len(subjchars) > 0:
            note["Image"] = subjchars
        else:
            url = next((v["url"] for v in subj["data"]["character_images"] if v["content_type"] == "image/svg+xml"), "")
            svgcode = fetchAndParseUrl(url, {}, lambda p: p.text)
            doc = pq(svgcode)
            svg = doc[0]
            svg.attrib["width"] = "80px"
            svg.attrib["style"] = "background-color:transparent"

            note["Image"] = doc.outerHtml().replace("#000", "white")

        col.update_note(note)



# Get Kanjis from WK
subjects = fetchSubjects()
kanjis = [v for v in subjects if v["type"] == "kanji"]
radicals = [v for v in subjects if v["type"] == "radical"]

# Open Anki Collection
col = Collection("{userhome}\\AppData\\Roaming\\Anki2\\Flo\\collection.anki2".format(userhome = Path.home()))

kanji_note_ids = col.find_notes("Deck:Kanji")
existing_kanjislugs = [getNoteInfo(col, v, "Character") for v in kanji_note_ids]
createMissingKanji(col, kanjis, existing_kanjislugs, radicals)

radical_note_ids = col.find_notes("Deck:Radicals")
existing_radicalnames = [getNoteInfo(col, v, "Name") for v in radical_note_ids]
createMissingRadicals(col, radicals, existing_radicalnames, kanjis)

col.close()