import json
import os
import unicodedata
import re


def clean_name(s: str) -> str:
    """Nettoie le nom en remplaçant les espaces et caractères spéciaux par des underscores.

    Args:
        s (str): Le nom à nettoyer.

    Returns:
        str: Le nom nettoyé.
    """
    s = re.sub("[_' ]+", "_", s)
    return "".join([c for c in s if c.isalpha() or c == "_"])


def clean_obj(obj: dict) -> None:
    """Normalise le nom d'un objet.

    Args:
        obj (dict): L'objet à nettoyer.
    """
    if "name" in obj:
        name = obj['name']
    elif "id" in obj:
        name = obj["id"]
    else:
        name = "undefined"
    name = clean_name(name)
    obj["name"] = unicodedata.normalize("NFC", name)


def clean_annotation_names(annotations: dict) -> dict:
    """Nettoie les clés 'name' de tous les objets concernés dans les annotations.

    Args:
        annotations (dict): Les annotations à nettoyer.

    Returns:
        dict: Les annotations nettoyées.
    """
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
                for key, ersatz in [("causedBy", 'cause'), ('hasObject', 'object')]:
                    if key in em:
                        pass
                    elif ersatz in em:
                        em[key] = em[ersatz]
                        em.pop(ersatz)
                    else:
                        continue
                    if isinstance(em[key], dict):
                        clean_obj(em[key])
                    else:
                        em.pop(key)
            c["feels"] = emotions
    return annotations


if __name__ == "__main__":
    dir_source = "../data/annotations"
    dir_target = "../data/annotations_cleaned"

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
