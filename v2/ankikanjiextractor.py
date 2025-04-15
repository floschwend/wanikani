import wksync
import yaml
import itertools
from collections import namedtuple

GroupKey = namedtuple("GroupKey", ["note_id", "due_date"])

class ReadingInfo(object):
    pass

# TODO: refactor into wksync (also usage in ankilib)
def get_primary_meaning(kanji):
    return next((v["meaning"] for v in kanji["data"]["meanings"] if v["primary"] == True), "")

def get_reading_infos(subject):

    meaning = get_primary_meaning(subject)
    kanji = subject["data"]["slug"]

    readings = []

    for reading in subject["data"]["readings"]:
        info = ReadingInfo()
        info.kanji = kanji
        info.meaning = meaning
        info.reading = reading["reading"]
        info.type = reading["type"]
        readings.append(info)

    return readings

def print_readings(type):

    print("=== {type} ===".format(type=type))
    filtered_cards = [v for v in readings if v.type == type]

    sorted_cards = sorted(filtered_cards, key=lambda x: (x.reading))
    groups = [(k, list(g)) for k, g in itertools.groupby(sorted_cards, lambda x: x.reading)]

    for (key, values) in groups:
        kanjis = ["{char} ({name})".format(char=v.kanji, name=v.meaning) for v in values]
        print("{key}: {values}".format(key=key, values=", ".join(kanjis)))

config = yaml.safe_load(open("config.yaml"))

wkkey = next((v["waniKaniKey"] for v in config["Profiles"] if v["profileName"] == "Flo"), "")

subjects = wksync.fetchSubjects("kanji", wkkey)

readings = []
for subject in subjects:
    readings += get_reading_infos(subject)

# Onyomi
print_readings("onyomi")
print_readings("kunyomi")