import json
import os
import unicodedata
import re


def clean_name(s):
    """character's name -> character_s_name"""

    s = re.sub("[_' ]+", "_", s)
    return "".join([c for c in s if c.isalpha() or c == "_"])


def clean_obj(obj) -> None:
    """normalise le nom d'un objet."""

    if "name" in obj:
        name = obj["name"]
    elif "id" in obj:
        # si 'name' est manquant, c'est en fait toujours l'id qui contient le nom. il suffit donc de le réassigner.
        name = obj["id"]
    else:
        name = "undefined"
    # la fonction qui enlève notamment les espaces.
    name = clean_name(name)
    # normalisation supplémentaires, pour essayer d'éliminer au maximum les erreurs.
    obj["name"] = unicodedata.normalize("NFC", name)
    return


def clean_annotation_names(annotations):
    """clean les clés 'name' de tous les objets concernés."""

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
    return annotations


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
