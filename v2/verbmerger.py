import ankilib
import yaml
import re

config = yaml.safe_load(open("config.yaml"))

profile = next((v["profileName"] for v in config["Profiles"] if v["profileName"] == "Flo"), "")

col = ankilib.open_collection(profile)

def merge_verbs(col):
    find_polite = "deck:Vocab tag:verb (English:he* OR English:she* OR English:it*)"
    notes_verb_dict_ids = col.find_notes("deck:Vocab tag:verb English:to* Kanji:_*")

    # Loop the dict ones
    processed = 0
    for dict_note_id in notes_verb_dict_ids:

        dict_note = col.get_note(dict_note_id)

        # Build potential polite matches group 1 (u, tsu, ru, bu, mu, nu, ku, gu, su) + 2 (ru)
        ext_list = [('う','います'), ('つ','ちます'), ('る','ります'), ('ぶ','びます'), ('む','みます'), ('ぬ','にます'), ('く','きます'), ('ぐ','ぎます'), ('す','します'), ('る','ます')]

        # Build combinations
        matching_endings = [e for e in ext_list if dict_note["Kanji"].endswith(e[0])]
        potential_polite = [dict_note["Kanji"][:len(dict_note["Kanji"])-1] + e[1] for e in matching_endings]
        #print(dict_note["Kanji"])
        #print(potential_polite)

        # Find the polite matches
        searches = find_polite + " (" + " OR ".join(["Kanji:{kanji}".format(kanji=p) for p in potential_polite]) + ")"
        results = col.find_notes(searches)

        # We only process if we have exactly 1 result
        if(len(results) == 1):
            
            # Get the polite note
            polite_note = col.get_note(results[0])
            #print(polite_note["Kanji"])

            # Get the cards
            for card_type in [c.ord for c in dict_note.cards()]:
                polite_cards = [c for c in polite_note.cards() if c.ord == card_type]
                dict_cards = [c for c in dict_note.cards() if c.ord == card_type]

                if(len(polite_cards) > 1 or len(dict_cards) > 1):
                    raise ValueError("Multiple cards founds")
                
                if(len(polite_cards) == 0):
                    raise ValueError("No matching card found for notes: {nid1}, {nid2}".format(nid1=polite_note.id, nid2=dict_note.id))

                polite_card = polite_cards[0]
                dict_card = dict_cards[0]

                # User lower due date on dict_card
                lower_due = due=min([polite_card.due, dict_card.due])
                dict_card.due = lower_due

                col.update_card(dict_card)

                print("Polite: {poldue}, Dict: {dictdue} => result: {due}".format(poldue=polite_card.due, dictdue=dict_card.due, due=min([polite_card.due, dict_card.due])))


            # Update dict note
            # We keep the English text of dict_card, but we need to update the reading + kanji
            dict_note["Kanji"] = "{dict} / {polite}".format(dict=dict_note["Kanji"], polite=polite_note["Kanji"])
            dict_note["Kana"] = "{dict} / {polite}".format(dict=dict_note["Kana"], polite=polite_note["Kana"])

            # Tag old note
            polite_note.add_tag("DEPRECATED")

            print(dict_note["English"])
            print(dict_note["Kanji"])
            print(dict_note["Kana"])
            processed += 1

            print("nid:{id1} OR nid:{id2}".format(id1=polite_note.id, id2=dict_note.id))

            col.update_note(dict_note)
            col.update_note(polite_note)

            break

        else:
            print("Won't process: {searches} => {results}".format(searches=searches, results=results))
        
        print(processed)
            
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

merge_verbs(col)