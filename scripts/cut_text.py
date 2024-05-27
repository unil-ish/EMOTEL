import argparse
import os
import json

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data"
)
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--file",
    action="store",
    type=str,
    help="le fichier à découper",
    required=True,
)
parser.add_argument(
    "-n",
    "--character-number",
    action="store",
    type=int,
    default=2000,
    help="le nombre de caractère maximal par morceau.",
)
parser.add_argument(
    "-j",
    "--json",
    action="store_true",
    default=False,
)
parser.add_argument(
    "-p",
    "--prompt-file",
    action="store",
    type=str,
    help="le fichier avec le prompt initial.",
    required=True,
)


def cut_text_on_paragraph(fp, limit=2000):
    """Coupe un texte tout les n caractères, sans couper au milieu des paragraphes.

    `fp`: le chemin du fichier à découper.
    `limit`: le nombre de caractères maximal. celui-ci est outrepassé si un paragraphe est plus long que la limite.
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
    """Construit des listes de messages pour le chat completion de chatgpt.

    `prompt_file`: le chemin du fichier qui contient le prompt initial, celui dans lequel sont données les consignes d'annotations

    `chunks`: les morceaux de textes, découpés en messages.

    `limit`: la limite de caractères que doit avoir l'ensemble des messages (chatgpt limite par défaut à 60'000 caractères par requests).
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


def cut(args):
    """découpe un texte pour construire des messages à envoyer à chatgpt."""

    fp = args.file
    n = args.character_number

    # vérifie que le fichier existe
    if not os.path.isfile(fp):
        raise ValueError(fp, "is not a file.")

    parts = cut_text_on_paragraph(fp, limit=n)

    # créer le dossier s'il n'existe pas déjà. sinon, vérifier qu'il ne contient pas déjà des fichiers.
    dest_dir = create_dest_dir(args.file)

    def new_filepath(fp, dest_dir, n, ext):
        dest_fp = os.path.join(
            dest_dir,
            str(n) + "." + ext,
        )
        return dest_fp

    # prépare des listes de messages pour chatgpt et les écrits au format json.
    if args.json is True:
        messages_list_lists = cut_to_messages(
            prompt_file=args.prompt_file, chunks=parts, limit=50000
        )
        for n, i in enumerate(messages_list_lists):
            fp = new_filepath(
                fp=args.file,
                dest_dir=dest_dir,
                n=n,
                ext="json",
            )
            with open(fp, "w") as f:
                json.dump(obj=i, fp=f, indent=1, ensure_ascii=False)
    else:
        for n, x in enumerate(parts):
            fp = new_filepath(
                fp=args.file,
                dest_dir=dest_dir,
                n=n,
                ext="txt",
            )
            with open(fp, "w") as f:
                f.write(x)


def create_dest_dir(fp):
    """créer un répertoire pour les morceaux du fichier découper.

    ex:
        fichier initial:
            project/data/texts/mobydick.txt

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
    args = parser.parse_args()
    cut(args)
