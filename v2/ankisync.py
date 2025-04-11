import ankilib, wksync
import yaml

config = yaml.safe_load(open("config.yaml"))

def syncNilay():
    col = ankilib.open_collection(config['profileNameNilay'])
    subjects = wksync.fetchSubjects("kanji,radical,vocabulary", config['waniKaniKeyNilay'])
    kanjis = [v for v in subjects if v["type"] == "kanji"]
    radicals = [v for v in subjects if v["type"] == "radical"]
    vocab = [v for v in subjects if v["type"] == "vocabulary"]

    kanji_note_ids = col.find_notes("Deck:Kanji")
    existing_kanjislugs = [ankilib.getNoteInfo(col, v, "Character") for v in kanji_note_ids]
    ankilib.createMissingKanji(col, kanjis, existing_kanjislugs, radicals)

    radical_note_ids = col.find_notes("Deck:Radicals")
    existing_radicalnames = [ankilib.getNoteInfo(col, v, "Name") for v in radical_note_ids]
    ankilib.createMissingRadicals(col, radicals, existing_radicalnames, kanjis)

    vocab_note_ids = col.find_notes("Deck:Vocab note:VocabWithKanji")
    existing_vocab = [ankilib.getNoteInfo(col, v, "Word") for v in vocab_note_ids]
    ankilib.createMissingVocab(col, vocab, existing_vocab, kanjis) 

    col.close()


def syncFlo():
    col = ankilib.open_collection(config['profileNameFlo'])

    subjects = wksync.fetchSubjects("kanji,radical", config['waniKaniKeyFlo'])
    kanjis = [v for v in subjects if v["type"] == "kanji"]
    radicals = [v for v in subjects if v["type"] == "radical"]

    kanji_note_ids = col.find_notes("Deck:Kanji")
    existing_kanjislugs = [ankilib.getNoteInfo(col, v, "Character") for v in kanji_note_ids]
    ankilib.createMissingKanji(col, kanjis, existing_kanjislugs, radicals)

    radical_note_ids = col.find_notes("Deck:Radicals")
    existing_radicalnames = [ankilib.getNoteInfo(col, v, "Name") for v in radical_note_ids]
    ankilib.createMissingRadicals(col, radicals, existing_radicalnames, kanjis)

    ankilib.fix_duedates(col)

    col.close()


# Sync Flo
syncNilay()