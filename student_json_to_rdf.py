import json
from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD

# Chargement du fichier JSON
with open("student_data.json", "r") as f:
    data = json.load(f)

# Création du graphe RDF
g = Graph()

# Chargement de l'ontologie depuis le fichier RDF
g.parse("student_ontology.rdf", format="xml")

# Définition de namespaces
ex_ns = "http://example.org/"
ex = URIRef(ex_ns)


# Fonction pour ajouter un individu au graphe
def add_individual(individual):
    ind_uri = URIRef(ex_ns + individual["id"])
    class_uri = URIRef(ex_ns + individual["type"])
    g.add((ind_uri, RDF.type, class_uri))
    for prop, value in individual["properties"].items():
        prop_uri = URIRef(ex_ns + prop)
        if isinstance(value, str):
            g.add((ind_uri, prop_uri, Literal(value, datatype=XSD.string)))
        elif isinstance(value, int):
            g.add((ind_uri, prop_uri, Literal(value, datatype=XSD.integer)))
        else:
            g.add((ind_uri, prop_uri, URIRef(ex_ns + value)))


# Ajout des individus depuis le fichier JSON
for individual in data["individuals"]:
    add_individual(individual)

# Sérialisation du graphe en format RDF/XML
print(g.serialize(format="xml"))

# Interrogation du graphe avec SPARQL
qres = g.query(
    """
    PREFIX ex: <http://example.org/>
    SELECT ?name ?age ?course
    WHERE {
        {?student rdf:type ex:Student} 
        UNION {?student rdf:type ex:Person} .
        ?student ex:hasName ?name .
        ?student ex:hasAge ?age .
        OPTIONAL { ?student ex:isEnrolledIn ?course }
    }
    """
)

# Affichage des résultats
for row in qres:
    print(f"Name: {row.name}, Age: {row.age}, Course: {row.course}")
