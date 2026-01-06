import ankilib, wksync
import yaml
from datetime import datetime, timedelta

config = yaml.safe_load(open("config.yaml"))

def sync_profile(name, wkkey, ankikey, syncVocabAfter: datetime.date = None, syncVocabLowerCase: bool = False, syncVocabEmptyWKID : bool = False):

    print("=== Starting sync [{name}] ===".format(name=name))

    col = ankilib.open_collection(name)
    ankilib.perform_sync(col, ankikey)
    ankilib.create_backup(col)

    # First, get all local IDs
    kanji_note_ids = col.find_notes("Deck:Kanji")
    radical_note_ids = col.find_notes("Deck:Radicals")
    vocab_note_ids = col.find_notes("Deck:Vocab note:VocabWithKanji")

    # When did we sync last? Take that date -10d to be safe
    max_vocab_nid =  max(nid for nid in vocab_note_ids)
    last_sync = datetime.fromtimestamp(max_vocab_nid / 1000.0) - timedelta(days=10)

    # Get Kanjis + Radicals from WK (get all)
    subjects = wksync.fetchSubjectsBySRS("kanji,radical", wkkey)
    kanjis = [v for v in subjects if v["type"] == "kanji"]
    radicals = [v for v in subjects if v["type"] == "radical"]
    
    # Update Kanjis in Anki
    existing_kanjislugs = [ankilib.getNoteInfo(col, v, "Character") for v in kanji_note_ids]
    ankilib.createMissingKanji(col, kanjis, existing_kanjislugs, radicals)

    # Update Radicals in Anki
    existing_radicalnames = [ankilib.getNoteInfo(col, v, "Name") for v in radical_note_ids]
    ankilib.createMissingRadicals(col, radicals, existing_radicalnames, kanjis)

    # Get Vocab from WK (only recent ones)
    subjects = wksync.fetchSubjectsBySRS("vocabulary", wkkey, last_sync, syncVocabAfter)
    vocab = [v for v in subjects if v["type"] == "vocabulary"]

    # Update Vocab in Anki
    existing_vocab = [ankilib.getNoteInfo(col, v, "WKID") for v in vocab_note_ids]
    ankilib.createMissingVocab(col, vocab, existing_vocab, kanjis, syncVocabLowerCase) 

    # Convert vocab with non-numeric WKID (= vocab string) to WKID, then sync with WK
    if syncVocabEmptyWKID:
        fix_vocab_strings = [ankilib.getNoteInfo(col, v, "Word") for v in vocab_note_ids if len(ankilib.getNoteInfo(col, v, "WKID")) == 0]
        fix_subjects = wksync.fetchVocabBySlug(fix_vocab_strings, wkkey)
        ankilib.update_vocab_by_word_set_wkid(col, fix_subjects, kanjis, syncVocabLowerCase)

    # Fix due dates + sync
    ankilib.fix_duedates(col)
    ankilib.perform_sync(col, ankikey)

    col.close()

    print("=== Finished sync [{name}] ===".format(name=name))

    return


# Perform action
for syncUser in config["Profiles"]:
    sync_profile(syncUser["profileName"], syncUser["waniKaniKey"], syncUser["ankiSyncAuth"], 
                  syncUser.get("syncVocabAfter", None), syncUser.get("syncVocabLowerCase", False),
                  syncUser.get("syncVocabEmptyWKID", False))