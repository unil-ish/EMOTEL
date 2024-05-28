from rdflib import Graph
from collections import Counter
import re
import pprint


d = {}
g = Graph()

fp = "../outputs/world_strict.rdf"

with open(fp, "r") as f:
    g.parse(file=f)

query = """
prefix emotel: <https://github.com/unil-ish/EMOTEL#>
select distinct ?place_name ?event_name ?emotion
where {
    ?emotion emotel:causedBy ?event .
    ?event emotel:takePlaceAt ?place .
    ?event emotel:hasName ?event_name .
    ?place emotel:hasName ?place_name .
}
"""


def get_emo_name(emotion):
    emotion = str(emotion)
    emotion = re.search(r'\w+?\d+$', emotion).group(0)
    emotion = "".join([c for c in emotion if c.isalpha()])
    return emotion


# pour montrer un peu: regarder les 40 premiers résultats
for n, i in enumerate(g.query(query)):
    print(f"""place: {i.place_name}
event: {i.event_name}
emotion: {get_emo_name(i.emotion)}
""")
    if n > 40:
        break

d = {}
places = {}
for row in g.query(query):
    pl = str(row.place_name).lower()
    emo = get_emo_name(row.emotion)
    if emo not in d:
        d[emo] = [pl]
    else:
        d[emo].append(pl)
    if pl not in places:
        places[pl] = [emo]
    else:
        places[pl].append(emo)

all_words = []
for i in places.keys():
    all_words.extend(i.split('_'))

x = {}
for i in all_words:
    if i not in x:
        x[i] = []
    for pl, emos in places.items():
        if i in pl.split('_'):
            x[i].extend(emos)

for i in x:
    x[i] = Counter(x[i])

# les émotions liées aux événements qui se trouvent dans un endroit dont le nom contient le mot 'house'.
pprint.pprint(x['house'])

# et 'home'
pprint.pprint(x['home'])
