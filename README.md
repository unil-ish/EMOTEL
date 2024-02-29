# Développement d'une Ontologie des Émotions pour l'Analyse Littéraire

Inspiré par "[EFO: the Emotion Frame Ontology](https://arxiv.org/pdf/2401.10751.pdf)" de Stefano De Giorgis et Aldo Gangemi, vous pourriez développer une ontologie basée sur OWL pour modéliser les émotions spécifiques des personnages et les situations décrites dans les textes littéraires. Cette ontologie pourrait inclure des cadres sémantiques qui capturent différents aspects de l'expérience émotionnelle, tels que les causes des émotions, les réactions des personnages et les changements au fil de la narration. Votre projet pourrait explorer comment différentes théories des émotions peuvent être intégrées et représentées au sein d'une structure ontologique unique, permettant des analyses comparatives et approfondies des textes.


## A quoi ça sert?

Voici plusieurs cas d'utilisation potentiels pour une ontologie basée sur OWL dédiée à la modélisation des émotions dans les textes littéraires :

### 1. **Analyse Académique Approfondie**:

Les chercheurs en littérature peuvent utiliser l'ontologie pour mener des analyses textuelles plus profondes et structurées, examinant comment les émotions des personnages sont représentées et évoluent à travers différents genres littéraires ou périodes historiques. Cela peut ouvrir de nouvelles perspectives sur la psychologie des personnages, la construction narrative et les thèmes émotionnels à travers la littérature.

### 2. **Éducation et Enseignement**:

Les enseignants peuvent intégrer l'ontologie dans leurs programmes d'études littéraires pour aider les étudiants à comprendre et à analyser la dimension émotionnelle des textes littéraires. Les étudiants pourraient utiliser l'ontologie pour identifier et discuter des motifs émotionnels, enrichissant ainsi leur interprétation et leur appréciation des œuvres littéraires.

### 3. **Développement de Recommandations de Lecture**:

Les bibliothèques, les librairies en ligne et les plateformes de lecture peuvent utiliser l'ontologie pour développer des systèmes de recommandation basés sur les émotions. Les utilisateurs pourraient chercher des livres qui provoquent certaines émotions ou explorer des œuvres littéraires qui traitent de thèmes émotionnels spécifiques, améliorant ainsi leur expérience de découverte de livres.

### 4. **Création de Contenu et Écriture**:

Les auteurs et les scénaristes peuvent s'appuyer sur l'ontologie pour créer des personnages plus nuancés et des intrigues émotionnellement cohérentes. L'ontologie pourrait servir de référence pour développer la profondeur émotionnelle des personnages et structurer les arcs narratifs de manière à résonner de façon plus profonde avec les lecteurs ou les spectateurs.

### 5. **Analyse Sentimentale et Émotionnelle Automatisée**:

Les développeurs de logiciels peuvent intégrer l'ontologie dans des outils d'analyse textuelle pour automatiser la détection et la classification des émotions dans les textes. Cela pourrait être utilisé dans la recherche en sciences humaines, le marketing, la psychologie des consommateurs, et d'autres domaines pour analyser les réponses émotionnelles à divers types de contenu.

### 6. **Études Interdisciplinaires**:

L'ontologie peut faciliter la collaboration entre les chercheurs en littérature, psychologie, sciences cognitives, et informatique, permettant des études interdisciplinaires sur la représentation des émotions dans les textes et leur impact sur les lecteurs. Ceci pourrait conduire à de nouvelles découvertes sur la manière dont les êtres humains traitent et réagissent aux stimuli émotionnels dans la littérature.

En adoptant une telle ontologie, les utilisateurs de différents domaines peuvent non seulement mieux comprendre les complexités des émotions dans les textes littéraires, mais aussi appliquer ces connaissances pour enrichir l'expérience littéraire, l'éducation, la recherche, et au-delà.

## Comment la faire?

Pour approfondir la conception d'une ontologie des émotions pour l'analyse littéraire en utilisant des techniques OWL, nous pouvons diviser le projet en plusieurs étapes clés :

### 1. **Définition des Classes d'Émotions Principales :**

Commencez par identifier les émotions fondamentales à inclure dans votre ontologie. Celles-ci pourraient être basées sur des théories psychologiques bien établies, telles que les émotions de base d'Ekman : Joie, Tristesse, Colère, Peur, Surprise et Dégoût. Chaque émotion peut être une classe principale dans l'ontologie.

### 2. **Identification des Propriétés et des Relations :**

Pour chaque classe d'émotion, définissez les propriétés qui décrivent les causes, les manifestations physiques et psychologiques et les effets sur le comportement des personnages. Par exemple, la tristesse pourrait avoir des propriétés telles que "causée par", "manifestée par", et "résulte en". Ajoutez des relations entre les émotions, comme "peut se transformer en" ou "est opposée à", pour refléter la complexité des expériences émotionnelles dans les textes littéraires.

Voici un exemple:

```
<!-- Definition of the class 'Sadness' -->
<owl:Class rdf:about="#Sadness">
    <rdfs:label xml:lang="en">Sadness</rdfs:label>
    <rdfs:comment xml:lang="en">An emotion characterized by feelings of disadvantage, loss, and helplessness.</rdfs:comment>
</owl:Class>

<!-- Properties for the class 'Sadness' -->
<owl:ObjectProperty rdf:about="#causedBy">
    <rdfs:label xml:lang="en">caused by</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#Event"/>
</owl:ObjectProperty>

<owl:ObjectProperty rdf:about="#manifestedBy">
    <rdfs:label xml:lang="en">manifested by</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#Behavior"/>
</owl:ObjectProperty>

<owl:ObjectProperty rdf:about="#resultsIn">
    <rdfs:label xml:lang="en">results in</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#Action"/>
</owl:ObjectProperty>

<!-- Relationships between emotions -->
<owl:ObjectProperty rdf:about="#canTransformInto">
    <rdfs:label xml:lang="en">can transform into</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#Emotion"/>
</owl:ObjectProperty>

<owl:ObjectProperty rdf:about="#isOppositeTo">
    <rdfs:label xml:lang="en">is opposite to</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#Joy"/>
</owl:ObjectProperty>

```

### 3. **Intégration avec des Éléments Littéraires :**

Étendez l'ontologie pour inclure des éléments littéraires tels que les personnages, les cadres, les événements de l'intrigue et le style narratif. Cela permet de modéliser comment les émotions sont liées à des contextes narratifs spécifiques. Par exemple, vous pouvez relier la classe "Tristesse" avec des événements de l'intrigue comme "la perte d'un proche" ou "l'échec d'un objectif".

Voici un exemple:

```
<!-- Definition of 'Sadness' class -->
<owl:Class rdf:about="#Sadness">
    <rdfs:label xml:lang="en">Sadness</rdfs:label>
    <rdfs:comment xml:lang="en">An emotion characterized by feelings of disadvantage, loss, and helplessness.</rdfs:comment>
</owl:Class>

<!-- Properties for the 'Sadness' class -->
<owl:ObjectProperty rdf:about="#causedBy">
    <rdfs:label xml:lang="en">caused by</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#PlotEvent"/>
</owl:ObjectProperty>

<owl:ObjectProperty rdf:about="#manifestedBy">
    <rdfs:label xml:lang="en">manifested by</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#CharacterBehavior"/>
</owl:ObjectProperty>

<owl:ObjectProperty rdf:about="#resultsIn">
    <rdfs:label xml:lang="en">results in</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#CharacterAction"/>
</owl:ObjectProperty>

<!-- Literary elements relations -->
<owl:ObjectProperty rdf:about="#associatedWithCharacter">
    <rdfs:label xml:lang="en">associated with character</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#LiteraryCharacter"/>
</owl:ObjectProperty>

<owl:ObjectProperty rdf:about="#occursInSetting">
    <rdfs:label xml:lang="en">occurs in setting</rdfs:label>
    <rdfs:domain rdf:resource="#Sadness"/>
    <rdfs:range rdf:resource="#Setting"/>
</owl:ObjectProperty>

<!-- Example of linking 'Sadness' with specific plot events -->
<owl:NamedIndividual rdf:about="#LossOfLovedOne">
    <rdf:type rdf:resource="#PlotEvent"/>
    <rdfs:label xml:lang="en">Loss of a Loved One</rdfs:label>
</owl:NamedIndividual>

<owl:NamedIndividual rdf:about="#FailureOfGoal">
    <rdf:type rdf:resource="#PlotEvent"/>
    <rdfs:label xml:lang="en">Failure of a Goal</rdfs:label>
</owl:NamedIndividual>

```

### 4. **Alignement avec des Ontologies Existantes :**

Pour promouvoir l'interopérabilité, alignez votre ontologie avec des standards et des ontologies existantes. Vous pourriez, par exemple, utiliser [Ontology Profile](https://raw.githubusercontent.com/dpicca/ontologies/main/character-profiling-ontology/V3/model_with_nif.rdf)  comme ontologie de base pour fournir des définitions de base et des relations. Cela aide à assurer que votre ontologie soit cohérente avec d'autres ontologies dans le domaine plus large des sciences humaines et sociales.

### 5. **Peuplement de l'Ontologie :**

Une fois la structure de l'ontologie définie, utilisez des LLM (Large Language Models) et les [prompts suggérés](./prompts.md) pour peupler votre ontologie avec des exemples tirés de textes littéraires. Cela comprend l'utilisation des LLM pour identifier et classer les émotions dans des extraits littéraires, ainsi que pour détecter les relations entre les émotions et les autres éléments littéraires. Ce processus peut être facilité par l'automatisation partielle à travers les réponses générées par les LLM aux prompts donnés, mais il nécessitera toujours une révision manuelle minutieuse pour s'assurer de la pertinence et de l'exactitude des données par rapport à votre ontologie.

#### 5.1 Sélection des Textes:

**Diversité des Genres**: Sélectionnez une gamme de textes couvrant divers genres littéraires comme les romans, les drames, etc. Cela permet de tester l'ontologie contre une variété de formes et de styles narratifs, assurant ainsi que l'ontologie est adaptable et applicable à travers différents types de littérature.

**Variété des Périodes**: Incluez des œuvres de différentes époques pour tester la capacité de l'ontologie à capturer des expressions émotionnelles qui pourraient varier avec le temps. Cela aidera à garantir que l'ontologie reste pertinente à travers différentes périodes littéraires et contextes culturels.

### 6. **Évaluation et Test :**

Évaluez l'ontologie en utilisant une série de textes littéraires variés pour vous assurer qu'elle peut capturer avec précision les émotions et leurs nuances telles qu'elles sont représentées dans la littérature. Cela peut inclure l'analyse de la manière dont les émotions changent au cours de la narration et comment elles influencent le comportement des personnages et le développement de l'intrigue.

Évaluation de la Couverture :

1. **Définition et Planification** :

   - Définissez ce que signifie "couverture" pour votre ontologie : Cela pourrait se référer à la gamme de différentes émotions, la variété de scénarios ou de contextes où les émotions sont exprimées, et la diversité des expériences émotionnelles des personnages.
   - Planifiez comment mesurer la couverture : Décidez d'un échantillon représentatif de textes littéraires incluant une large variété de genres, périodes et cultures.
2. **Collecte de Données** :

   - Collectez un ensemble de textes littéraires qui seront utilisés pour l'évaluation. Assurez-vous que cet ensemble est assez diversifié pour mettre à l'épreuve la gamme de l’ontologie.
   - Préparez les textes en les segmentant en unités analysables (par exemple, paragraphes, phrases ou chapitres).
3. **Annotation Manuelle** :

   - Faites annoter manuellement par des annotateurs les émotions, scénarios et états des personnages dans les textes en utilisant des directives qui reflètent la structure et les classes de votre ontologie.
   - Collectez et consolidez les annotations dans un jeu de données qui servira de vérité terrain pour évaluer l'ontologie.
4. **Application de l'Ontologie** :

   - Appliquez votre ontologie au même ensemble de textes, manuellement par des experts ou automatiquement à l'aide d'un outil conçu pour reconnaître et classifier le contenu émotionnel basé sur votre ontologie.
   - Enregistrez quelles émotions, scénarios et états des personnages l'ontologie a réussi à capturer et ceux qu'elle a manqués.
5. **Analyse** :

   - Comparez la sortie de l'ontologie avec le jeu de données de vérité terrain issu de l'annotation manuelle. Calculez le pourcentage de contenu émotionnel correctement identifié par l'ontologie par rapport au total identifié par les annotateurs humains.
   - Identifiez les lacunes dans la couverture de l'ontologie, telles que des émotions spécifiques, des scénarios ou des expériences de personnages qui sont constamment manqués ou sous-représentés.
   - **Pour la précision** : Évaluez chaque élément de contenu émotionnel identifié par l'ontologie et vérifiez-le par rapport aux annotations manuelles pour voir s'il a été correctement identifié.
   - **Pour le rappel** : Vérifiez tout le contenu émotionnel identifié par les annotateurs humains et voyez si l'ontologie a pu également l'identifier.
   - Calculez la précision et le rappel en utilisant les formules : Précision = Vrais Positifs / (Vrais Positifs + Faux Positifs), Rappel = Vrais Positifs / (Vrais Positifs + Faux Négatifs).

   #### Actions d'Amélioration :


   - **Pour une faible précision**, examinez l'ontologie et l'outil d'analyse de texte pour découvrir pourquoi des faux positifs se produisent. Cela pourrait être dû à des définitions trop larges ou à des classifications incorrectes.
   - **Pour un faible rappel**, identifiez quels types de contenu émotionnel sont manqués et pourquoi. Cela peut impliquer l'ajout de nouveaux concepts à l'ontologie ou l'ajustement des critères de classification.

### 7. **Itération et Amélioration :**

Sur la base des retours reçus pendant la phase d'évaluation, apportez les modifications nécessaires pour affiner et améliorer l'ontologie. Cela peut inclure l'ajout de nouvelles émotions, la refonte des relations existantes ou l'ajustement des définitions de classe pour mieux refléter la complexité des émotions dans les textes littéraires.

Cette approche détaillée vous aidera à construire une ontologie robuste et significative qui peut être utilisée pour analyser et comprendre les émotions dans les textes littéraires de manière plus profonde et systématique.
