import os
import openai
import json
import sys
import tqdm
import time


def send_req(messages) -> str:
    """Envoie une requête avec une liste de messages à chatpgt, et récupère le contenu de la réponse."""

    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,  # on ne souhaite pas forcément une expérimentation trop grande, au contraire on souhaite un resect strict, à la fois de nos catégories pour les émotions, et de la structure du JSON.
        max_tokens=None,  # ne pas mettre de maximum sinon on se retrouve avec des demi-json.
        top_p=1,  # ?
        frequency_penalty=0,  # la répétition de tokens n'est pas un souci.
        presence_penalty=0,
    )
    result = "\n".join([i.message.content for i in response.choices])
    # parfois, chatgpt retourne le JSON dans un format markdown (blockCode):
    # ```json
    # [...]
    # ```
    # les enlever si elles sont là.
    if result.startswith("```json"):
        result = result[6:-3]
    return result


def annotate_directory(chunks_dir) -> None:
    """Annote les séquences de messages qui se trouvent dans un dossier.

    Le processus est répété si certains textes n'ont pas été correctement analysés et que la réponse est vide (10 répétitions maximum).

    Si le JSON est mal formé, (ce qui arrive), il est placé tel quel mais au nom de fichier est ajouté le suffixe '_a_corriger'. normalement, il ne devrait pas y en avoir trop.
    """

    # le dossier contenant les séquences de messages
    chunks_dir = os.path.realpath(chunks_dir)
    # le dossier où placer les annotations
    annotations_dir = chunks_dir.replace("/chunks/", "/annotations/")
    # (créer le dossier d'annotations s'il n'existe pas)
    if not os.path.isdir(annotations_dir):
        os.mkdir(annotations_dir)

    def get_not_yet_annotated() -> list[str]:
        """Dresse la liste des fichiers qu'il reste à annoter.

        Simplement obtenue par la liste de fichiers de l'oeuvre, à laquelle est soustraire la liste des fichiers annotés.
        """

        chunk_files = set(os.listdir(chunks_dir))
        annotations_files = set(os.listdir(annotations_dir))
        files = chunk_files - annotations_files
        return files

    # la liste de départ: tous les fichiers
    files = get_not_yet_annotated()

    # le nombre total de fichier: pour afficher la progression (et dire à la fonction quand s'arrêter).
    total_n = len(files)
    n = 0  # le nombre de fichiers déjà annotés: 0.
    x = 1  # le nombre de répétitions du traitement.

    while n < total_n and x < 10:
        print(f"""reste à annoter {total_n - n} conversations. 
essai numéro {x}/10""")
        for fp in tqdm.tqdm(files):  # tqdm: afficher la progression

            # parse la conversation (prompt initial et série de textes)
            with open(os.path.join(chunks_dir, fp), "r") as f:
                messages = json.load(f)

            # envoie à chatpgt et récupère le contenu de la réponse
            response = send_req(messages)

            # la construction try/except sert surtout à identifier les JSON mal formés et qu'il faut corriger (à la main ou autrement).
            try:
                # parse le résultat, s'il est non-null, alors écrire le fichier.
                r = json.loads(response)
                if r is not None:
                    with open(os.path.join(annotations_dir, fp), "w") as f:
                        json.dump(obj=r, fp=f, indent=1, ensure_ascii=False)
                    n += 1
            except json.decoder.JSONDecodeError:
                # si le JSON est mal formé, l'écrire sans passer par le module JSON et ajouter un suffixe au fichier pour noter qu'il y a un problème.
                print("erreur de décodage: à corriger manuelement")
                with open(os.path.join(annotations_dir, fp + "_a_corriger"), "w") as f:
                    f.write(response)
                n += 1
        x += 1
        # après une série de demande, attendre un peu pour éviter d'atteindre les limites.
        time.sleep(30)
        # et réactualiser la liste des fichiers à annoter.
        files = get_not_yet_annotated()
    return


if __name__ == "__main__":
    chunk_dir = sys.argv[1]
    if os.path.isdir(chunk_dir):
        annotate_directory(chunk_dir)
        quit(0)
    else:
        raise ValueError("not a directory:", chunk_dir)
