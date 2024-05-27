import json
import os
import unicodedata
import re
from typing import Callable


def dict_iter_rec(obj, fn_condition: Callable, fn_apply: Callable) -> None:
    """recherche récursivement les 'dict' satisfaisant une certaine condition et leur applique une fonction qui modifie ces dicts.

    Args:
        obj (dict): n'importe quel objet dans lequel chercher récursivement des dictionnaires satisfaisant à une condition.

        fn_condition (Callable): une fonction qui permet d'identifier les objets sur lesquels appliquer la fonction `fn_apply`.

        fn_apply (Callable): la fonction à appliquer sur les objets satisfaisant à la condition `fn_condition`.

    Returs:
        None: (les objets sont modifiés 'in place'.)
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
    """Normalise une chaîne de caractère pour qu'elle puisse être integrée à une URI.

    Args:
        s (str): Le nom à nettoyer.

    Returns:
        str: Le nom nettoyé.
    """

    s = unicodedata.normalize("NFC", s)
    s = re.sub("[_' ]+", "_", s)
    return "".join([c for c in s if c.isalnum() or c == "_"])


def normalize_obj_name(obj: dict) -> None:
    """Normalise l'attributs 'name' d'un objet (dict).

    Args:
        obj (dict): L'objet à nettoyer.
    """

    if "name" in obj:
        name = obj["name"]
    else:
        name = "undefined"
    # la fonction qui enlève notamment les espaces.
    name = url_conformize(name)

    obj["name"] = name
    return


def clean_annotation_names(annotations: dict) -> None:
    """Normalise les clés 'name' de tous les objets concernés dans les annotations.

    Args:
        annotations (dict): Les annotations à normaliser.

    Returns:
        None
    """

    # certaines clés sont remplacés par d'autres (ici appelés 'ersatz'). l'itération suivante assignes, dans les objets concernés, la valeur de l'ersatz (ex. 'cause') à la clé manquante (ex. 'causedBy').
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

        dict_iter_rec(
            obj=annotations,
            fn_condition=missing_key_but_ersatz,
            fn_apply=replace_ersatz_with_key,
        )

    # certaines propriétés qui devraient être des objets JSON (des dicts) n'en sont pas (par exemple, sont des str). s'il s'agit d'une string, on la remplace par un dict qui associe sa valeur à la clé 'name', s'il s'agit d'une liste et qu'il n'y a qu'un élément, alors on la remplace par ce premier élément.
    # les autres très rares cas sont des listes à plusieurs éléments, en fait, ce qui aurait été intéressant est d'en avoir d'avantage, en particulier pour 'hasParticipant' qui devrait souvent avoir une liste comme valeur. c'est probablement une amélioration possible de notre prompt.
    properties = set(
        [
            "hasObject",
            "causedBy",
            "takePlaceAt",
            "hasParticipant",
        ]
    )

    def has_any_prop(d):
        return properties.intersection(d.keys())

    def remove_nodict_prop(d):
        for p in properties:
            if p in d.keys():
                obj = d[p]
                if isinstance(obj, list):
                    if len(obj) == 1:
                        d[p] = obj[0]
                    else:
                        pass
                elif isinstance(obj, str):
                    d[p] = {"name": obj}
                elif isinstance(obj, dict):
                    pass
                else:
                    d.pop(p)

    dict_iter_rec(
        obj=annotations,
        fn_condition=has_any_prop,
        fn_apply=remove_nodict_prop,
    )

    def has_id_or_name_key(d):
        return set(["id", "name"]).intersection(d.keys())

    # utilisation d'une fonction (récursive) qui trouve tous les objets JSON (dict) qui ont au moins l'une des clés ['id', 'name'], et applique sur ces objets la fonction de normalisation.
    dict_iter_rec(
        obj=annotations,
        fn_condition=has_id_or_name_key,
        fn_apply=normalize_obj_name,
    )

    return


def rename_causedBy(annotations: dict) -> None:
    """remplace la propriété 'causedByEvent' par 'causedBy'.

    l'usage de 'causedByEvent' comme nom de propriété dans le prompt est simplement destiné à faire comprendre à ChatGPT que la nature de la cause est un évenement. cette fonction remplace ce nom par le nom de la propriété correspondante dans notre ontologie.

    Args:
        annotations (dict): l'objet JSON des annotations dans lequel remplacer les noms de proprétés.

    Returns:
        None
    """

    def has_causedbyevent(d: dict) -> bool:
        return "causedByEvent" in d.keys()

    def rename_causedbyevent(d: dict) -> None:
        d["causedBy"] = d["causedByEvent"]
        d.pop("causedByEvent")

    dict_iter_rec(
        obj=annotations,
        fn_condition=has_causedbyevent,
        fn_apply=rename_causedbyevent,
    )


def unnest_places_events(annotations):
    """déplie et aggrège les JSONS:

    la structure des JSONS produits par ChatGPT est constituée d'objets et d'arrays imbriquées. ce script les 'déplie', applatit la structure pour faciliter les scripts qui peuplent l'ontologie.
    """

    d = {}
    events = []
    places = []
    characters = annotations.get("FictionalCharacters")
    if characters is not None:
        for c in characters:
            if "feels" in c.keys():
                for emotions in c["feels"]:
                    if "causedBy" in emotions.keys():
                        ev = emotions["causedBy"]
                        events.append(ev)
                        emotions["causedBy"] = {"name": ev["name"]}
        d["FictionalCharacters"] = characters
    for ev in events:
        if "takePlaceAt" in ev.keys():
            pl = ev["takePlaceAt"]
            places.append(pl)
            ev["takePlaceAt"] = {"name": ev["name"]}
    annotations["Events"] = events
    annotations["Places"] = places
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

            rename_causedBy(annote)
            clean_annotation_names(annote)
            unnest_places_events(annote)

            d2 = os.path.join(dir_target, dirname)
            if not os.path.isdir(d2):
                os.mkdir(d2)
            fp2 = os.path.join(d2, filename)
            with open(fp2, "w") as f:
                json.dump(obj=annote, fp=f, indent=1, ensure_ascii=False)
