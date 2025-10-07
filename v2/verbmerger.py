import ankilib
import yaml
import re

config = yaml.safe_load(open("config.yaml"))

profile = next((v["profileName"] for v in config["Profiles"] if v["profileName"] == "Flo"), "")

col = ankilib.open_collection(profile)

# Open setdeck vocabulary
# vocab_note_ids = col.find_notes("Deck:Vocab note:VocabWithKanji")

def merge_verbs(col):
    find_polite = "deck:Vocab tag:verb (English:he* OR English:she* OR English:it*)"
    notes_verb_dict_ids = col.find_notes("deck:Vocab tag:verb (English:to*)")

    # Loop the dict ones
    for dict_note_id in notes_verb_dict_ids:

        dict_note = col.get_note(dict_note_id)

        # Find the polite match
        # Build potential polite matches group 1
        


def fix_tags(col):
    notes_with_tags = col.find_notes("tag:_* tag:*,*")
    for note_id in notes_with_tags:
        note = col.get_note(note_id)

        print("{key}".format(key=note_id))
        print("{key}".format(key=note.tags))

        tags_string = note.string_tags() 
            
        tags_list = [s.strip() for s in re.split("\s|,", tags_string)]
        tags_list = [s for s in tags_list if len(s) > 0]
        note.tags.clear()

        for tag in tags_list:
            note.add_tag(tag)

        print("{key}".format(key=note.tags))
        col.update_note(note)
