from anki.collection import Collection
from pathlib import Path
from pyquery import PyQuery as pq
import wksync

colpath = "{userhome}\\AppData\\Roaming\\Anki2\\{profile}\\collection.anki2"

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
        
        usingkanjis = ["{k}: {d}".format(k=v["data"]["slug"], d=getPrimaryMeaning(v)) for v in kanjis if v["id"] in subj["data"]["amalgamation_subject_ids"]]
        note["Kanjis"] = ", ".join(usingkanjis)

        subjchars = subj["data"]["characters"]
        if subjchars is not None and len(subjchars) > 0:
            note["Image"] = subjchars
        else:
            url = next((v["url"] for v in subj["data"]["character_images"] if v["content_type"] == "image/svg+xml"), "")
            svgcode = wksync.fetchAndParseUrl(url, {}, lambda p: p.text)
            doc = pq(svgcode)
            svg = doc[0]
            svg.attrib["width"] = "80px"
            svg.attrib["style"] = "background-color:transparent"

            note["Image"] = doc.outerHtml().replace("#000", "white")

        col.update_note(note)

def createMissingVocab(col, vocab, existing_vocab, kanjis):

    note_type = col.models.by_name("VocabWithKanji")
    did = col.decks.id("Kanji")

    for subj in vocab:

        word = subj["data"]["characters"]

        note = None
        if word in existing_vocab:
            exnotesids = col.find_notes("Deck:Kanji Word:{word}".format(word=word))
            if(len(exnotesids) != 1):
                raise Exception("More than one note to update found: {word}".format(word = word))
            note = col.get_note(exnotesids[0])
            # print("Updating Vocab: {word}".format(word = word))
        else:
            note = col.new_note(note_type)
            note["Word"] = word
            col.add_note(note, did)
            print("Adding new Vocab: {word}".format(word = word))


        used_kanji = [v["data"]["slug"] for v in kanjis if v["id"] in subj["data"]["component_subject_ids"]]
        note["UsedKanji"] = ", ".join(used_kanji)
        
        note["Meaning"] = getPrimaryMeaning(subj)
        note["Reading"] = next((v["reading"] for v in subj["data"]["readings"] if v["primary"] == True), "")
        note["OtherMeanings"] = ", ".join([v["meaning"] for v in subj["data"]["meanings"] if v["primary"] == False])
        note["OtherReadings"] = ", ".join([v["reading"] for v in subj["data"]["readings"] if v["primary"] == False])
        
        col.update_note(note)