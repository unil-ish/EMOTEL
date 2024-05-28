import json
import os
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD


EMOTEL = Namespace("https://github.com/unil-ish/EMOTEL#")
ROOT_DIRECTORY = "../data/annotations_cleaned"


def add_story(g, directory, n=0):
    story = URIRef(directory)
    dir_path = os.path.join(ROOT_DIRECTORY, directory)
    annotes = []

    # parse les JSONS
    for file in os.listdir(dir_path):
        fp = os.path.join(dir_path, file)
        try:
            with open(fp, "r") as f:
                a = json.load(f)
            annotes.append(a)
        except json.decoder.JSONDecodeError:
            pass

    # construire des listes vides pour chaque classe
    events = []
    characters = []
    emotions = []
    places = []

    # placer tous les individus de ces classes dans les listes.
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

    def add_in_story(obj, obj_type):
        if "id" in obj:
            uri = URIRef(obj["id"])
            g.add((uri, RDF.type, obj_type))
            if "name" in obj:
                g.add((uri, EMOTEL.hasName, Literal(obj["name"])))
            g.add((uri, EMOTEL.isIn, story))
            return uri
        return

    # ajouter les lieux
    for obj in places:
        i = add_in_story(
            obj=obj,
            obj_type=EMOTEL.FictionalPlace,
        )

    # ajouter les personnages
    for obj in characters:
        i = add_in_story(
            obj=obj,
            obj_type=EMOTEL.FictionalCharacter,
        )
        d[obj["id"]] = i

    # ajouter les évenements
    for obj in events:
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

    # ajouter, enfin, les émotions
    for obj in emotions:
        n += 1
        if "name" in obj:
            uri = URIRef(obj["name"])
            emotion_type = getattr(EMOTEL, obj["name"])
            _ = g.add((uri, RDF.type, emotion_type))
            _ = g.add((uri, EMOTEL.isIn, story))

            if "feltBy" in obj:
                _ = g.add((uri, EMOTEL.feltBy, d[obj["feltBy"]]))

            for prop in ['causedBy', 'hasObject']:
                x = obj.get(prop)
                if x is not None:
                    y = x.get('id')
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
    return n


d = {}
g = Graph()
g.parse("../ontology/ontology.owl", format="xml")
g.bind("emotel", EMOTEL)


root_directory = "../data/annotations_cleaned"
n = 0
for directory_name in os.listdir(root_directory):
    n = add_story(g, directory_name, n)


output_file = "../outputs/world.xml"
with open(output_file, "w") as f:
    f.write(g.serialize(format="pretty-xml"))
