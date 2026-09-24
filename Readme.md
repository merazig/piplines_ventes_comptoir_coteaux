# Pipeline de ventes — Comptoir des Coteaux

Pipeline ETL permettant de transformer les données de ventes du Comptoir des Coteaux, de produire un chiffre d'affaires exploitable et d'identifier les vins premium.

Le traitement est orchestré avec Kestra, les fichiers sources sont stockés dans MinIO, les transformations principales sont réalisées avec DuckDB, et Pandas est disponible comme solution de fallback.

## Architecture
```
                    ┌─────────────────────┐
                    │       MinIO         │
                    │                     │
                    │ Fichier_erp.xlsx    │
                    │ fichier_liaison.xlsx│
                    │ Fichier_web.xlsx    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ convert_to_parquet  │
                    │       Python        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     execute_sql     │
                    │      DuckDB         │
                    │                     │
                    │ clean.sql           │
                    │ deduplicate.sql     │
                    │ merge.sql           │
                    │ sales.sql           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       z_score       │
                    │       Pandas        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       tests         │
                    │  contrôles qualité  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     test_sales      │
                    │ rapport de contrôle │
                    └─────────────────────┘

```
## Fonctionnement

Les trois fichiers Excel sont déposés par l'utilisateur dans MinIO :
```
input/Fichier_erp.xlsx
input/fichier_liaison.xlsx
input/Fichier_web.xlsx
```

Le pipeline est ensuite exécuté par Kestra.

Les données Parquet sont organisées par période :
```
parquet/YYYY-MM/
├── bronze/
│   ├── erp.parquet
│   ├── liaison.parquet
│   └── web.parquet
│
├── silver/
│   ├── web_clean.parquet
│   ├── web_deduplicated.parquet
│   └── merged.parquet
│
└── gold/
    └── sales.parquet
```

Cette organisation permet de conserver les traitements séparés entre les données brutes, nettoyées et finales.

## Traitements SQL

Quatre scripts DuckDB sont exécutés dans l'ordre :

1. clean.sql

2. deduplicate.sql

3. merge.sql

4. sales.sql

## Nettoyage Web

Les lignes Web dont le sku est absent sont supprimées.

## Dédoublonnage Web

Les données Web sont filtrées afin de conserver les produits nécessaires au rapprochement.

## Fusion

Les données ERP, liaison et Web sont rapprochées à partir des identifiants produits.

## Chiffre d'affaires

Le chiffre d'affaires est calculé à partir du prix et du nombre de ventes :
```
revenue = price × total_sales
```
## Détection des vins premium

Le script `scripts/z_score.py` calcule un score Z sur le prix des vins.
```
z = (prix - moyenne) / écart-type
```

Les vins dont :
```
z > 2
```

sont considérés comme premium pour ce traitement.

Deux fichiers CSV sont produits :
```
output/YYYY-MM/vins_premium.csv
output/YYYY-MM/vins_non_premium.csv
```

Le rapport de chiffre d'affaires est produit au format Excel :
```
output/YYYY-MM/rapport_ca.xlsx
```
## Contrôles

Les tests sont exécutés **après toutes les tâches nominales**.

Ils vérifient notamment les volumes de données et le chiffre d'affaires produit.

Les valeurs de référence utilisées lors de la validation sont :

|Contrôle | Valeur attendue |
| --- | --- |
|ERP après dédoublonnage | 825 lignes |
|Liaison après dédoublonnage | 825 lignes |
|Web après nettoyage | 1 428 lignes |
|Web après dédoublonnage | 714 lignes |
|Fichier fusionné | 714 lignes |
|Chiffre d'affaires total | 70 568,60 € |
|Vins premium détectés (z > 2) | 30 |

Le script `test_sales` affiche également ces résultats à la fin du pipeline.

## Fallback Pandas

Une implémentation Pandas du traitement SQL est également disponible comme solution de secours.

Elle utilise les fonctions de lecture et d'upload présentes dans `scripts/minio_client.py`.

Le fallback reprend les mêmes étapes fonctionnelles :
```
clean Web
    ↓
deduplicate Web
    ↓
merge
    ↓
calculate sales
```

Il peut être utilisé lorsque le traitement DuckDB n'est pas disponible ou rencontre un problème.

## Orchestration avec Kestra

Kestra orchestre l'ensemble du pipeline.

Le flow exécute :
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

Le déclenchement automatique est configuré avec un cron mensuel :
```
triggers:
  - id: monthly
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 15 * *"
    timezone: Europe/Paris
```

Le traitement est donc lancé **le 15 de chaque mois à 9h.**

Les fichiers sources sont gérés directement dans MinIO. Si les fichiers n'ont pas été remplacés avant l'exécution mensuelle, le pipeline traite les fichiers actuellement présents dans `input/`.

## Technologies

- Python 3.12

- Pandas

- DuckDB

- PyArrow

- MinIO

- Kestra

- Docker

- Git / GitHub

## Installation

Le projet utilise une image Docker contenant les dépendances nécessaires.

Les paramètres de connexion à MinIO sont fournis par les variables d'environnement :
```
S3_ENDPOINT
MINIO_ROOT_USER
MINIO_ROOT_PASSWORD
MINIO_BUCKET
```

Les identifiants ne sont pas stockés dans le dépôt.
## Génération de `.env_encoded`

Depuis PowerShell, avec un fichier `.env` contenant `MINIO_ROOT_USER` et `MINIO_ROOT_PASSWORD` :

```powershell
$envFile = Get-Content .env
$variables = @{}

foreach ($line in $envFile) {
    if ($line -match '^\s*([^#=]+)\s*=\s*(.*)\s*$') {
        $variables[$matches[1].Trim()] = $matches[2].Trim()
    }
}

$user = [Convert]::ToBase64String(
    [Text.Encoding]::UTF8.GetBytes($variables["MINIO_ROOT_USER"])
)

$password = [Convert]::ToBase64String(
    [Text.Encoding]::UTF8.GetBytes($variables["MINIO_ROOT_PASSWORD"])
)

@"
SECRET_MINIO_ROOT_USER=$user
SECRET_MINIO_ROOT_PASSWORD=$password
"@ | Set-Content .env_encoded.example
```
## Exécution

Le pipeline complet est normalement lancé par Kestra.

Pour exécuter les différents traitements directement dans le conteneur :
```
PYTHONPATH=/app python -m scripts.convert_to_parquet
PYTHONPATH=/app python -m scripts.execute_sql
PYTHONPATH=/app python -m scripts.z_score
PYTHONPATH=/app python -m tests.tests
PYTHONPATH=/app python -m tests.test_sales
```
## Résultats attendus

À l'issue d'une exécution réussie, le pipeline produit :

- les fichiers Parquet organisés par période dans MinIO ;

- le rapport de chiffre d'affaires au format .xlsx ;

- la liste des vins premium au format .csv ;

- la liste des vins non premium au format .csv ;

- les résultats des contrôles de qualité.

## Validation

Le pipeline a été testé avec les données de référence du projet.

Les résultats obtenus sont conformes aux valeurs attendues :
```
ERP après dédoublonnage : 825 lignes
Liaison après dédoublonnage : 825 lignes
Web après nettoyage : 1 428 lignes
Web après dédoublonnage : 714 lignes
Fichier fusionné : 714 lignes
Chiffre d'affaires total : 70 568,60 €
Vins premium détectés (z > 2) : 30
```
## Dépôt

Le code source, les scripts Python, les scripts SQL, le flow Kestra et la documentation du projet sont disponibles dans ce dépôt GitHub.