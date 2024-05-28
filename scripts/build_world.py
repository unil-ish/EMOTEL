import json
import os
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD


EMOTEL = Namespace("https://github.com/unil-ish/EMOTEL#")
ROOT_DIRECTORY = "../data/annotations_cleaned"

d = {}
g = Graph()
g.parse("../ontology/ontology.owl", format="xml")
g.bind("emotel", EMOTEL)


def add_in_story(obj, obj_type, story):
    """Une fonction simple et générique pour ajouter une instance dans une histoire.

    L'URI de l'instance est crée à partir de la clé 'id'.  Si l'instance a au nom, ce nom est aussi ajouté.

    Args:
        obj (dict): L'objet décrivant l'instance
        obj_type (str): Le nom de la classe de l'instance
        story (uri): L'URI de la Story.

    Return:
        Union[None, URIRef]: L'URI de l'instance, si elle a été créée
    """

    if "id" in obj:
        uri = URIRef(obj["id"])
        g.add((uri, RDF.type, obj_type))
        if "name" in obj:
            g.add((uri, EMOTEL.hasName, Literal(obj["name"])))
        g.add((uri, EMOTEL.isIn, story))
        return uri
    return


def add_event(obj):
    """Ajoute un événement dans le graphe, et les propriétés spécifiques.

    Args:
        obj (dict): L'objet décrivant l'événement

    Return:
        None
    """

    i = add_in_story(
        obj=obj,
        obj_type=EMOTEL.FictionalEvent,
    )

    # ajouter les propriétés événements -> lieu
    x = obj.get("takePlaceAt")
    if isinstance(x, dict):
        x = [x]
    if isinstance(x, list):
        for p in x:
            if "id" in p:
                uri = URIRef(p["id"])
                _ = g.add((i, EMOTEL.takePlaceAt, uri))

    # ajouter les propriétés événements -> personnages
    x = obj.get("hasParticipant")
    if isinstance(x, dict):
        x = [x]
    if isinstance(x, list):
        for p in x:
            if "id" in p:
                uri = URIRef(p["id"])
                _ = g.add((i, EMOTEL.hasParticipant, uri))


def add_emotion(obj, n) -> None:
    """Ajoute les émotions dans le graphe.

    Args:
        obj (dict): Le dict décrivant l'émotion.
        n (int): Le numéro unique lié à l'émotion, pour son URI.

    Returns:
        None
    """

    if "name" in obj:
        uri = URIRef(obj["name"])
        emotion_type = getattr(EMOTEL, obj["name"])
        _ = g.add((uri, RDF.type, emotion_type))
        _ = g.add((uri, EMOTEL.isIn, story))

        if "feltBy" in obj:
            _ = g.add((uri, EMOTEL.feltBy, d[obj["feltBy"]]))

        for prop in ["causedBy", "hasObject"]:
            x = obj.get(prop)
            if x is not None:
                y = x.get("id")
                if y is not None:
                    g.add((uri, getattr(EMOTEL, prop), URIRef(y)))

        if "hasIntensity" in obj:
            g.add(
                (
                    uri,
                    EMOTEL.hasIntensity,
                    Literal(obj["hasIntensity"], datatype=XSD.decimal),
                )
            )


def get_all_jsons(directory) -> list:
    """parse tous les JSNS dans un dossier.

    Args:
        directory (str): Le nom du dossire.

    Returns:
        list (les JSONS parsed)
    """

    a = []
    for file in os.listdir(directory):
        fp = os.path.join(directory, file)
        try:
            with open(fp, "r") as f:
                a = json.load(f)
            annotes.append(a)
        except json.decoder.JSONDecodeError:
            pass
    return a


# def add_story(g, directory, n=0):
root_directory = "../data/annotations_cleaned"
n = 0
for directory_name in os.listdir(root_directory):
    story = URIRef(directory_name)
    dir_path = os.path.join(ROOT_DIRECTORY, directory_name)
    annotes = get_all_jsons(dir_path)

    # construire des listes vides pour chaque classe
    events = []
    characters = []
    emotions = []
    places = []

    # placer tous les individus de ces classes dans ces quatres listes.
    for a in annotes:
        if not isinstance(a, dict):
            continue
        for v, k in [
            (events, "Events"),
            (characters, "FictionalCharacters"),
            (places, "Places"),
        ]:
            x = a.get(k)
            if isinstance(x, list):
                v.extend(x)
        x = a.get("FictionalCharacters")
        if isinstance(x, list):
            for char in x:
                y = char.get("feels")
                if y is not None:
                    charid = char.get("id")
                    for em in y:
                        em["feltBy"] = charid
                        emotions.append(em)

    # ajouter les lieux
    for obj in places:
        i = add_in_story(
            obj=obj,
            obj_type=EMOTEL.FictionalPlace,
            story=story,
        )

    # ajouter les personnages
    for obj in characters:
        i = add_in_story(
            obj=obj,
            obj_type=EMOTEL.FictionalCharacter,
        )

    # ajouter les évenements
    for obj in events:
        add_event(obj)

    # ajouter, enfin, les émotions
    for obj in emotions:
        n += 1
        add_emotion(obj=obj, n=n)

output_file = "../outputs/world.xml"
with open(output_file, "w") as f:
    f.write(g.serialize(format="pretty-xml"))
