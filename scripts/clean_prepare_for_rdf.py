import json
import os
import unicodedata
import re
from typing import Callable
import owlready2 as owl
import types
from build_populated_ontology import get_all_jsons, JSON_DIRECTORY


def dict_iter_rec(obj, fn_condition: Callable, fn_apply: Callable) -> None:
    """Recherche récursivement les dictionnaires satisfaisant une condition et leur applique une fonction.

    Args:
        obj (dict): Objet dans lequel chercher récursivement des dictionnaires.
        fn_condition (Callable): Fonction pour identifier les objets sur lesquels appliquer `fn_apply`.
        fn_apply (Callable): Fonction à appliquer sur les objets satisfaisant `fn_condition`.

    Returns:
        None: Les objets sont modifiés in place.
    """
    if isinstance(obj, dict) and fn_condition(obj):
        fn_apply(obj)
    if isinstance(obj, dict):
        for i in obj.values():
            dict_iter_rec(i, fn_condition, fn_apply)
    elif isinstance(obj, (list, set, tuple)):
        for i in obj:
            dict_iter_rec(i, fn_condition, fn_apply)


def url_conformize(s: str) -> str:
    """Normalise une chaîne de caractères pour une URI.

    Args:
        s (str): Chaîne à nettoyer.

    Returns:
        str: Chaîne nettoyée.
    """
    s = unicodedata.normalize("NFC", s)
    s = re.sub("[_' ]+", "_", s)
    return "".join([c for c in s if c.isalnum() or c == "_"])


def normalize_obj_name(obj: dict) -> None:
    """Normalise l'attribut 'name' d'un dictionnaire.

    Args:
        obj (dict): Dictionnaire à nettoyer.
    """
    if "name" in obj:
        name = obj["name"]
    else:
        name = "undefined"
    name = url_conformize(name)
    obj["name"] = name


def clean_annotation_names(annotations: dict) -> None:
    """Normalise les clés 'name' dans les annotations.

    Args:
        annotations (dict): Annotations à normaliser.

    Returns:
        None
    """
    for key, ersatz in [
        ("feels", "emotions"),
        ("causedBy", "cause"),
        ("hasObject", "object"),
    ]:

        def missing_key_but_ersatz(d: dict) -> bool:
            return key not in d.keys() and ersatz in d.keys()

        def replace_ersatz_with_key(d: dict) -> None:
            d[key] = d[ersatz]
            d.pop(ersatz)

        dict_iter_rec(annotations, missing_key_but_ersatz, replace_ersatz_with_key)

    properties = {"hasObject", "causedBy", "takePlaceAt", "hasParticipant"}

    def has_any_prop(d: dict) -> bool:
        return bool(properties.intersection(d.keys()))

    def remove_nodict_prop(d: dict) -> None:
        for p in properties:
            if p in d.keys():
                obj = d[p]
                if isinstance(obj, list):
                    if len(obj) == 1:
                        d[p] = obj[0]
                elif isinstance(obj, str):
                    d[p] = {"name": obj}
                elif not isinstance(obj, dict):
                    d.pop(p)

    dict_iter_rec(annotations, has_any_prop, remove_nodict_prop)

    def has_id_or_name_key(d: dict) -> bool:
        return bool({"id", "name"}.intersection(d.keys()))

    dict_iter_rec(annotations, has_id_or_name_key, normalize_obj_name)


def rename_causedBy(annotations: dict) -> None:
    """Remplace 'causedByEvent' par 'causedBy'.

    Args:
        annotations (dict): Annotations dans lesquelles remplacer les noms de propriétés.

    Returns:
        None
    """

    def has_causedbyevent(d: dict) -> bool:
        return "causedByEvent" in d.keys()

    def rename_causedbyevent(d: dict) -> None:
        d["causedBy"] = d["causedByEvent"]
        d.pop("causedByEvent")

    dict_iter_rec(annotations, has_causedbyevent, rename_causedbyevent)


def unnest_places_events(annotations: dict) -> None:
    """Déplie et agrège les JSONs.

    Args:
        annotations (dict): Annotations à transformer.

    Returns:
        None
    """
    d = {}
    events = []
    places = []
    characters = annotations.get("FictionalCharacters")
    if characters:
        for c in characters:
            if "feels" in c:
                for emotions in c["feels"]:
                    if "causedBy" in emotions:
                        ev = emotions["causedBy"]
                        events.append(ev)
                        emotions["causedBy"] = {"name": ev["name"]}
        d["FictionalCharacters"] = characters
    for ev in events:
        if "takePlaceAt" in ev:
            pl = ev["takePlaceAt"]
            places.append(pl)
            ev["takePlaceAt"] = {"name": pl["name"]}
    annotations["Events"] = events
    annotations["Places"] = places


def add_unregistered_emotions() -> None:
    """Ajoute des émotions non enregistrées dans l'ontologie.

    Returns:
        None
    """
    curfile = os.path.realpath(__file__)
    root = os.path.dirname(os.path.dirname(curfile))
    base_onto = os.path.join(root, "ontology", "ontology.owl")
    base_onto_full = f"file://{base_onto}"

    onto = owl.get_ontology(base_onto_full).load()

    annotes = []
    emotions = set()
    for directory_name in os.listdir(JSON_DIRECTORY):
        annotes.extend(get_all_jsons(os.path.join(JSON_DIRECTORY, directory_name)))
    for a in annotes:
        x = a.get("FictionalCharacters")
        if x:
            for char in x:
                y = char.get("feels")
                if isinstance(y, list):
                    for emo in y:
                        if "name" in emo:
                            emotions.add(emo["name"])

    registered_emotions = set()
    unregistered = set()

    def rec_add_subclass(c):
        s = str(c)
        name = s[s.index(".") + 1 :]
        registered_emotions.add(name)
        for sub in c.subclasses():
            rec_add_subclass(sub)

    for i in onto.Emotion.subclasses():
        rec_add_subclass(i)

    for i in onto.classes():
        registered_emotions.add(str(i))

    for emo in emotions:
        if emo not in registered_emotions:
            unregistered.add(emo)

    with onto:
        for emo in unregistered:
            _ = types.new_class(emo, (onto.Emotion,))

    onto_extend_fp = base_onto.replace(".", "_extended.")
    onto.save(file=onto_extend_fp, format="rdfxml")


if __name__ == "__main__":
    dir_source = "data/annotations"
    dir_target = "data/annotations_cleaned"
    add_unregistered_emotions()
    quit(0)  # test

    for dirname in os.listdir(dir_source):
        d1 = os.path.join(dir_source, dirname)
        for filename in os.listdir(d1):
            fp1 = os.path.join(d1, filename)
            with open(fp1, "r") as f:
                try:
                    annote = json.load(f)
                except json.decoder.JSONDecodeError:
                    continue

            rename_causedBy(annote)
            clean_annotation_names(annote)
            unnest_places_events(annote)

            d2 = os.path.join(dir_target, dirname)
            if not os.path.isdir(d2):
                os.mkdir(d2)
            fp2 = os.path.join(d2, filename)
            with open(fp2, "w") as f:
                json.dump(obj=annote, fp=f, indent=1, ensure_ascii=False)
