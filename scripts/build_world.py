import json
import os
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD


EMOTEL = Namespace("https://github.com/unil-ish/EMOTEL#")
JSON_DIRECTORY = "data/annotations_cleaned"


def get_emotions_lists(fp_onto):
    import owlready2 as owl
    base_onto_full = f"file://{os.path.realpath(fp_onto)}"
    onto = owl.get_ontology(base_onto_full).load()
    registered_emotions = set()

    def rec_add_subclass(c):
        s = str(c)
        name = s[s.index(".") + 1 :]
        registered_emotions.add(name)
        for sub in c.subclasses():
            rec_add_subclass(sub)

    for i in onto.Emotion.subclasses():
        rec_add_subclass(i)
    return registered_emotions



def create_uri(element_id):
    """Crée un URI pour un élément donné.

    Args:
        base_uri (str): L'URI de base.
        element_id (str): L'identifiant de l'élément.

    Returns:
        URIRef: L'URI complet de l'élément.
    """

    base_uri = EMOTEL
    if "texts/" in element_id:
        base_uri = base_uri.replace("#", "") + "/"
    return URIRef(f"{base_uri}{element_id}")


def add_in_story(g, obj, obj_type, story):
    """Une fonction simple et générique pour ajouter une instance dans une histoire.

    L'URI de l'instance est crée à partir de la clé 'id'.  Si l'instance a au nom, ce nom est aussi ajouté.

    Args:
        obj (dict): L'objet décrivant l'instance
        obj_type (str): Le nom de la classe de l'instance
        story (uri): L'URI de la Story.

    Return:
        Union[None, URIRef]: L'URI de l'instance, si elle a été créée
    """

    if "id" in obj:
        uri = create_uri(obj["id"])
        g.add((uri, RDF.type, obj_type))
        if "name" in obj:
            g.add((uri, EMOTEL.hasName, Literal(obj["name"])))
        g.add((uri, EMOTEL.isIn, story))
        return uri
    return


def add_event(g, obj, story):
    """Ajoute un événement dans le graphe, et les propriétés spécifiques.

    Args:
        obj (dict): L'objet décrivant l'événement
        story (uri): L'URI de la Story.

    Return:
        None
    """

    i = add_in_story(
        g=g,
        obj=obj,
        obj_type=EMOTEL.FictionalEvent,
        story=story,
    )

    # ajouter les propriétés événements -> lieu
    x = obj.get("takePlaceAt")
    if isinstance(x, dict):
        x = [x]
    if isinstance(x, list):
        for p in x:
            if "id" in p:
                uri = create_uri(p["id"])
                _ = g.add((i, EMOTEL.takePlaceAt, uri))

    # ajouter les propriétés événements -> personnages
    x = obj.get("hasParticipant")
    if isinstance(x, dict):
        x = [x]
    if isinstance(x, list):
        for p in x:
            if "id" in p:
                uri = create_uri(p["id"])
                _ = g.add((i, EMOTEL.hasParticipant, uri))


def add_emotion(g, obj, story, n, keep_new_emo, registered) -> None:
    """Ajoute les émotions dans le graphe.

    Args:
        obj (dict): Le dict décrivant l'émotion.
        story (str): La story dans laquelle l'émotion est exprimée.
        n (int): Le numéro unique lié à l'émotion, pour son URI.

    Returns:
        None
    """

    if "name" in obj:
        emo_type = obj["name"]
        uri = create_uri(emo_type + str(n))
        if emo_type not in registered:
            emo_type = EMOTEL.Emotion
            unregistered = True
        else:
            emo_type = getattr(EMOTEL, obj["name"])
            unregistered = False
        _ = g.add((uri, RDF.type, emo_type))
        _ = g.add((uri, EMOTEL.isIn, story))

        if unregistered is True:
            g.add((uri, EMOTEL.hasName, Literal(obj["name"])))

        if "feltBy" in obj:
            feltby = obj["feltBy"]
            if isinstance(feltby, list):
                for char in obj["feltBy"]:
                    _ = g.add((uri, EMOTEL.feltBy, create_uri(char)))
            elif isinstance(feltby, str):
                _ = g.add((uri, EMOTEL.feltBy, create_uri(feltby)))

        for prop in ["causedBy", "hasObject"]:
            x = obj.get(prop)
            if x is not None:
                y = x.get("id")
                if y is not None:
                    _ = g.add((uri, getattr(EMOTEL, prop), create_uri(y)))

        if "hasIntensity" in obj:
            _ = g.add(
                (
                    uri,
                    EMOTEL.hasIntensity,
                    Literal(obj["hasIntensity"], datatype=XSD.decimal),
                )
            )


def get_all_jsons(directory) -> list:
    """parse tous les JSONS dans un dossier.

    Args:
        directory (str): Le nom du dossire.

    Returns:
        list (les JSONS parsed)
    """

    annotes = []
    for file in os.listdir(directory):
        fp = os.path.join(directory, file)
        try:
            with open(fp, "r") as f:
                a = json.load(f)
            annotes.append(a)
        except json.decoder.JSONDecodeError:
            pass
    return annotes


def create_and_write_graph(output_file, keep_new_emo: bool, fp_onto) -> None:
    g = Graph()
    g.parse(fp_onto, format="xml")
    g.bind("emotel", EMOTEL)

    n = 0
    for directory_name in os.listdir(JSON_DIRECTORY):
        story = create_uri(directory_name)
        dir_path = os.path.join(JSON_DIRECTORY, directory_name)
        annotes = get_all_jsons(dir_path)

        # construire des listes vides pour chaque classe
        events = []
        characters = []
        emotions = []
        places = []

        # placer tous les individus de ces classes dans ces quatres listes.
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

        registered_emotions = get_emotions_lists(fp_onto)
        # ajouter les lieux
        for obj in places:
            _ = add_in_story(
                g=g,
                obj=obj,
                obj_type=EMOTEL.FictionalPlace,
                story=story,
            )

        # ajouter les personnages
        for obj in characters:
            _ = add_in_story(
                g=g,
                obj=obj,
                obj_type=EMOTEL.FictionalCharacter,
                story=story,
            )

        # ajouter les évenements
        for obj in events:
            add_event(g=g, obj=obj, story=story)

        for obj in emotions:
            n += 1
            add_emotion(
                g=g,
                obj=obj,
                n=n,
                story=story,
                keep_new_emo=keep_new_emo,
                registered=registered_emotions,
            )

    with open(output_file, "w") as f:
        f.write(g.serialize(format="pretty-xml"))


if __name__ == "__main__":
    for keepnew, rdfname, ontoname in [
        (False, "world_strict", "ontology.owl"),
        (True, "world", "ontology_extended.owl"),
    ]:
        fp_rdf = f"outputs/{rdfname}.rdf"
        fp_onto = f"ontology/{ontoname}"
        create_and_write_graph(
            keep_new_emo=keepnew, output_file=fp_rdf, fp_onto=fp_onto
        )
