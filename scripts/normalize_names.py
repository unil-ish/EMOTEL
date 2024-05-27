import json
import os
import unicodedata
import re


def clean_name(s):
    """character's name -> character_s_name"""

    s = re.sub("[_' ]+", "_", s)
    return "".join([c for c in s if c.isalpha() or c == "_"])


def clean_obj(obj) -> None:
    """clean la clé 'name' d'un dict."""

    if "name" in obj:
        name = clean_name(obj["name"])
    elif "id" in obj:
        name = clean_name(obj["id"])
    else:
        name = "undefined"
    obj["name"] = unicodedata.normalize("NFC", name)
    return


def clean_annotation_names(annotations):
    """clean les clés 'name' de tous les objets concernés."""

    for key in ("Places", "Events", "FictionalCharacters"):
        if key in annotations.keys():
            for obj in annotations[key]:
                clean_obj(obj)
    if "FictionalCharacters" in annotations.keys():
        for c in annotations["FictionalCharacters"]:
            if "feels" not in c:
                if "emotions" in c:
                    c["feels"] = c["emotions"]
                    c.pop("emotions")
                else:
                    continue
            emotions = [em for em in c["feels"] if isinstance(em, dict)]
            for em in emotions:
                if "causedBy" in em:
                    pass
                elif "cause" in em:
                    em["causedBy"] = em["cause"]
                    em.pop("cause")
                else:
                    continue
                if isinstance(em["causedBy"], dict):
                    clean_obj(em["causedBy"])
                else:
                    em.pop("causedBy")
            c["feels"] = emotions
    return annotations


if __name__ == "__main__":
    dir_source = "../data/annotations"
    dir_target = "../data/annotations_unique_ids"

    for dirname in os.listdir(dir_source):
        d1 = os.path.join(dir_source, dirname)
        for filename in os.listdir(d1):
            fp1 = os.path.join(d1, filename)
            with open(fp1, "r") as f:
                try:
                    c = json.load(f)
                except json.decoder.JSONDecodeError:
                    continue
            clean_annotation_names(c)
            d2 = os.path.join(dir_target, dirname)
            if not os.path.isdir(d2):
                os.mkdir(d2)
            fp2 = os.path.join(d2, filename)
            with open(fp2, "w") as f:
                json.dump(obj=c, fp=f, indent=1, ensure_ascii=False)
