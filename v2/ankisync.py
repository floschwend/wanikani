import ankilib, wksync

# Sync Nilay
#col = ankilib.open_collection("Nilay")
#subjects = wksync.fetchSubjects("kanji,radical,vocabulary")
#col.close()

# Sync Flo
col = ankilib.open_collection("Flo")

subjects = wksync.fetchSubjects("kanji,radical")
kanjis = [v for v in subjects if v["type"] == "kanji"]
radicals = [v for v in subjects if v["type"] == "radical"]

kanji_note_ids = col.find_notes("Deck:Kanji")
existing_kanjislugs = [wksync.getNoteInfo(col, v, "Character") for v in kanji_note_ids]
ankilib.createMissingKanji(col, kanjis, existing_kanjislugs, radicals)

radical_note_ids = col.find_notes("Deck:Radicals")
existing_radicalnames = [wksync.getNoteInfo(col, v, "Name") for v in radical_note_ids]
ankilib.createMissingRadicals(col, radicals, existing_radicalnames, kanjis)

col.close()