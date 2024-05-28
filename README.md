# EMOTEL: "Emotion Ontology for Literary Exploration".

Une ontologie représentant les émotions dans des textes littéraires.

Ce projet a été réalisé dans le cadre du cours "Programmation pour le Web sémantique" de Davide Picca (SLI, Lettres, UNIL) au printemps 2024.

## But du projet

Ce projet cherche à représenter les émotions dans un texte littéraire en créant une ontologie à l'aide du logiciel [Protégé](https://protege.stanford.edu/).

Nous utilisons ensuite des LLMs (ici [ChatGPT](https://chatgpt.com/)) pour annoter nos textes puis des scripts python pour peupler notre ontologie.

## Étapes du projet

1. Identification des émotions et informations que nous souhaitons recenser dans notre ontologie. 

2. Alignement avec des ontologies existantes et récupération de classes et de propriétés intéressantes pour notre cas.

3. Création d'une hiérarchie de classe dans notre ontologie.

4. Développement de prompts permettant d'extraire les informations nécessaires au peuplement de notre ontologie.

5. Développement de scripts permettant l'ajouts de nos individus dans l'ontologie.

6. Création d'une deuxième ontologie étendue à partir des résultats de ChatGPT.

## Structure de ce repository

| Dossier | Contenu |
|---------|---------|
| Data | Contient les données intermédiaires au format JSON utilisées dans ce projet |
| Doc | Documentation concernant la construction de notre ontologie ainsi que de nos réflexions théoriques autour d'une ontologie des émotions littéraires |
| Ontology | Contient une première version de notre ontologie, créée avec [Protégé](https://protege.stanford.edu/) [owlready2](https://owlready2.readthedocs.io/en/latest/) ainsi qu'une deuxième qui résulte des sorties de ChatGPT et qui est créée par le script `clean_prepare_for_rdf.py`|
| Outputs | Contient les deux versions d'ontologies peuplées par le script `build_populated_ontology.py` qui repose sur la librairie [rdflib](https://rdflib.readthedocs.io/en/stable/) |
| Project guidelines | Contient le `README.md` officiel de la donnée du projet |
| Prompts | Contient différents itérations de la construction de nos prompts |
| Queries | Conient un script python qui exécute des requêtes SPARQL sur notre ontologie |
| Scripts | Contient les scripts conçus pour traiter nos données |
| Texts | Contient les textes utilisés pour peupler notre ontologie |

### Data

Ce dossier contient les éléments suivants:

- `annotations` : Contient les résultats de nos prompts appliqués aux textes de notre corpus et corrigés à certains endroits par nos soins
- `annotations_cleaned` : Contient les annotations corrigées par le script `clean_prepare_for_rdf.py` qui sont ensuite utilisées pour peupler l'ontologie
- `chunks` : Contient les textes découpés pour être passés dans ChatGPT

### Scripts

- `ask_chatgpt.py` : Annote les morceaux de textes envoyés à l'API ChatGPT et nous indique si certains fichiers doivent être corrigés à la main
- `build_populated_ontology.py` : Itère sur toutes les annotations de `annotations_cleaned` pour créer des individus et les injecter dans les ontologies `ontology.owl` et `ontology_extended.owl`
- `clean_prepare_for_rdf.py` : Normalise les noms afin qu'ils puissent être utilisés pour des URIs (typiquement en remplaçant les espaces par des underscores), et reconstruit la structure souhaitée là où ChatGPT s'éloigne du modèle.
- `cut_text.py` : Prépare l'annotation en (1) coupant les fichiers textes après un certain nombre de caractères et (2) construisant des séquences de messages adaptés à l'analyse par ChatGPT.
- `uniquiser_ids.py` : Construit des IDs utilisés pour les URIs et construit les liens entre les entités disjointes (pour des raisons techniques) au cours de l'annotation.
- `uniquiser_ids.py` : Uniformise les IDs assignés aux _FictionalCharacter_, _FictionalEvent_ et _FictionalPlace_

## Installation

1. Cloner ce repo

2. Créer un environnement virtuel (par exemple avec la librarire `venv`)

3. Installer le fichier `requirements.txt`:
    - Unix/macOS: `python3 -m pip install -r requirements.txt`
    - Windows: `py -m pip install -r requirements.txt`

## Pipeline

Pour répliquer nos résultats (en partant de `ontology/ontology.owl`) : 

1. Exécuter `clean_prepare_for_rdf.py` pour créer l'ontologie étendue `ontology_extended.owl`
2. Exécuter `cut_text.py` pour séparer les textes en vue de leur passage dans l'API de ChatGPT
3. Exécuter `ask_chatgpt.py` pour obtenir les fichiers JSON puis les vérifier
4. Exécuter `uniquiser_ids.py` pour standardiser les IDs des objets de nos fichiers JSON
5. Exécuter `build_populated_ontology.py` pour créer les deux versions d'ontologies peuplées

## Dépendances

- annotated-types==0.7.0
- anyio==4.3.0
- certifi==2024.2.2
- distro==1.9.0
- h11==0.14.0
- httpcore==1.0.5
- httpx==0.27.0
- idna==3.7
- isodate==0.6.1
- openai==1.30.3
- owlready2==0.46
- pydantic==2.7.1
- pydantic_core==2.18.2
- pyparsing==3.1.2
- rdflib==7.0.0
- six==1.16.0
- sniffio==1.3.1
- tqdm==4.66.4
- typing_extensions==4.12.0

## Crédits

Ce projet a été réalisé par: (TODO: corriger les noms)

- Zakari Rabet
- Amélie McCormick
- Annaël Madec-Prévost
- Thibault Ziegler
- Johan Cuda

Développé à l'aide de la communauté Python et Protégé, ainsi qu'avec le soutien de ChatGPT.
