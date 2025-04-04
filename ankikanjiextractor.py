from anki.collection import Collection
from pathlib import Path

def getNoteInfo(col, note_id, key):

    note = col.get_note(note_id)
    return note[key]

# Open Anki Collection
col = Collection("{userhome}\\AppData\\Roaming\\Anki2\\User 1\\collection.anki2".format(userhome = Path.home()))

kanji_note_ids = col.find_notes("Deck:Kanji")
existing_kanjislugs = [getNoteInfo(col, v, "Character") for v in kanji_note_ids]

kanjis = ",".join(existing_kanjislugs)

print(kanjis)

col.close()