from rdflib import Graph


d = {}
g = Graph()
g.parse("../ontology/ontology.owl", format="xml")

fp = "../outputs/world.xml"

with open(fp, 'r') as f:
    g.parse(file=f)


query = """
prefix emotel: <https://github.com/unil-ish/EMOTEL#>
select distinct ?place_name ?emotion ?event_name
where {
    ?emotion emotel:causedBy ?event .
    ?event emotel:takePlaceAt ?place .
    ?event emotel:hasName ?event_name .
    ?place emotel:hasName ?place_name .
}
"""

# pour montrer un peu: regarder les 10 premiers résultats.
for n, i in enumerate(g.query(query)):
    print('place:', i.place_name)
    print('event: ', i.event_name)
    print('emotion:', i.emotion[i.emotion.index('#'):])
    print('\n')
    if n > 100:
        break

# construire une liste avec tous les résultats, pour regarder sa longueur.
a = list(g.query(query))
print(len(a))

d = {}

# en cours: l'analyse
places = {}
for row in g.query(query):
    pl = row.place_name
    emo = row.emotion[i.emotion.index('#'):]
    if emo not in d:
        d[emo] = [row.place_name]
    else:
        d[emo].append(row.place_name)
