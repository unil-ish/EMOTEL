import json
import os
import unicodedata
import re


def dict_iter_rec(obj, fn_condition, fn_apply) -> None:
    """recherche récursivement les 'dict' satisfaisant une certaine condition et leur applique une fonction qui modifie ces dicts."""

    if isinstance(obj, dict) and fn_condition(obj):
        fn_apply(obj)
    if isinstance(obj, dict):
        for i in obj.values():
            dict_iter_rec(i, fn_condition, fn_apply)
    elif isinstance(obj, (list, set, tuple)):
        for i in obj:
            dict_iter_rec(i, fn_condition, fn_apply)


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


def normalize_obj_name(obj) -> None:
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

    def has_id_or_name_key(d):
        return set(["id", "name"]).intersection(d.keys())

    # utilisation d'une fonction (récursive) qui trouve tous les objets JSON (dict) qui ont au moins l'une des clés ['id', 'name'], et applique sur ces objets la fonction de normalisation.
    dict_iter_rec(
        obj=annotations,
        fn_condition=has_id_or_name_key,
        fn_apply=normalize_obj_name,
    )

    # certaines clés sont remplacés par d'autres (ici appelés 'ersatz'). l'itération suivante assignes, dans les objets concernés, la valeur de l'ersatz (ex. 'cause') à la clé manquante (ex. 'causedBy').
    for key, ersatz in [
        ("feels", "emotions"),
        ("causedBy", "cause"),
        ("hasObject", "object"),
    ]:

        def missing_key_but_ersatz(d):
            return key not in d.keys() and ersatz in d.keys()

        def replace_ersatz_with_key(d):
            d[key] = d[ersatz]
            d.pop(ersatz)

        dict_iter_rec(
            obj=annotations,
            fn_condition=missing_key_but_ersatz,
            fn_apply=replace_ersatz_with_key,
        )

    # enfin, dernière modification: certaines propriétés qui devraient être des objets JSON (des dicts) n'en sont pas (par exemple, sont des str). s'il s'agit d'une string, on la remplace par un dict qui associe sa valeur à la clé 'name', s'il s'agit d'une liste et qu'il n'y a qu'un élément, alors on la remplace par ce premier élément.
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
                else:
                    d.pop(p)

    dict_iter_rec(
        obj=annotations,
        fn_condition=has_any_prop,
        fn_apply=remove_nodict_prop,
    )

    return


def add_missing_names(annote):
    ids = {}
    # d'abord, récupérer les ids de ce qui se trouve dans le fichiers d'annotations, à savoir: les ids des Places et FictionalCharacters, afin de pouvoir mettre les 'name' correspondant dans les sous-sous-clés de Events.
    for key in ("FictionalCharacters", "Places"):
        if key in annote:
            obj = annote[key]
            for i in obj:
                if "name" in i.keys():
                    name = i["name"]
                    if "id" in i.keys():
                        _id = i["id"]
                        ids[_id] = name
                    else:
                        ids[name] = name
                else:
                    pass

    # deuxième étape: mettre ces noms là où ils manquent
    def missing_name(d):
        return "name" not in d.keys() and "id" in d.keys()

    def add_name(d):
        d["name"] = ids[d["id"]]

    dict_iter_rec(
        obj=annote,
        fn_condition=missing_name,
        fn_apply=add_name,
    )
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
            add_missing_names(annote)

            d2 = os.path.join(dir_target, dirname)
            if not os.path.isdir(d2):
                os.mkdir(d2)
            fp2 = os.path.join(d2, filename)
            with open(fp2, "w") as f:
                json.dump(obj=annote, fp=f, indent=1, ensure_ascii=False)
