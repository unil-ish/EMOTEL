""" MARCHE PAS ENCORE """
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import OWL, RDFS, XSD
import json
import os

dirname = "data/annotations/littlewomen"
ext = ('.json')

# Namespace
EMOTEL = Namespace("https://github.com/unil-ish/EMOTEL#")



# Initialize the graph
g = Graph()
# Chargement de l'ontologie depuis le fichier RDF
g.parse("ontology/ontology.owl", format="xml")
g.bind("emotel", EMOTEL)

# Function to create URIs
def create_uri(base_uri, element_id):
    return URIRef(f"{base_uri}{element_id}")

# Function to add FictionalCharacter
def add_fictional_character(character):
    char_uri = create_uri(EMOTEL, character['id'])
    g.add((char_uri, RDF.type, EMOTEL.FictionalCharacter))
    if 'name' in character:
        g.add((char_uri, EMOTEL.hasName, Literal(character['name'], datatype=XSD.string)))
    
    for emotion in character['feels']:
        emotion_uri = create_uri(EMOTEL, f"{character['id']}_{emotion['name']}")
        g.add((emotion_uri, RDF.type, EMOTEL.Emotion))
        g.add((emotion_uri, EMOTEL.hasIntensity, Literal(emotion['hasIntensity'], datatype=XSD.decimal)))
        g.add((emotion_uri, EMOTEL.text, Literal(emotion['quote'], datatype=XSD.string)))
        
        if 'causedBy' in emotion:
            event_uri = create_uri(EMOTEL, emotion['causedBy']['id'])
            g.add((emotion_uri, EMOTEL.causedBy, event_uri))
        
        if 'hasObject' in emotion:
            object_uri = create_uri(EMOTEL, emotion['hasObject']['id'])
            g.add((emotion_uri, EMOTEL.hasObject, object_uri))
        
        if 'place' in emotion:
            print(emotion['place'])
            for place in data['Places']:
                if place['name'] == emotion['place']:
                    place_id = place['id']
                    place_uri = create_uri(EMOTEL, place_id)
                    g.add((emotion_uri, EMOTEL.takePlaceAt, place_uri))
        
        g.add((char_uri, EMOTEL.feels, emotion_uri))

# Function to add Object
def add_object(obj):
    obj_uri = create_uri(EMOTEL, obj['id'])
    g.add((obj_uri, RDF.type, EMOTEL.FictionalObject))
    if 'name' in obj:
        g.add((obj_uri, EMOTEL.hasName, Literal(obj['name'], datatype=XSD.string)))
    
    for emotion in obj.get('associatedEmotions', []):
        emotion_uri = create_uri(EMOTEL, emotion)
        g.add((obj_uri, EMOTEL.isObjectOf, emotion_uri))

# Function to add Place
def add_place(place):
    place_uri = create_uri(EMOTEL, place['id'])
    g.add((place_uri, RDF.type, EMOTEL.FictionalPlace))
    if 'name' in place:
        g.add((place_uri, EMOTEL.hasName, Literal(place['name'], datatype=XSD.string)))
    if 'description' in place:
        g.add((place_uri, EMOTEL.hasDesc, Literal(place['description'], datatype=XSD.string)))

# Function to add Event
def add_event(event):
    event_uri = create_uri(EMOTEL, event['id'])
    g.add((event_uri, RDF.type, EMOTEL.FictionalEvent))
    if 'name' in event:
        g.add((event_uri, EMOTEL.hasName, Literal(event['name'], datatype=XSD.string)))
    if 'takePlaceAt' in event:
        place_uri = create_uri(EMOTEL, event['takePlaceAt']['id'])
        g.add((event_uri, EMOTEL.takePlaceAt, place_uri))
    if 'hasParticipant' in event:
        participant_uri = create_uri(EMOTEL, event['hasParticipant']['id'])
        g.add((event_uri, EMOTEL.hasParticipant, participant_uri))

# iterating over all files
for files in os.listdir(dirname):
    print(files)
    if files.endswith(ext):

        # Chargement du fichier JSON
        with open(f"data/annotations/littlewomen/{files}", "r") as f:
            data = json.load(f)
        # Add data to the graph
        try:
            for character in data['FictionalCharacters']:
                add_fictional_character(character)
        except KeyError as er:
            pass

        try:
            for place in data['Places']:
                add_place(place)
        except KeyError as er:
            pass

        try:
            for event in data['Events']:
                print(event)
                add_event(event)
        except KeyError as er:
            pass

# Serialize the graph to RDF/XML format and save to file
output_file = "ontology_output_mult.rdf"
with open(output_file, "w") as f:
    f.write(g.serialize(format="pretty-xml"))

print(f"Ontology saved to {output_file}")