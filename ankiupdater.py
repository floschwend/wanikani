from anki.collection import Collection
from datetime import timedelta, date
import itertools
from collections import namedtuple
from pathlib import Path

GroupKey = namedtuple("GroupKey", ["note_id", "due_date"])

class CardInfo(object):
    pass

def get_card_info(col, card_id):
    card = col.get_card(card_id)
    duedays = card.due - col.sched.today
    info = CardInfo()
    info.card_id = card_id
    info.due = card.due
    info.due_date = date.today() + timedelta(days=duedays)
    info.note_id = card.note().id
    info.english = card.note()["English"]
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



col = Collection("{userhome}\\AppData\\Roaming\\Anki2\\User 1\\collection.anki2".format(userhome = Path.home()))
card_ids = col.find_cards("deck:Duolingo -is:new -is:suspended")
cards = [get_card_info(col, v) for v in card_ids]
sorted_cards = sorted(cards, key=lambda x: (x.note_id, x.due_date, x.ord))

groups = [(k, list(g)) for k, g in itertools.groupby(sorted_cards, lambda x: GroupKey(x.note_id, x.due_date))]

duplicates = [(k, g) for k, g in groups if len(g) >= 2]

print("{0} duplicates found".format(len(duplicates)))

for key, group in duplicates:
    update_cards(col, group)

col.close()