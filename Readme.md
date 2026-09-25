# 🍷 Pipeline de ventes — Comptoir des Coteaux
Pipeline ETL permettant d'automatiser le traitement mensuel des données de ventes du Comptoir des Coteaux.

Le pipeline rapproche les données de l'ERP et de la boutique en ligne, calcule le chiffre d'affaires par produit et le chiffre d'affaires total, puis identifie les vins premium à partir d'un z-score calculé sur le prix.

L'orchestration est assurée par Kestra, le stockage objet par MinIO, les transformations principales par DuckDB / SQL et les traitements statistiques par Python / Pandas.

## 📌 Sommaire
- Contexte

- Objectifs

- Architecture technique

- Architecture du projet

- Technologies utilisées

- Prérequis

- Installation

- Configuration des variables d'environnement

- Démarrage avec Docker Compose

- Configuration de MinIO

- Configuration de Kestra

- Exécution du pipeline

- Déroulement des traitements

- Transformation Excel vers Parquet

- Nettoyage des données Web

- Dédoublonnage

- Fusion des sources

- Calcul du chiffre d'affaires

- Détection des vins premium

- Exports

- Tests et contrôles qualité

- Tests en développement et en production

- Résultats de référence

- Fallback Pandas

- Planification automatique

- Gestion des erreurs

- Exécution manuelle des scripts

- Dépannage

- Documentation

- Suivi du projet

- Évolutions possibles

## 📖 Contexte
Le Comptoir des Coteaux utilise plusieurs sources de données qui ne partagent pas les mêmes identifiants.

Les données sont issues de trois fichiers :
```
Fichier_erp.xlsx
fichier_liaison.xlsx
Fichier_web.xlsx
```
L'ERP contient notamment les informations produits et les prix.

La boutique en ligne contient les données liées aux ventes.

Une table de correspondance permet de relier les deux systèmes :
```
ERP
product_id
    │
    ▼
fichier_liaison
product_id ↔ id_web
    │
    ▼
Web
sku
```
Le traitement était auparavant réalisé manuellement. L'objectif de ce projet est de rendre ce traitement reproductible, automatisé, contrôlé et planifié.

## 🎯 Objectifs
Le pipeline doit permettre de :

- récupérer les trois fichiers sources ;

- convertir les fichiers Excel en Parquet ;

- nettoyer les données ;

- supprimer les doublons ;

- rapprocher ERP et Web grâce à la table de liaison ;

- calculer le chiffre d'affaires par produit ;

- calculer le chiffre d'affaires total ;

- calculer le z-score des prix ;

- identifier les vins premium ;

- identifier les vins ordinaires ;

- produire les fichiers Excel et CSV attendus ;

- contrôler automatiquement la qualité des résultats ;

- exécuter le traitement automatiquement chaque mois.

## 🏗️ Architecture technique
```
                         ┌─────────────────────────┐
                         │         MINIO           │
                         │                         │
                         │ input/                  │
                         │ ├── Fichier_erp.xlsx    │
                         │ ├── fichier_liaison.xlsx│
                         │ └── Fichier_web.xlsx    │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │  convert_to_parquet.py  │
                         │         Python          │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │         BRONZE          │
                         │                         │
                         │ erp.parquet             │
                         │ liaison.parquet         │
                         │ web.parquet             │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │     execute_sql.py      │
                         │         DuckDB          │
                         └────────────┬────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                │                     │                     │
                ▼                     ▼                     ▼
           clean.sql          deduplicate.sql          merge.sql
                                                           │
                                                           ▼
                                                  merged.parquet
                                                           │
                                                           ▼
                                                     sales.sql
                                                           │
                                                           ▼
                                                    sales.parquet
                                                           │
                                      ┌────────────────────┴───────────────┐
                                      │                                    │
                                      ▼                                    ▼
                              export_sales.py                       z_score.py
                                      │                                    │
                                      ▼                                    ▼
                              rapport_ca.xlsx                     Premium / Ordinaire
                                      │                                    │
                                      └────────────────┬───────────────────┘
                                                       ▼
                                                tests/tests.py
                                                       │
                                                       ▼
                                              tests/test_sales.py
```
### Principe d'architecture
Le principe retenu est :

**Kestra orchestre, les scripts traitent les données.**

Kestra est donc responsable de l'enchaînement des tâches et de leur exécution.

La logique métier reste dans :

- les scripts Python ;

- les scripts SQL DuckDB.

Cela permet de conserver un workflow Kestra lisible et de faire évoluer les traitements sans transformer le YAML en code métier.

Le flow actuellement versionné contient 106 lignes et orchestre les différentes étapes du pipeline. 


## 📁 Architecture du projet
```
piplines_ventes_comptoir_coteaux/
│
├── data/
│   └── fichiers sources Excel
│
├── docs/
│   ├── Logigramme.png
│   ├── note_cadrage.md
│   └── captures/
│       ├── Kestra_installed.jpg
│       └── execution.jpg
│
├── flows/
│   └── ventes_comptoir_coteaux.yaml
│
├── scripts/
│   ├── convert_to_parquet.py
│   ├── execute_sql.py
│   ├── export_sales.py
│   ├── fallback_pandas.py
│   ├── minio_client.py
│   └── z_score.py
│
├── sql/
│   ├── clean.sql
│   ├── deduplicate.sql
│   ├── merge.sql
│   └── sales.sql
│
├── tests/
│   ├── tests.py
│   └── test_sales.py
│
├── outputs/
│   └── résultats générés
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .env_encoded.example
├── .gitignore
└── Readme.md
```
## 🛠️ Technologies utilisées
|Technologie | Rôle|
| --- | --- |
Python 3.12	| Scripts de traitement
Pandas	| Manipulation et statistiques
DuckDB	| Transformations SQL
PyArrow	| Format Parquet
MinIO	| Stockage objet
Kestra	| Orchestration
Docker	| Conteneurisation
Docker Compose |	Environnement local
Git / GitHub	| Versionnement

Le dépôt contient notamment un `Dockerfile`, un `docker-compose.yml`, un fichier `requirements.txt` et un `pyproject.toml`.

## 💻 Prérequis
Avant de commencer, installer :

- Git ;

- Docker ;

- Docker Compose.

Vérifier l'installation :
```
docker --version
docker compose version
git --version
```
## 📥 Installation
Cloner le dépôt :
```shell
git clone https://github.com/merazig/piplines_ventes_comptoir_coteaux.git
cd piplines_ventes_comptoir_coteaux
```
Créer ensuite le fichier d'environnement à partir du modèle fourni :
```bash
cp .env.example .env
```
Sous PowerShell :
```shell
Copy-Item .env.example .env
```
## 🔐 Configuration des variables d'environnement
Le projet utilise des variables d'environnement pour la connexion à MinIO.

Exemple :
```
S3_ENDPOINT=http://minio:9000
MINIO_ROOT_USER=admin
MINIO_ROOT_PASSWORD=mot_de_passe
MINIO_BUCKET=comptoir-coteaux
```
Les valeurs réelles ne doivent jamais être commit dans Git.

Le fichier `.env` doit rester local.

Le script `execute_sql.py` récupère notamment l'endpoint, le nom d'utilisateur, le mot de passe et le bucket depuis les variables d'environnement. 

## 🐳 Démarrage avec Docker Compose
Le projet fournit un environnement Docker permettant de lancer les services nécessaires.

Démarrer les conteneurs :
```shell
docker compose up -d
```
Vérifier leur état :
```shell
docker compose ps
```
Consulter les logs :
```shell
docker compose logs -f
```
Pour arrêter l'environnement :
```shell
docker compose down
```
Pour reconstruire les images :
```shell
docker compose build
```
Puis relancer :
```shell
docker compose up -d
```
## 🗄️ Configuration de MinIO
### 1. Accéder à MinIO
Une fois Docker Compose lancé, accéder à la console MinIO depuis le navigateur :
```
http://localhost:9001
```
Utiliser les identifiants définis dans .env.

### 2. Créer le bucket
Dans MinIO, créer un bucket :
```
comptoir-coteaux
```
Le nom doit correspondre à :
```
MINIO_BUCKET=comptoir-coteaux
```
### 3. Créer le dossier input
Dans le bucket, créer :
```
input/
```
L'arborescence initiale doit être :
```
comptoir-coteaux/
└── input/
```
### 4. Charger les fichiers Excel
Déposer dans input/ les trois fichiers :
```
input/
├── Fichier_erp.xlsx
├── fichier_liaison.xlsx
└── Fichier_web.xlsx
```
Les noms sont importants car le script de conversion recherche explicitement ces fichiers. Le script convertit ensuite les trois sources en Parquet.

## 📦 Conversion des fichiers Excel en Parquet
Le script :
```
scripts/convert_to_parquet.py
```
lit les fichiers Excel directement depuis MinIO.

Il utilise Pandas pour la lecture Excel et convertit les fichiers au format Parquet.

Les fichiers sont stockés dans :
```
parquet/YYYY-MM/bronze/
```
avec :
```
erp.parquet
liaison.parquet
web.parquet
```
Le script adapte également les types des identifiants Web avant l'écriture en Parquet, notamment `id_web` et `sku`.

## 🔄 Déroulement des traitements
Le workflow suit la séquence :
```
convert_to_parquet
        ↓
execute_sql
        ↓
z_score
        ↓
tests
        ↓
test_sales
```
### 1. Transformation Excel → Parquet
```
Fichier_erp.xlsx
fichier_liaison.xlsx
Fichier_web.xlsx
          │
          ▼
convert_to_parquet.py
          │
          ▼
bronze/*.parquet
```
Cette étape constitue la zone **Bronze** du pipeline.

### 2. Nettoyage des données Web
Script SQL :
```
sql/clean.sql
```
Les lignes Web dont le `sku` est absent sont supprimées.

L'objectif est de disposer d'une clé exploitable pour les traitements suivants.

### 3. Dédoublonnage
Script :
```
sql/deduplicate.sql
```
Cette étape permet de supprimer les doublons et de conserver des clés utilisables pour les jointures.

Les résultats intermédiaires sont conservés dans la zone **Silver**.
```
silver/
├── web_clean.parquet
└── web_deduplicated.parquet
```
### 4. Fusion des sources
Script :
```
sql/merge.sql
```
La table de correspondance permet de rapprocher :
```
ERP.product_id
        │
        ▼
liaison.product_id
        │
        ▼
liaison.id_web
        │
        ▼
Web.sku
```
Le résultat de la fusion est :
```
silver/merged.parquet
```
### 5. Calcul du chiffre d'affaires
Script :
```
sql/sales.sql
```
Le chiffre d'affaires par produit est calculé selon :
```
CA produit = prix × nombre de ventes
```
soit :
```
revenue = price × total_sales
```
Le résultat est enregistré dans :

gold/sales.parquet

Le script Python `execute_sql.py` exécute les quatre scripts SQL dans l'ordre :
```
clean.sql
deduplicate.sql
merge.sql
sales.sql
```
puis déclenche l'export du rapport de ventes. 

## 📊 Calcul du z-score
Le script :
```
scripts/z_score.py
```
calcule le score Z sur le prix des vins.

Formule :
```
z = (prix - moyenne) / écart-type
```
La règle métier est :
```
z > 2  → vin premium
z ≤ 2  → vin ordinaire
```
Cette classification permet de générer deux populations distinctes.

## 📤 Exports
Le pipeline produit les fichiers suivants.

### Rapport de chiffre d'affaires
```
rapport_ca.xlsx
```
Le rapport contient le chiffre d'affaires par produit ainsi que le chiffre d'affaires total.

### Vins premium
```
vins_premium.csv
```
Ce fichier contient les vins dont :
```
z > 2
```
### Vins ordinaires
```
vins_non_premium.csv
```
Ce fichier contient les vins dont :
```
z ≤ 2
```
Les fichiers sont organisés par période :
```
output/
└── YYYY-MM/
    ├── rapport_ca.xlsx
    ├── vins_premium.csv
    └── vins_non_premium.csv
```
## 🧪 Tests et contrôles qualité
Le pipeline contient deux scripts de contrôle :
```
tests/tests.py
tests/test_sales.py
```
### `tests.py`
Il vérifie notamment :

- l'absence de valeurs manquantes ;

- l'absence de doublons ;

- la cohérence des jointures ;

- la cohérence du chiffre d'affaires ;

- la cohérence de la classification par z-score.

### `test_sales.py`
Ce script est destiné au **contrôle des résultats de l'exécution mensuelle**.

Il affiche notamment :
```
ERP après dédoublonnage
Liaison après dédoublonnage
Web après nettoyage
Web après dédoublonnage
Fichier fusionné
Chiffre d'affaires total
Nombre de vins premium
```
Il ne compare pas systématiquement chaque nouvelle exécution à une valeur fixe avec des `assert`.

C'est volontaire : les données commerciales d'un nouveau mois peuvent naturellement avoir des volumes et un chiffre d'affaires différents.

## 🔬 Tests en développement et en production
Pendant le développement, les contrôles ont été effectués après chaque étape.

Cela permettait de localiser rapidement une erreur :
```
Étape
  ↓
Test
  ↓
Étape suivante
```
Pour le workflow de production, les tests sont regroupés après les traitements nominaux :
```
convert_to_parquet
        ↓
execute_sql
        ↓
z_score
        ↓
tests
        ↓
test_sales
```
Ce choix permet de conserver un flow Kestra plus court et plus lisible tout en conservant les contrôles qualité.

Les tests ne sont donc pas supprimés : ils sont regroupés dans une étape dédiée.

## ✅ Résultats de référence
Avec les données de référence fournies dans le brief, les résultats obtenus sont :

Contrôle	| Résultat attendu
 --- | ---
ERP après dédoublonnage	| 825 lignes
Liaison après dédoublonnage	| 825 lignes
Web après nettoyage	| 1428 lignes
Web après dédoublonnage	| 714 lignes
Fichier fusionné	| 714 lignes
Chiffre d'affaires total	| 70 568,60 €
Vins premium (z > 2)	| 30

Ces valeurs servent à **valider le pipeline avec le jeu de données de référence.**

Elles ne sont pas considérées comme des valeurs fixes pour les futures exécutions mensuelles.

## 🪣 Organisation du stockage MinIO
Le stockage est organisé par période et par niveau de transformation :
```
comptoir-coteaux/
│
├── input/
│   ├── Fichier_erp.xlsx
│   ├── fichier_liaison.xlsx
│   └── Fichier_web.xlsx
│
├── parquet/
│   └── YYYY-MM/
│       │
│       ├── bronze/
│       │   ├── erp.parquet
│       │   ├── liaison.parquet
│       │   └── web.parquet
│       │
│       ├── silver/
│       │   ├── web_clean.parquet
│       │   ├── web_deduplicated.parquet
│       │   └── merged.parquet
│       │
│       └── gold/
│           └── sales.parquet
│
└── output/
    └── YYYY-MM/
        ├── rapport_ca.xlsx
        ├── vins_premium.csv
        └── vins_non_premium.csv
```
Cette organisation permet de séparer :

- **Bronze** : données converties depuis les sources ;

- **Silver** : données nettoyées, dédoublonnées et fusionnées ;

- **Gold** : données finales utilisées pour les ventes ;

- **Output** : fichiers destinés aux utilisateurs.

## 🔁 Fallback Pandas
Une implémentation alternative est disponible dans :
```
scripts/fallback_pandas.py
```
Elle permet de reproduire les principales transformations sans utiliser DuckDB.

Le traitement reprend les étapes :
```
Nettoyage Web
      ↓
Dédoublonnage
      ↓
Fusion
      ↓
Calcul des ventes
```
Le module :
```
scripts/minio_client.py
```
fournit les fonctions nécessaires à la lecture et à l'upload des fichiers dans MinIO.

Le fallback permet donc de disposer d'une solution alternative lorsqu'un problème empêche l'utilisation du traitement DuckDB.

## ⏰ Planification automatique
Le workflow Kestra est planifié avec un trigger mensuel.
```
triggers:
  - id: monthly
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 15 * *"
    timezone: Europe/Paris
```
La planification signifie :
```
Jour       : 15
Heure      : 09:00
Fréquence  : mensuelle
Fuseau     : Europe/Paris
```
Le pipeline traite les fichiers présents dans :
```
input/
```
au moment du déclenchement.

Il faut donc déposer les nouveaux fichiers sources dans MinIO avant l'exécution mensuelle.

## 🧭 Configuration de Kestra
### Accéder à Kestra
Avec Docker Compose lancé :
```
http://localhost:8080
```
### Importer le flow
Le workflow est disponible ici :
```
flows/ventes_comptoir_coteaux.yaml
```
Il peut être importé dans Kestra depuis l'interface.

Le workflow contient les tâches nécessaires à l'exécution du pipeline.

### Secrets MinIO
Les identifiants MinIO ne sont pas écrits en clair dans le flow.

Ils doivent être configurés dans Kestra comme secrets.

Exemple :
```
MINIO_ROOT_USER
MINIO_ROOT_PASSWORD
``` 
Le flow peut ensuite les utiliser via le mécanisme de secrets de Kestra.

## ▶️ Exécution du pipeline
### Exécution automatique
Une fois le trigger actif, Kestra lance automatiquement le pipeline :
```
15 du mois
     ↓
09:00 Europe/Paris
     ↓
convert_to_parquet
     ↓
execute_sql
     ↓
z_score
     ↓
tests
     ↓
test_sales
```
### Exécution manuelle
Pour tester le pipeline sans attendre le 15 du mois, utiliser le bouton Execute dans Kestra.

Cette méthode est recommandée après :

- une modification du flow ;

- une modification d'un script ;

- une modification SQL ;

- un changement de configuration MinIO.

### 🖥️ Exécution manuelle des scripts
Les scripts peuvent également être exécutés directement dans le conteneur Python.

Conversion
```shell
PYTHONPATH=/app python -m scripts.convert_to_parquet
```
SQL
```shell
PYTHONPATH=/app python -m scripts.execute_sql
```
Z-score
```shell
PYTHONPATH=/app python -m scripts.z_score
```
Tests
```shell
PYTHONPATH=/app python -m tests.tests
```
Contrôle des ventes
```shell
PYTHONPATH=/app python -m tests.test_sales
```
Cette méthode est particulièrement utile pour le développement et le diagnostic.

## 🚨 Gestion des erreurs
Plusieurs problèmes peuvent interrompre le pipeline :

- fichier source absent ;

- fichier source mal nommé ;

- erreur de connexion à MinIO ;

- identifiants incorrects ;

- erreur SQL ;

- problème d'environnement Docker ;

- indisponibilité de DuckDB ;

- données inattendues.

Kestra permet de suivre l'exécution tâche par tâche.

En cas d'erreur :
```
Kestra
  ↓
identifier la tâche en erreur
  ↓
consulter les logs
  ↓
corriger le problème
  ↓
relancer le traitement
```
Les traitements étant séparés dans des scripts Python et SQL, le diagnostic peut être effectué indépendamment de l'orchestration.

## 🔐 Sécurité
Aucun mot de passe ou token ne doit être stocké dans Git.

Les informations sensibles doivent rester dans :
```
.env
```
ou dans les secrets Kestra.

Le fichier `.env` doit rester ignoré par Git.

Le fichier `.env.example` fournit uniquement un modèle de configuration.

## 🧰 Dépannage
### MinIO inaccessible
Vérifier :
```
docker compose ps
```
Puis :
```
docker compose logs minio
```
La console est normalement accessible sur :
```
http://localhost:9001
```
### Kestra inaccessible
Vérifier :
```
docker compose ps
```
Puis :
```
docker compose logs kestra
```
La console est normalement accessible sur :
```
http://localhost:8080
```
### Le pipeline ne trouve pas les fichiers
Vérifier dans MinIO :
```
input/
├── Fichier_erp.xlsx
├── fichier_liaison.xlsx
└── Fichier_web.xlsx
```
Vérifier également :

- le nom du bucket ;

- les identifiants ;

- l'endpoint MinIO ;

- les secrets Kestra.

### Attention à l'endpoint MinIO
Depuis l'hôte :
```
http://localhost:9000
```
peut être utilisé pour accéder au service selon le mapping Docker.

Depuis un autre conteneur du réseau Docker, il faut utiliser le nom du service :
```
http://minio:9000
```
Le script SQL utilise par défaut :
```
http://minio:9000
```
lorsqu'aucun endpoint n'est fourni. 

## 📚 Documentation du projet
La documentation complémentaire se trouve dans `docs/`.

### Note de cadrage
📄 Note de cadrage

Elle présente :

- le besoin métier ;

- le périmètre ;

- les contraintes ;

- les questions identifiées ;

- les choix de traitement.

### Logigramme
Le logigramme représente le flux de traitement ainsi que les contrôles associés.

### Installation de Kestra
### Exécution du pipeline
## 📋 Suivi du projet
Le projet a été suivi avec OpenProject afin de gérer le backlog, le Kanban et l'avancement des différentes étapes.

### OpenProject
📌 Projet OpenProject — Comptoir des Coteaux

Le suivi a été organisé autour des différentes étapes de la mission :
```
Étape 0
Cadrage du besoin
       ↓
Étape 1
Architecture / logigramme
       ↓
Étape 2
Implémentation du pipeline
       ↓
Étape 3
Tests et validation
       ↓
Étape 4
Soutenance
```
## 📦 Livrables
Le dépôt regroupe les principaux livrables du projet :

Livrable	| Emplacement
 --- | ---
README	| Readme.md
Flow Kestra	| flows/
Scripts Python	| scripts/
Scripts SQL	| sql/
Tests	| tests/
Données sources	| data/
Documentation	| docs/
Résultats	| outputs/
Dockerfile	| Dockerfile
Docker Compose	| docker-compose.yml
Dépendances	| requirements.txt

## 🔮 Évolutions possibles
Plusieurs améliorations pourraient être ajoutées dans une version ultérieure :

- ajouter une nouvelle source de données sans modifier fortement le workflow ;

- ajouter des contrôles de schéma à l'arrivée des fichiers ;

- ajouter des notifications Kestra en cas d'échec ;

- utiliser des retries sur certaines tâches ;

- archiver automatiquement les fichiers sources ;

- ajouter une validation plus fine des types de données ;

- historiser les indicateurs de chaque exécution ;

- ajouter des contrôles statistiques supplémentaires ;

- mettre en place une CI pour tester automatiquement les scripts ;

- renforcer la gestion des versions des données.

## 🧩 Résumé
Le pipeline permet de passer automatiquement de :
```
3 fichiers Excel
      │
      ▼
     MinIO
      │
      ▼
Conversion Parquet
      │
      ▼
Nettoyage
      │
      ▼
Dédoublonnage
      │
      ▼
Fusion ERP / Liaison / Web
      │
      ▼
Calcul du chiffre d'affaires
      │
      ├───────────────┐
      ▼               ▼
Rapport Excel      Z-score
                      │
                ┌─────┴─────┐
                ▼           ▼
             Premium     Ordinaire
                │           │
                ▼           ▼
             CSV          CSV
                │           │
                └─────┬─────┘
                      ▼
                    Tests
                      │
                      ▼
                 Contrôle final
```
L'ensemble est orchestré automatiquement par Kestra et peut être exécuté chaque mois le 15 à 9h, heure de Paris.

Le pipeline permet ainsi de remplacer un traitement manuel par une chaîne reproductible, contrôlée et documentée.