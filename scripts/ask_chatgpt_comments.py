import os
import openai
import json
import sys
import tqdm
import time


def send_req(messages) -> str:
    """Envoie une requête avec une liste de messages à l'API OpenAI et récupère le contenu de la réponse.

    Args:
        messages (list): Liste de messages à envoyer à l'API.

    Returns:
        str: Contenu de la réponse de l'API, sous forme de chaîne de caractères.
    """
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,  # On souhaite un respect strict des catégories d'émotions et de la structure du JSON.
        max_tokens=None,  # Pas de maximum pour éviter des JSON incomplets.
        top_p=1,
        frequency_penalty=0,  # La répétition de tokens n'est pas un souci.
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    result = "\n".join([i.message.content for i in response.choices])
    # Parfois, l'API retourne le JSON dans un format Markdown (blockCode):
    # ```json
    # [...]
    # ```
    # Les enlever si elles sont présentes.
    if result.startswith("```json"):
        result = result[6:-3]
    return result


def annotate_directory(chunks_dir: str) -> None:
    """Annote les séquences de messages qui se trouvent dans un dossier.

    Le processus est répété si certains textes n'ont pas été correctement analysés
    et que la réponse est vide (10 répétitions maximum). Si le JSON est mal formé,
    il est placé tel quel mais au nom de fichier est ajouté le suffixe '_a_corriger'.

    Args:
        chunks_dir (str): Chemin vers le répertoire contenant les séquences de messages.

    """
    chunks_dir = os.path.realpath(chunks_dir)
    annotations_dir = chunks_dir.replace("/chunks/", "/annotations/")
    
    if not os.path.isdir(annotations_dir):
        os.mkdir(annotations_dir)

    def get_not_yet_annotated() -> list[str]:
        """Dresse la liste des fichiers qu'il reste à annoter.

        Simplement obtenue par la liste de fichiers du répertoire de chunks, à laquelle est soustraite
        la liste des fichiers annotés.

        Returns:
            list[str]: Liste des fichiers non encore annotés.
        """
        chunk_files = set(os.listdir(chunks_dir))
        annotations_files = set(os.listdir(annotations_dir))
        files = chunk_files - annotations_files
        return list(files)

    files = get_not_yet_annotated()
    total_n = len(files)
    n = 0
    x = 1

    while n < total_n and x < 10:
        print(f"Il reste à annoter {total_n - n} fichiers. Essai {x}/10")
        for fp in tqdm.tqdm(files):
            with open(os.path.join(chunks_dir, fp), "r") as f:
                messages = json.load(f)

            response = send_req(messages)

            try:
                r = json.loads(response)
                if r is not None:
                    with open(os.path.join(annotations_dir, fp), "w") as f:
                        json.dump(obj=r, fp=f, indent=1, ensure_ascii=False)
                    n += 1
            except json.decoder.JSONDecodeError:
                print("Erreur de décodage: à corriger manuellement")
                with open(os.path.join(annotations_dir, fp + "_a_corriger"), "w") as f:
                    f.write(response)
                n += 1
        x += 1
        time.sleep(30)
        files = get_not_yet_annotated()
    return


if __name__ == "__main__":
    chunk_dir = sys.argv[1]
    if os.path.isdir(chunk_dir):
        annotate_directory(chunk_dir)
        quit(0)
    else:
        raise ValueError("Not a directory:", chunk_dir)
