import ankilib, wksync
import yaml

config = yaml.safe_load(open("config.yaml"))

def sync_profile(name, wkkey, ankikey, syncvocab: bool):

    print("=== Starting sync [{name}] ===".format(name=name))

    col = ankilib.open_collection(name)
    ankilib.perform_sync(col, ankikey)
    ankilib.create_backup(col)

    subjects = wksync.fetchSubjects("kanji,radical", wkkey)
    kanjis = [v for v in subjects if v["type"] == "kanji"]
    radicals = [v for v in subjects if v["type"] == "radical"]
    
    kanji_note_ids = col.find_notes("Deck:Kanji")
    existing_kanjislugs = [ankilib.getNoteInfo(col, v, "Character") for v in kanji_note_ids]
    ankilib.createMissingKanji(col, kanjis, existing_kanjislugs, radicals)

    radical_note_ids = col.find_notes("Deck:Radicals")
    existing_radicalnames = [ankilib.getNoteInfo(col, v, "Name") for v in radical_note_ids]
    ankilib.createMissingRadicals(col, radicals, existing_radicalnames, kanjis)

    if(syncvocab):
        subjects = wksync.fetchSubjects("vocabulary", wkkey)
        vocab = [v for v in subjects if v["type"] == "vocabulary"]

        vocab_note_ids = col.find_notes("Deck:Vocab note:VocabWithKanji")
        existing_vocab = [ankilib.getNoteInfo(col, v, "WKID") for v in vocab_note_ids]
        ankilib.createMissingVocab(col, vocab, existing_vocab, kanjis) 

    ankilib.fix_duedates(col)
    ankilib.perform_sync(col, ankikey)

    col.close()

    print("=== Finished sync [{name}] ===".format(name=name))

    return


# Perform action
for syncUser in config["Profiles"]:
    sync_profile(syncUser["profileName"], syncUser["waniKaniKey"], syncUser["ankiSyncAuth"], syncUser["syncVocab"])