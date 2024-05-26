"""coupe un texte en textes plus petits d'au maximum 2000 caractères, sans couper au milieu des lignes."""

import argparse
import os


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


def _parsearguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file", action="store", type=str, help="le fichier à découper"
    )
    parser.add_argument(
        "-d",
        "--target-dir",
        action="store",
        type="str",
        help="le dossier où placer le résultats découpé.",
    )
    parser.add_argument(
        "-p",
        "--paragraph",
        action="store_true",
        type=bool,
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
    args = parser.parse_args()
    return args


def cut(args):
    fp = args.file
    target_dir = os.path.realpath(args.target_dir)
    paragraph = args.paragraph
    n = args.character_number

    # vérifie que le fichier existe
    if not os.path.isfile(fp):
        raise ValueError(fp, "is not a file.")

    # créer le dossier s'il n'existe pas déjà
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)
    # sinon, vérifier qu'il ne contient pas déjà des fichiers.
    elif len(os.listdir(target_dir)) != 0:
        raise ValueError(target_dir, "is not empty.")

    # assigne la fonction qui correspond à la méthode choisie
    if paragraph is True:
        fn = cut_text_on_paragraph
    else:
        fn = cut_text_on_newlines

    parts = fn(fp, n)

    for n, x in enumerate(parts):
        with open(
            os.path.join(target_dir, os.path.basename(fp) + "_" + str(n)), "w"
        ) as f:
            f.write(x)


if __name__ == "__main__":
    args = _parsearguments()
    cut(args)
