import json
import os
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import OWL, RDFS, XSD

# Root
dirname = "data/annotations_cleaned"
ext = ".json"

# Namespace
EMOTEL = Namespace("https://github.com/unil-ish/EMOTEL#")

# Initialize the graph
g = Graph()
# Loading and parsing ontology
g.parse("ontology/ontology.owl", format="xml")
g.bind("emotel", EMOTEL)


def create_uri(base_uri: str, element_id: str) -> URIRef:
    """Crée un URI pour un élément donné.

    Args:
        base_uri (str): L'URI de base.
        element_id (str): L'identifiant de l'élément.

    Returns:
        URIRef: L'URI complet de l'élément.
    """
    return URIRef(f"{base_uri}{element_id}")


def add_fictional_character(character: dict) -> None:
    """Ajoute un personnage fictif au graphe RDF.

    Args:
        character (dict): Les données du personnage.
    """
    char_uri = create_uri(EMOTEL, character["id"])
    g.add((char_uri, RDF.type, EMOTEL.FictionalCharacter))
    if "name" in character:
        g.add(
            (char_uri, EMOTEL.hasName, Literal(character["name"], datatype=XSD.string))
        )

    for emotion in character["feels"]:
        emotion_uri = create_uri(EMOTEL, f"{character['id']}_{emotion['name']}")
        g.add((emotion_uri, RDF.type, EMOTEL.Emotion))
        g.add(
            (
                emotion_uri,
                EMOTEL.hasIntensity,
                Literal(emotion["hasIntensity"], datatype=XSD.decimal),
            )
        )
        g.add(
            (emotion_uri, EMOTEL.text, Literal(emotion["quote"], datatype=XSD.string))
        )

        if "causedBy" in emotion:
            event_uri = create_uri(EMOTEL, emotion["causedBy"]["id"])
            g.add((emotion_uri, EMOTEL.causedBy, event_uri))

        if "hasObject" in emotion:
            object_uri = create_uri(EMOTEL, emotion["hasObject"]["id"])
            g.add((emotion_uri, EMOTEL.hasObject, object_uri))

        if "place" in emotion:
            for place in data["Places"]:
                if place["name"] == emotion["place"]:
                    place_id = place["id"]
                    place_uri = create_uri(EMOTEL, place_id)
                    g.add((emotion_uri, EMOTEL.takePlaceAt, place_uri))

        g.add((char_uri, EMOTEL.feels, emotion_uri))


def add_object(obj: dict) -> None:
    """Ajoute un objet fictif au graphe RDF.

    Args:
        obj (dict): Les données de l'objet.
    """
    obj_uri = create_uri(EMOTEL, obj["id"])
    g.add((obj_uri, RDF.type, EMOTEL.FictionalObject))
    if "name" in obj:
        g.add((obj_uri, EMOTEL.hasName, Literal(obj["name"], datatype=XSD.string)))

    for emotion in obj.get("associatedEmotions", []):
        emotion_uri = create_uri(EMOTEL, emotion)
        g.add((obj_uri, EMOTEL.isObjectOf, emotion_uri))


def add_place(place: dict) -> None:
    """Ajoute un lieu fictif au graphe RDF.

    Args:
        place (dict): Les données du lieu.
    """
    place_uri = create_uri(EMOTEL, place["id"])
    g.add((place_uri, RDF.type, EMOTEL.FictionalPlace))
    if "name" in place:
        g.add((place_uri, EMOTEL.hasName, Literal(place["name"], datatype=XSD.string)))
    if "description" in place:
        g.add(
            (
                place_uri,
                EMOTEL.hasDesc,
                Literal(place["description"], datatype=XSD.string),
            )
        )


def add_event(event: dict) -> None:
    """Ajoute un événement fictif au graphe RDF.

    Args:
        event (dict): Les données de l'événement.
    """
    event_uri = create_uri(EMOTEL, event["id"])
    g.add((event_uri, RDF.type, EMOTEL.FictionalEvent))
    if "name" in event:
        g.add((event_uri, EMOTEL.hasName, Literal(event["name"], datatype=XSD.string)))
    if "takePlaceAt" in event:
        place_uri = create_uri(EMOTEL, event["takePlaceAt"]["id"])
        g.add((event_uri, EMOTEL.takePlaceAt, place_uri))
    if "hasParticipant" in event:
        if isinstance(event["hasParticipant"], list):
            for participant in event["hasParticipant"]:
                participant_uri = create_uri(EMOTEL, participant["id"])
                g.add((event_uri, EMOTEL.hasParticipant, participant_uri))
        else:
            participant_uri = create_uri(EMOTEL, event["hasParticipant"]["id"])
            g.add((event_uri, EMOTEL.hasParticipant, participant_uri))


# Iterate over all files
for folder in os.listdir(dirname):
    for files in os.listdir(f"{dirname}/{folder}"):
        if files.endswith(ext):
            # Load JSON file
            with open(f"{dirname}/{folder}/{files}", "r") as f:
                data = json.load(f)

            # Add data to the graph
            try:
                for character in data["FictionalCharacters"]:
                    add_fictional_character(character)
            except KeyError:
                pass

            try:
                for place in data["Places"]:
                    add_place(place)
            except KeyError:
                pass

            try:
                for event in data["Events"]:
                    add_event(event)
            except KeyError:
                pass

# Serialize the graph to RDF/XML format and save to file
output_file = "outputs/populated_ontology.rdf"
with open(output_file, "w") as f:
    f.write(g.serialize(format="pretty-xml"))

print(f"Ontology saved to {output_file}")
