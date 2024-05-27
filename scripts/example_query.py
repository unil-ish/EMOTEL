from rdflib import Graph, Namespace
from rdflib.namespace import RDF, RDFS

# Load the RDF data
rdf_file = "example_output.rdf"
g = Graph()
g.parse(rdf_file, format="xml")

# Define the namespace
BASE = Namespace("https://github.com/unil-ish/EMOTEL#")

# Define the SPARQL query to find all instances of the label "Joy" and retrieve intensity and character name
query = """
PREFIX base: <https://github.com/unil-ish/EMOTEL#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?label ?intensity ?character_label
WHERE {
  ?subject rdfs:label ?label .
  FILTER (?label = "Joy")
  ?subject base:hasIntensity ?intensity .
  ?character base:feels ?subject .
  ?character rdfs:label ?character_label .
}
"""

# Execute the query
results = g.query(query)

# Print the results
for row in results:
    print(
        f"Subject: {row.subject}, Label: {row.label}, Intensity: {row.intensity}, Character Name: {row.character_label}"
    )
