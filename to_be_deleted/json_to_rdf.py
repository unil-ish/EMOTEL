import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD

# Load JSON data
with open('example.json') as f:
    data = json.load(f)

# Create an RDF graph
g = Graph()

# Define namespaces
BASE = Namespace("https://github.com/unil-ish/EMOTEL#")
g.bind("base", BASE)
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

# Add data to the graph
for character in data["FictionalCharacters"]:
    char_uri = BASE[character["id"]]
    g.add((char_uri, RDF.type, BASE[character["type"]]))
    g.add((char_uri, RDFS.label, Literal(character["name"], datatype=XSD.string)))

    for emotion in character["feels"]:
        emotion_uri = BASE[emotion["id"]]
        g.add((emotion_uri, RDF.type, BASE[emotion["type"]]))
        g.add((emotion_uri, RDFS.label, Literal(emotion["name"], datatype=XSD.string)))
        g.add((emotion_uri, BASE["hasIntensity"], Literal(emotion["hasIntensity"], datatype=XSD.decimal)))
        g.add((char_uri, BASE["feels"], emotion_uri))

        if "causedBy" in emotion:
            event = emotion["causedBy"]
            event_uri = BASE[event["id"]]
            g.add((event_uri, RDF.type, BASE[event["type"]]))
            g.add((event_uri, RDFS.label, Literal(event["name"], datatype=XSD.string)))
            g.add((emotion_uri, BASE["causedBy"], event_uri))

        if "hasObject" in emotion:
            obj = emotion["hasObject"]
            obj_uri = BASE[obj["id"]]
            g.add((obj_uri, RDF.type, BASE[obj["type"]]))
            g.add((obj_uri, RDFS.label, Literal(obj["name"], datatype=XSD.string)))
            g.add((emotion_uri, BASE["hasObject"], obj_uri))

# Serialize the graph to an RDF/XML file
g.serialize(destination='example_output.rdf', format='xml')

