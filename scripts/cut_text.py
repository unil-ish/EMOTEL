"""coupe un texte en textes plus petits d'au maximum 2000 caractères, sans couper au milieu des lignes."""

import argparse
import os

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


def cut_text_on_newlines(fp, limit):
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


if __name__ == "__main__":
    args = parser.parse_args()
    parts = cut(args)
    destination = os.path.realpath(args.destination)

    # créer le dossier s'il n'existe pas déjà
    if not os.path.isdir(destination):
        os.mkdir(destination)
    # sinon, vérifier qu'il ne contient pas déjà des fichiers.
    elif len(os.listdir(destination)) != 0:
        raise ValueError(destination, "is not empty.")
    for n, x in enumerate(parts):
        with open(
            os.path.join(
                destination,
                os.path.basename(args.file) + "_" + str(n),
            ),
            "w",
        ) as f:
            f.write(x)
