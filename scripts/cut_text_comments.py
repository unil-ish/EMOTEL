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
    help="Le fichier à découper.",
    required=True,
)
parser.add_argument(
    "-n",
    "--character-number",
    action="store",
    type=int,
    default=2000,
    help="Le nombre de caractères maximal par morceau.",
)
parser.add_argument(
    "-j",
    "--json",
    action="store_true",
    default=False,
    help="Option pour générer des fichiers au format JSON.",
)
parser.add_argument(
    "-p",
    "--prompt-file",
    action="store",
    type=str,
    help="Le fichier contenant le prompt initial.",
    required=True,
)


def cut_text_on_paragraph(fp: str, limit: int) -> list[str]:
    """Coupe un texte tous les n caractères, sans couper au milieu des paragraphes.

    Args:
        fp (str): Chemin vers le fichier à découper.
        limit (int): Nombre maximal de caractères par morceau.

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


def cut_to_messages(prompt_file: str, chunks: list[str], limit: int = 50000) -> list[list[dict]]:
    """Construit des listes de messages pour le chat completion de ChatGPT.

    Args:
        prompt_file (str): Chemin vers le fichier contenant le prompt initial.
        chunks (list[str]): Liste des morceaux de texte découpés.
        limit (int, optional): Limite de caractères par message. Par défaut à 50000.

    Returns:
        list[list[dict]]: Liste de listes de messages pour l'API ChatGPT.
    """
    with open(prompt_file, 'r') as f:
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


def cut(args: argparse.Namespace) -> None:
    """Découpe un fichier texte en morceaux et les sauvegarde en fichiers texte ou JSON.

    Args:
        args (argparse.Namespace): Arguments passés en ligne de commande.
    """
    fp = args.file
    n = args.character_number

    if not os.path.isfile(fp):
        raise ValueError(f"{fp} is not a file.")

    parts = cut_text_on_paragraph(fp, n)

    dest_dir = create_dest_dir(args.file)

    if args.json:
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


def new_filepath(fp: str, dest_dir: str, n: int, ext: str) -> str:
    """Génère un nouveau chemin de fichier avec un numéro de séquence et une extension.

    Args:
        fp (str): Chemin vers le fichier d'origine.
        dest_dir (str): Répertoire de destination.
        n (int): Numéro de séquence.
        ext (str): Extension de fichier.

    Returns:
        str: Nouveau chemin de fichier.
    """
    dest_fp = os.path.join(
        dest_dir,
        f"{n}.{ext}",
    )
    return dest_fp


def create_dest_dir(fp: str) -> str:
    """Crée un répertoire de destination basé sur le nom du fichier d'origine.

    Args:
        fp (str): Chemin vers le fichier d'origine.

    Returns:
        str: Chemin vers le répertoire de destination.
    """
    filename = os.path.basename(fp)
    if "." in filename:
        filename = filename[: filename.index(".")]
    dirpath = os.path.join(CHUNKS_DIR, filename)
    if not os.path.isdir(dirpath):
        os.mkdir(dirpath)
    elif len(os.listdir(dirpath)) != 0:
        raise ValueError(f"{dirpath} is not empty.")
    return dirpath


if __name__ == "__main__":
    args = parser.parse_args()
    cut(args)
