# EMOTEL: "Emotion Ontology for Literary Exploration".

Une ontologie représentant les émotions dans des textes littéraires.

Ce projet a été réalisé dans le cadre du cours "Programmation pour le Web sémantique" de Davide Picca (SLI, Lettres, UNIL) au printemps 2024.

## But du projet

Ce projet cherche à représenter les émotions dans un texte littéraire en créant une ontologie à l'aide du logiciel [Protégé](https://protege.stanford.edu/).

Nous utilisons ensuite des LLMs (ici [ChatGPT](https://chatgpt.com/)) pour annoter nos textes puis des scripts python pour peupler notre ontologie.

## Étapes du projet

1. Identification des émotions et informations que nous souhaitons recenser dans notre ontologie. 

2. Alignement avec des ontologies existantes et récupération de classes et de propriétés intéressantes pour notre cas.

3. Création d'une hiérarchie de classe de notre ontologie.

4. Développement de prompts permettant d'extraire les informations nécessaires au peuplement de notre ontologie.

5. Développement de scripts permettant l'ajouts de nos individus dans l'ontologie.

## Structure de ce repository

| Dossier | Contenu |
|---------|---------|
| Data | Contient les données intermédiaires au format JSON utilisées dans ce projet |
| Doc | Documentation concernant la construction de notre ontologie ainsi que de nos réflexions théoriques autour d'une ontologie des émotions littéraires |
| Ontology | Contient la structures (classes et propriétés) de notre ontologie OWL, créée avec [Protégé](https://protege.stanford.edu/) [owlready2](https://owlready2.readthedocs.io/en/latest/)|
| Outputs | Contient l'ontologie peuplée par le script `json_to_owl.py` qui repose sur la librairie [rdflib](https://rdflib.readthedocs.io/en/stable/) |
| Project guidelines | Contient le `README.md` officiel de la donnée du projet |
| Prompts | Contient différents itérations de la construction de nos prompts |
| Queries | Conient un script python qui exécute des requêtes SPARQL sur notre ontologie |
| Scripts | Contient les scripts conçus pour traiter nos données |
| Texts | Contient les textes utilisés pour peupler notre ontologie |

## Data

Ce dossier contient les éléments suivants:

- `annotations` : Contient les résultats de nos prompts appliqués aux textes de notre corpus et corrigés à certains endroits par nos soins
- `annotations_cleaned` : Contient les annotations corrigées par le script `normalize_names.py` qui sont ensuite utilisées pour peupler l'ontologie
- `chunks` : Contient les textes découpés pour être passés dans ChatGPT

## Scripts

- `ask_chatgpt.py` : Annote les morceaux de textes envoyés à l'API ChatGPT
- `clean_prepare_for_rdf.py` : Normalise les noms afin qu'ils puissent être utilisés pour des URIs (typiquement en remplaçant les espaces par des underscores), et reconstruit la structure souhaitée là où ChatGPT s'en éloigné du modèle.
- `cut_text.py` : Prépare l'annotation en (1) coupant les fichiers textes après un certain nombre de caractères et (2) construisant des séquences de messages adaptés à l'analyse par ChatGPT.
- `uniquiser_ids.py` : Construit des IDs utilisés pour les URIs et construit les liens entre les entités disjointes (pour des raisons techniques) au cours de l'annotation.
- `json_to_owl.py` : Itère sur toutes les annotations de `annotations_cleaned` pour créer des individus et les injecter dans l'ontologie `ontology.owl`

## Dépendances

Se référer au fichier requirements.txt pour une liste exacte.

Nous vous encourageons à exécuter nos scripts dans un environnement virtuel. Pour installer le fichier `requirements.txt`, exécutez la commande suivante dans un terminal:
- Unix/macOS: `python3 -m pip install -r requirements.txt`
- Windows: `py -m pip install -r requirements.txt`

## Crédits

Ce projet a été réalisé par: (TODO: corriger les noms)

- Zakari Rabet
- Amélie Mc Cormick
- Annaël Madec-Prévost
- Thibault Ziegler
- Johan Cuda

Développé à l'aide de la communauté Python et Protégé, ainsi qu'avec le soutien de ChatGPT.
