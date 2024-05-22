"""crée une ontologie OWL à l'aide de la librairie owlready2."""

import owlready2 as owl
import types

# les classes de base:
# - oeuvre
# - passage
# - entité fictionnelle
# - émotion
base_classes = ["Expression", "Emotion", "Story", "FictionalObject"]

# les sous-classes de 'entité fictionnelle':
# - personnage
# - situation
fictional_objects = ["FictionalCharacter", "FictionalEvent", "FictionalPlace"]

# les sous-classes de 'émotion' (émotions simples, composées, dérivées)
base_emotions = [
    "Trust",
    "Surprise",
    "Anger",
    "Joy",
    "Anticipation",
    "Fear",
    "Disgust",
    "Sadness",
]
derived_emotions = {
    "Acceptance": ["Trust"],
    "Admiration": ["Trust"],
    "Amazement": ["Surprise"],
    "Distraction": ["Surprise"],
    "Terror": ["Fear"],
    "Apprehension": ["Fear"],
    "Boredom": ["Disgust"],
    "Loathing": ["Disgust"],
    "Interest": ["Anticipation"],
    "Vigilance": ["Anticipation"],
    "Annoyance": ["Anger"],
    "Rage": ["Anger"],
    "Serenity": ["Joy"],
    "Ecstasy": ["Joy"],
    "Grief": ["Sadness"],
    "Pensiveness": ["Sadness"],
    "Contempt": ["Disgust", "Anger"],
    "Aggressiveness": ["Anger", "Anticipation"],
    "Optimism": ["Anticipation", "Joy"],
    "Love": ["Joy", "Trust"],
    "Submission": ["Trust", "Fear"],
    "Awe": ["Fear", "Surprise"],
    "Disapproval": ["Surprise", "Sadness"],
    "Remorse": ["Sadness", "Disgust"],
}

object_properties = {
    "isFeltBy": {"domain": "Emotion", "range": "Character"},
    "causedBy": {"domain": "Emotion", "range": "Situation"},
    "hasObject": {"domain": "Emotion", "range": "FictionalObject"},
    "isIn": {"domain": "FictionalObject", "range": "Story"},
    "takePlaceAt": {"domain": "FictionalEvent", "range": "FictionalPlace"},
    "hasParticipant": {"domain": "FictionalEvent", "range": "FictionalCharacter"},
}

data_properties = {
    "hasIntensity": {"domain": "Emotion", "range": float},
    "hasPubYear": {"domain": "Expression", "range": int},
}

# crée une ontologie avec, comme URI, l'URL du projet.
onto = owl.get_ontology("https://github.com/unil-ish/EMOTEL")
with onto:
    # 1) crée les classes de base
    for i in base_classes:
        types.new_class(i, (owl.Thing,))

    # 2) crée les sous-classe de 'entité fictionnelle'
    for i in fictional_objects:
        types.new_class(i, (onto.FictionalObject,))

    # 3) crée les classes d'émotions
    # 3.1) d'abord les émotions simples.
    for i in base_emotions:
        types.new_class(i, (onto.Emotion,))
    # 3.2) puis les émotions complexes
    for i in derived_emotions:
        superclasses = [getattr(onto, s) for s in derived_emotions[i]]
        types.new_class(i, tuple(superclasses))

    # 4) propriétés
    # 4.1) objects properties
    for i in object_properties:
        p = types.new_class(i, (owl.ObjectProperty,))
        for x in "domain", "range":
            setattr(p, x, getattr(onto, object_properties[i][x]))
    # 4.2) data properties
    for i in data_properties:
        p = types.new_class(i, (owl.DataProperty,))
        setattr(p, "domain", getattr(onto, data_properties[i]["domain"]))
        setattr(p, "range", data_properties[i]["range"])

onto.save(file="ontology.owl", format="rdfxml")
