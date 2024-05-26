import argparse
import os
import json

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "data"
)
CHUNKS_DIR = os.path.join(DATA_DIR, "chunks")
TEXTS_DIR = os.path.join(DATA_DIR, "texts")

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
    "--prompt",
    action="store",
    type=str,
    help="le fichier avec le prompt initial.",
    required=True,
)


def cut_text_on_paragraph(fp, limit):
    """coupe un texte tout les n caractères, sans couper au milieu des paragraphes."""

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


def cut_to_messages(prompt, chunks, limit=50000):
    """construit des listes de messages pour le chat completion de chatgpt."""
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
    fp = args.file
    n = args.character_number

    # vérifie que le fichier existe
    if not os.path.isfile(fp):
        raise ValueError(fp, "is not a file.")

    parts = cut_text_on_paragraph(fp, n)

    # créer le dossier s'il n'existe pas déjà. sinon, vérifier qu'il ne contient pas déjà des fichiers.
    dest_dir = create_dest_dir(args.file)

    # prépare des listes de messages pour chatgpt et les écrits au format json.
    if args.json is True:
        messages_list_lists = cut_to_messages(
            prompt=args.prompt, chunks=parts, limit=50000
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


def new_filepath(fp, dest_dir, n, ext):
    dest_fp = os.path.join(
        dest_dir,
        str(n) + "." + ext,
    )
    return dest_fp


def create_dest_dir(fp):
    filename = os.path.basename(fp)
    if "." in filename:
        filename = filename[: filename.index(".")]
    dirpath = os.path.join(CHUNKS_DIR, filename)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
    elif len(os.listdir(dirpath)) != 0:
        raise ValueError(dirpath, "is not empty.")
    return dirpath


if __name__ == "__main__":
    args = parser.parse_args()
    cut(args)
