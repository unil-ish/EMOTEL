import json
import os
import unicodedata
import re


def url_conformize(s) -> str:
    """Normalise une chaîne de caractère pour qu'elle puisse être integrée à une URI.

    Args:
        s (str): Le nom à nettoyer.

    Returns:
        str: Le nom nettoyé.
    """

    s = unicodedata.normalize("NFC", s)
    s = re.sub("[_' ]+", "_", s)
    return "".join([c for c in s if c.isalnum() or c == "_"])


def clean_obj(obj) -> None:
    """Normalise les attributs 'name' et 'id' d'un objet (dict).

    Args:
        obj (dict): L'objet à nettoyer.
    """

    if "id" in obj:
        obj["id"] = url_conformize(obj["id"])

    if "name" in obj:
        name = obj["name"]
    elif "id" in obj:
        # si 'name' est manquant, c'est en fait toujours l'id qui contient le nom. il suffit donc de le réassigner.
        name = obj["id"]
    else:
        name = "undefined"
    # la fonction qui enlève notamment les espaces.
    name = url_conformize(name)

    obj["name"] = name
    return


def clean_annotation_names(annotations) -> None:
    """Normalise les clés 'name' de tous les objets concernés dans les annotations.

    Args:
        annotations (dict): Les annotations à normaliser.

    Returns:
        None
    """

    # les objets qui se trouvent directement dans 'Places', 'Events', 'FictionalCharacters' sont facile à traiter, on utilise donc simplement la fonction 'clean_obj'.
    for key in ("Places", "Events", "FictionalCharacters"):
        if key in annotations.keys():
            for obj in annotations[key]:
                clean_obj(obj)

    # en revanche, les objets qui concernent les émotions sont plus chaotiques. donc la construction ici correspond aussi à ce nettoyage.
    if "FictionalCharacters" in annotations.keys():
        for c in annotations["FictionalCharacters"]:
            # le premier souci possible, c'est lorsque 'feels' est remplacé par 'emotions'.
            if "feels" not in c:
                if "emotions" in c:
                    c["feels"] = c["emotions"]
                    c.pop("emotions")
                else:
                    continue
            # le second souci, c'est les émotions qui ne sont pas des objets JSONs (dict en python), comme c'est trop aléatoire à gérer, on ne conserve que les 'dict'.
            emotions = [em for em in c["feels"] if isinstance(em, dict)]
            for em in emotions:
                # le troisième souci, c'est quand les clés 'causedBy' ou 'hasObject' sont soit absentes, soit remplacées, respectivement par 'cause' et 'object'. on normalize en mettant la clé canonique correspondante.
                for key, ersatz in [
                    ("causedBy", "cause"),
                    ("hasObject", "object"),
                ]:
                    if key in em:
                        pass
                    elif ersatz in em:
                        em[key] = em[ersatz]
                        em.pop(ersatz)
                    else:
                        continue
                    # dans les 'hasObject' et 'causesBy' aussi, parfois il n'y a pas d'objet JSONs. idem que pour les emotions: on ne conserve que les dicts.
                    if isinstance(em[key], dict):
                        clean_obj(em[key])
                    else:
                        em.pop(key)
            c["feels"] = emotions
    if "Events" in annotations.keys():
        normalise_events(annotations["Events"])
    return


def normalise_events(events):
    for ev in events:
        for key in ("takePlaceAt", "hasParticipant"):
            if key in ev:
                if isinstance(ev[key], dict):
                    clean_obj(ev[key])
                else:
                    ev.pop(key)
    return


def add_missing_names(annote):
    ids = {}
    # d'abord, récupérer les ids de ce qui se trouve dans le fichiers d'annotations, à savoir: les ids des Places et FictionalCharacters, afin de pouvoir mettre les 'name' correspondant dans les sous-sous-clés de Events.
    for key in ("FictionalCharacters", "Places"):
        if key in annote:
            obj = annote[key]
            for i in obj:
                if set(["name", "id"]).issubset(set(i.keys())):
                    name = i["name"]
                    _id = i["id"]
                    ids[_id] = name
                else:
                    print(i.keys())
    # deuxième étape: mettre ces noms là où ils manquent
    if "Events" in annote:
        for ev in annote["Events"]:
            for key in ("hasParticipant", "takePlaceAt"):
                if key in ev:
                    obj = ev[key]
                    if isinstance(obj, dict):
                        obj["name"] = ids[obj["id"]]
    return


if __name__ == "__main__":
    dir_source = "../data/annotations"
    dir_target = "../data/annotations_cleaned"

    # la structure ci-dessous ne sert qu'à une seule chose: appliquer sur chaque fichier d'annotations les fonctions du présent module, et écrire le résultat dans un nouveau fichier, avec le même nom mais dans un autre dossier.
    for dirname in os.listdir(dir_source):
        d1 = os.path.join(dir_source, dirname)
        for filename in os.listdir(d1):
            fp1 = os.path.join(d1, filename)
            with open(fp1, "r") as f:
                try:
                    annote = json.load(f)
                except json.decoder.JSONDecodeError:
                    continue

            # première fonction: clean les noms
            clean_annotation_names(annote)
            # seconde fonction: ajouter les noms là où ils manquent, en utilisant les ids.
            # add_missing_names(annote)

            d2 = os.path.join(dir_target, dirname)
            if not os.path.isdir(d2):
                os.mkdir(d2)
            fp2 = os.path.join(d2, filename)
            with open(fp2, "w") as f:
                json.dump(obj=annote, fp=f, indent=1, ensure_ascii=False)
