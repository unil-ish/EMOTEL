from rdflib import Graph
import re


d = {}
g = Graph()

fp = "../outputs/world.rdf"

with open(fp, 'r') as f:
    g.parse(file=f)

query = """
prefix emotel: <https://github.com/unil-ish/EMOTEL#>
select distinct ?place_name ?event_name
where {
    ?emotion emotel:causedBy ?event .
    ?event emotel:takePlaceAt ?place .
    ?event emotel:hasName ?event_name .
    ?place emotel:hasName ?place_name .
}
"""

# pour montrer un peu: regarder les 10 premiers résultats.
for n, i in enumerate(g.query(query)):
    print(f"""place: {i.place_name}
event: {i.event_name}
emotion: {re.search('', str(i.emotion))}
""")
    if n > 100:
        break

# en cours: l'analyse
d = {}
places = {}
for row in g.query(query):
    pl = str(row.place_name)
    emo = str(row.emotion[i.emotion.index('#')+1:])
    if emo not in d:
        d[emo] = [pl]
    else:
        d[emo].append(pl)
    if pl not in places:
        places[pl] = [emo]
    else:
        places[pl].append(emo)

places_words = {}
for pl, emo in places.items():
    words = pl.split('_')
    for w in words:
        if w not in places_words:
            places_words[w] = emo
        else:
            places_words[w].extend(emo)

places_words
