"""coupe un texte en textes plus petits d'au maximum 2000 caractères, sans couper au milieu des lignes."""

import argparse
import os
import json

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
    "-d",
    "--destination",
    action="store",
    type=str,
    help="le dossier (ou le fichier) où placer les résultats",
    default=None,
)
parser.add_argument(
    "-P",
    "--paragraph",
    action="store_true",
    default=False,
    help="ne sépare pas les paragraphes.",
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


def cut_text_on_newlines(fp, limit):
    """coupe un texte tout les N caractères, sans couper au milieu des lignes."""

    with open(fp) as f:
        c = f.readlines()
    n = 0
    a = []
    x = []
    for line in c:
        ll = len(line)
        if n + ll <= limit:
            x.append(line)
            n += ll
        else:
            a.append("".join(x))
            x = [line]
            n = 0
    return a


def cut_text_on_paragraph(fp, limit):
    """coupe un texte tout les N caractères, sans couper au milieu des paragraphes."""
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
        if n + ll < limit:
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

    paragraph = args.paragraph
    n = args.character_number

    # vérifie que le fichier existe
    if not os.path.isfile(fp):
        raise ValueError(fp, "is not a file.")

    # assigne la fonction qui correspond à la méthode choisie
    if paragraph is True:
        fn = cut_text_on_paragraph
    else:
        fn = cut_text_on_newlines

    parts = fn(fp, n)
    return parts


def new_filepath(fp, dest_dir, n, ext):
    filename = os.path.basename(fp)
    dest_fp = os.path.join(
        dest_dir,
        filename + "_" + str(n) + "." + ext,
    )
    return dest_fp


if __name__ == "__main__":
    args = parser.parse_args()

    # créer le dossier s'il n'existe pas déjà. sinon, vérifier qu'il ne contient pas déjà des fichiers.
    destination = os.path.realpath(args.destination)
    if not os.path.isdir(destination):
        os.mkdir(destination)
    elif len(os.listdir(destination)) != 0:
        raise ValueError(destination, "is not empty.")

    parts = cut(args)

    # prépare des listes de messages pour chatgpt et les écrits au format json.
    if args.json is True:
        messages_list_lists = cut_to_messages(
            prompt=args.prompt, chunks=parts, limit=5000
        )
        for n, i in enumerate(messages_list_lists):
            fp = new_filepath(
                fp=args.file,
                dest_dir=destination,
                n=n,
                ext="json",
            )
            with open(fp, "w") as f:
                json.dump(obj=i, fp=f)
        quit(0)
    else:
        for n, x in enumerate(parts):
            fp = new_filepath(
                fp=args.file,
                dest_dir=destination,
                n=n,
                ext="txt",
            )
            with open(fp, "w") as f:
                f.write(x)
