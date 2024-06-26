import os
import json

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data"
)
TEXTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "texts"
)
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")


def cut_text_on_paragraph(fp, limit=2000):
    """Coupe un texte tous les n caractères, sans couper au milieu des paragraphes.

    Args:
        fp (str): Chemin vers le fichier à découper.
        limit (int): Nombre maximal de caractères par morceau. (Ce nombre est est outrepassé si un paragraphe est plus long que la limite.)

    Returns:
        list[str]: Liste de morceaux de texte découpés.
    """

    with open(fp) as f:
        c = f.read().split("\n\n")
    c = [i.strip() for i in c]
    n = 0
    a = []
    x = []
    for paragraph in c:
        ll = len(paragraph)
        if ll > limit:
            a.append("".join(x))
            a.append(paragraph)
            x = []
            n = 0
        elif ll + n > limit:
            a.append("".join(x))
            x = [paragraph]
            n = 0
        else:
            x.append(paragraph)
            n += ll
    return a


def cut_to_messages(prompt_file, chunks, limit=50000):
    """Construit des listes de messages pour le chat completion de ChatGPT.

    Args:
        prompt_file (str): Chemin vers le fichier contenant le prompt initial.
        chunks (list[str]): Liste des morceaux de texte découpés.
        limit (int, optional): Limite de caractères par message. Par défaut à 50000.

    Returns:
        list[list[dict]]: Liste de listes de messages pour l'API ChatGPT.
    """

    with open(prompt_file, "r") as f:
        prompt = f.read()

    base_messages = [
        {"role": "user", "content": prompt},
        {
            "role": "assistant",
            "content": "understood. i wait until you've sent the whole text and once you stop, i annotate each of them.",
        },
    ]
    a = []
    x = []
    lp = len(str(base_messages))
    n = lp
    for i in chunks:
        ll = len(i)
        if (n + ll) < limit:
            x.append(i)
            n += ll
        else:
            a.append(x)
            x = []
            n = lp
    result = []
    for x in a:
        messages = base_messages + [{"role": "user", "content": i} for i in x]
        result.append(messages)
    return result


def cut(fp, prompt_file, n):
    """Découpe un fichier texte en morceaux et les sauvegarde en fichiers texte ou JSON.

    Args:
        fp (str): Chemin vers le fichier à découper.
        n (int): le nombre de caractère maximum par morceau.
    """

    # vérifie que le fichier existe
    if not os.path.isfile(fp):
        raise ValueError(fp, "is not a file.")

    parts = cut_text_on_paragraph(fp, limit=n)

    # créer le dossier s'il n'existe pas déjà. sinon, vérifier qu'il ne contient pas déjà des fichiers.
    dest_dir = create_dest_dir(fp)

    def new_filepath(dest_dir, n, ext):
        """Génère un nouveau chemin de fichier avec un numéro de séquence et une extension.

        Args:
            dest_dir (str): Répertoire de destination.
            n (int): Numéro de séquence.
            ext (str): Extension de fichier.

        Returns:
            str: Nouveau chemin de fichier.
        """
        dest_fp = os.path.join(
            dest_dir,
            str(n) + "." + ext,
        )
        return dest_fp

    messages_list_lists = cut_to_messages(
        prompt_file=prompt_file, chunks=parts, limit=50000
    )
    for n, i in enumerate(messages_list_lists):
        fp = new_filepath(
            dest_dir=dest_dir,
            n=n,
            ext="json",
        )
        with open(fp, "w") as f:
            json.dump(obj=i, fp=f, indent=1, ensure_ascii=False)


def create_dest_dir(fp):
    """Crée un répertoire de destination basé sur le nom du fichier d'origine.

    Args:
        fp (str): Chemin vers le fichier d'origine.

    Returns:
        str: Chemin vers le répertoire de destination.

    Exemple:
        fichier initial:
            project/texts/mobydick.txt

        dossier créer:
            project/data/chunks/mobydick/

        les morceaux:
            project/data/chunks/mobydick/1.txt
            project/data/chunks/mobydick/2.txt
    """

    # récupère le nom du fichier
    filename = os.path.basename(fp)

    # enlève l'extension, s'il y en a une
    if "." in filename:
        filename = filename[: filename.index(".")]

    # construit le chemin de fichier
    dirpath = os.path.join(CHUNKS_DIR, filename)

    # crée le dossier s'il n'existe pas
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)

    # erreur: si le dossier n'est pas vide.
    elif len(os.listdir(dirpath)) != 0:
        raise ValueError(dirpath, "is not empty.")

    return dirpath


if __name__ == "__main__":
    # prompt_file = "../prompts/2024-05-26.txt"
    prompt_file = "../prompts/2024-05-27.txt"  # test

    for filename in os.listdir(TEXTS_DIR):
        if filename.replace(".txt", "") not in os.listdir(
            CHUNKS_DIR
        ) and not filename.startswith("LICENSE"):
            fp = os.path.join(TEXTS_DIR, filename)
            cut(fp=fp, prompt_file=prompt_file, n=2000)
