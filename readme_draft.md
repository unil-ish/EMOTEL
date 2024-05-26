# EMOTEL: "Emotion Ontology for Literary Exploration".

Une ontologie représentant les émotions dans des textes littéraires.

Ce projet a été réalisé dans le cadre du cours "Programmation pour le Web sémantique" de Davide Picca (SLI, Lettres, UNIL) au printemps 2024.

## But du projet

Ce projet cherche à représenter les émotions dans un texte littéraire en créant une ontologie à l'aide du logiciel [Protégé](https://protege.stanford.edu/).

Nous utilisons ensuite des LLMs pour essayer de peupler notre ontologie au moyen de prompts ajustés pour effectuer cette tâche.

## Étapes du projet

1. Identification des émotions et informations que nous souhaitons recenser dans notre ontologie. 

2. Alignement avec des ontologies existantes et récupération de classes et de propriétés intéressantes pour notre cas.

3. Création d'une hiérarchie de classe de notre ontologie.

4. Développement de prompts permettant d'extraire les informations nécessaires au peuplement de notre ontologie.

5. Développement de scripts permettant l'ajouts de nos individus dans l'ontologie.

## Structure de ce repository

| Dossier | Contenu |
|---------|---------|
| Data | Contient les textes complets de notre corpus, ainsi que le découpage (pour les requêtes à CHat GPT) ainsi que les réponses d'annotations au format JSON |
| Doc | Documentation concernant la construction de notre ontologie ainsi que de nos réflexions théoriques autour d'une ontologie des émotions littéraires |
| Prompts | Contient différents itérations de la construction de nos prompts |
| Scripts | Contient scripts conçus pour traiter nos données |

## Dépendances

Se référer au fichier requirements.txt pour une liste exacte.

Nous vous encourageons à exécuter nos scripts dans un environnement virtuel. Pour installer le fichier `requirements.txt`, exécutez la commande suivante dans un terminal:
- Unix/macOS: `python3 -m pip install -r requirements.txt`
- Windows: `py -m pip install -r requirements.txt`

## Crédits

Ce projet a été réalisé par: (TODO: corriger les noms)

- Zakari
- Amélie
- Annaël
- Thibault
- Johan
