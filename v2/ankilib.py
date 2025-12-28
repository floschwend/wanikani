from anki.collection import Collection
from pathlib import Path
from pyquery import PyQuery as pq
from datetime import timedelta, date
import itertools
from collections import namedtuple
from anki.sync import SyncAuth 
from threading import Thread
import os

colpath = "{userhome}\\AppData\\Roaming\\Anki2\\{profile}\\collection.anki2"
GroupKey = namedtuple("GroupKey", ["note_id", "due_date"])

class CardInfo(object):
    pass

def perform_sync_thread(col: Collection, hkey):
    result = col.sync_collection(SyncAuth(hkey=hkey), True)
    print(result)

def perform_sync(col: Collection, hkey):
    # auth = col.sync_login("email", "pw", None)
    t = Thread(target = perform_sync_thread, args = (col, hkey))
    t.start()
    t.join()

def create_backup(col: Collection):
    col_folder = os.path.dirname(col.path)
    backup_folder = os.path.join(col_folder, "backups")
    col.create_backup(backup_folder=backup_folder, force=False, wait_for_completion=True)

def open_collection(profile):
    col = Collection(colpath.format(userhome = Path.home(), profile = profile))
    return col

def getPrimaryMeaning(kanji):
    return next((v["meaning"] for v in kanji["data"]["meanings"] if v["primary"] == True), "")

def createMissingKanji(col, kanjis, existing_characters, radicals):

    note_type = col.models.by_name("KanjiOnly")
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


        radicals_kanji = ["{char}".format(char=v["data"]["slug"]) 
                          for v in radicals if v["id"] in subj["data"]["component_subject_ids"]]
        note["Radicals"] = ", ".join(radicals_kanji)
        
        note["Meaning"] = getPrimaryMeaning(subj)
        note["MeaningMnemonic"] = subj["data"]["meaning_mnemonic"] or ""
        note["MeaningHint"] = subj["data"]["meaning_hint"] or ""
        note["Reading"] = next((v["reading"] for v in subj["data"]["readings"] if v["primary"] == True), "")
        note["ReadingType"] = next((v["type"] for v in subj["data"]["readings"] if v["primary"] == True), "")
        note["ReadingMnemonic"] = subj["data"]["reading_mnemonic"] or ""
        note["ReadingHint"] = subj["data"]["reading_hint"] or ""
        note["OtherMeanings"] = ", ".join([v["meaning"] for v in subj["data"]["meanings"] if v["primary"] == False and v["accepted_answer"] == True])
        note["OtherReadings"] = ", ".join([v["reading"] for v in subj["data"]["readings"] if v["primary"] == False and v["accepted_answer"] == True])
        note["URL"] = subj["data"]["document_url"]
        
        similar = ["{k}: {d}".format(k=v["data"]["slug"], d=getPrimaryMeaning(v)) for v in kanjis if v["id"] in subj["data"]["visually_similar_subject_ids"]]
        note["SimilarKanjis"] = ", ".join(similar)

        col.update_note(note)


def createMissingRadicals(col, radicals, existing_characters, kanjis):

    note_type = col.models.by_name("RadicalOnly")
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
        note["URL"] = subj["data"]["document_url"]
        
        usingkanjis = ["{k}: {d}".format(k=v["data"]["slug"], d=getPrimaryMeaning(v)) for v in kanjis if v["id"] in subj["data"]["amalgamation_subject_ids"]]
        note["Kanjis"] = ", ".join(usingkanjis)

        subjchars = subj["data"]["characters"]
        if subjchars is not None and len(subjchars) > 0:
            note["Image"] = subjchars
        else:
            svgcode = subj["data"]["svgcode"]
            doc = pq(svgcode)
            svg = doc[0]
            svg.attrib["width"] = "80px"
            svg.attrib["style"] = "background-color:transparent"

            note["Image"] = doc.outerHtml().replace("#000", "white")

        col.update_note(note)

def createMissingVocab(col, vocab, existing_vocab, kanjis, syncVocabConjugateVerbs: bool, syncVocabLowerCase: bool):

    note_type = col.models.by_name("VocabWithKanji")
    did = col.decks.id("Vocab")

    for subj in vocab:

        wkid = str(subj["id"])
        word = subj["data"]["characters"]

        note = None
        if wkid in existing_vocab:
            exnotesids = col.find_notes("Deck:Vocab WKID:{wkid}".format(wkid=wkid))
            if(len(exnotesids) != 1):
                raise Exception("More than one note to update found: {wkid}".format(wkid = wkid))
            note = col.get_note(exnotesids[0])
            # print("Updating Vocab: {word}".format(word = word))
        else:
            note = col.new_note(note_type)
            note["WKID"] = wkid
            col.add_note(note, did)
            print("Adding new Vocab: {word}".format(word = word))

        note["Word"] = word

        used_kanji = ["{char} ({desc})".format(char=v["data"]["slug"], desc=getPrimaryMeaning(v)) 
                      for v in kanjis if v["id"] in subj["data"]["component_subject_ids"]]
        note["UsedKanji"] = ", ".join(used_kanji)

        keepOriginalVocabCase = False
        if syncVocabLowerCase:
            keepOriginalVocabCase = any(v for v in subj["data"]["parts_of_speech"] if v == "proper noun")
        
        note["Meaning"] = fix_meaning(getPrimaryMeaning(subj), keepOriginalVocabCase)
        note["Reading"] = next((v["reading"] for v in subj["data"]["readings"] if v["primary"] == True), "")
        note["OtherMeanings"] = ", ".join([fix_meaning(v["meaning"], keepOriginalVocabCase) for v in subj["data"]["meanings"] if v["primary"] == False])
        note["OtherReadings"] = ", ".join([v["reading"] for v in subj["data"]["readings"] if v["primary"] == False])
        note["URL"] = subj["data"]["document_url"]

        wordtypes = ", ".join([v for v in subj["data"]["parts_of_speech"]])
        note["Notes-Backside"] = wordtypes
        
        col.update_note(note)

def fix_meaning(meaning: str, keepOriginalVocabCase: bool):
    if keepOriginalVocabCase:
        return meaning
    return meaning.lower()

def get_card_info(col, card_id):
    card = col.get_card(card_id)
    duedays = card.due - col.sched.today
    if(duedays > 1000):
        duedays = 0
    info = CardInfo()
    info.card_id = card_id
    info.due = card.due
    info.due_date = date.today() + timedelta(days=duedays)
    info.note_id = card.note().id
    if(any(f["name"] == "English" for f in card.note_type()["flds"])):
        info.english = card.note()["English"]
    elif(any(f["name"] == "Meaning" for f in card.note_type()["flds"])):
        info.english = card.note()["Meaning"]
    info.ivl = card.ivl
    info.type = card.note_type()["tmpls"][card.ord]["name"]
    info.ord = card.ord
    return info

def get_anki_date(col, due):
    duedays = due - col.sched.today
    return date.today() + timedelta(days=duedays)

def update_cards(col, card_group):
    days = 0
    print("--- Note: {english} ({note_id})".format(english = card_group[0].english, note_id = card_group[0].note_id))
    for card in card_group:
        if(days == 0):
            print("Keeping [{0}] current due date".format(card.type))
        else:
            new_due = card.due + days
            print("Change [{type}] => Old: {old_date} ({old_due}), new: {new_date} ({new_due})".format(type= card.type, old_date = card.due_date, new_date = get_anki_date(col, new_due), old_due = card.due, new_due = new_due))
            
            ankicard = col.get_card(card.card_id)
            ankicard.due = new_due

            col.update_card(ankicard)
            print("Saved card {card_id}".format(card_id = card.card_id))
                    
        days += 1


def fix_duedates(col):
    card_ids = col.find_cards("deck:Vocab is:review prop:ivl>1") # only take the ones which have an interval > 1d
    numdupl = update_duedates(col, card_ids)
    while numdupl > 0:
        numdupl = update_duedates(col, card_ids)

def update_duedates(col, card_ids):

    cards = [get_card_info(col, v) for v in card_ids]
    sorted_cards = sorted(cards, key=lambda x: (x.note_id, x.due_date, x.ord))

    groups = [(k, list(g)) for k, g in itertools.groupby(sorted_cards, lambda x: GroupKey(x.note_id, x.due_date))]

    duplicates = [(k, g) for k, g in groups if len(g) >= 2]

    numdupl = len(duplicates)
    print("{0} duplicates found".format(numdupl))

    for key, group in duplicates:
        update_cards(col, group)
    
    return numdupl

def getNoteInfo(col, note_id, key):

    note = col.get_note(note_id)
    return note[key]