Rapport d'avancement — Pipeline ventes Comptoir des Coteaux
1. Objectif du projet

Mettre en place un pipeline de données reproductible pour traiter les exports ERP, liaison et Web, calculer le chiffre d'affaires et identifier les vins premium, puis automatiser l'ensemble avec Kestra.

Les résultats de référence fournis par Octave sont :

Indicateur	Valeur attendue
ERP après dédoublonnage	825 lignes
Liaison après dédoublonnage	825 lignes
Web après nettoyage	1 428 lignes
Web après dédoublonnage	714 lignes
Fichier fusionné	714 lignes
Chiffre d'affaires	70 568,60 €
Vins premium (z > 2)	30
2. Travail réalisé
Conversion Excel → Parquet

Le script :

scripts/convert_to_parquet.py


fonctionne.

Les trois fichiers sont correctement convertis :

erp.parquet
liaison.parquet
web.parquet


Résultats :

ERP      : 825 lignes
Liaison  : 825 lignes
Web      : 1513 lignes


Un problème de typage PyArrow a été rencontré avec la colonne sku / id_web, car certaines valeurs numériques et textuelles étaient mélangées. Le problème a été corrigé.

Le warning openpyxl :

Unknown extension is not supported and will be removed


n'empêche pas le traitement. Il est lié aux extensions Excel non prises en charge par la version utilisée.

Nettoyage

Un seul fichier nécessite réellement le nettoyage : Web.

La liaison ne nécessite pas de nettoyage et doit rester à :

825 lignes


Le fichier :

web_clean.parquet


contient :

1428 lignes

Dédoublonnage

Le fichier Web contenait des doublons, notamment des lignes de type attachment.

Après dédoublonnage :

web_deduplicated.parquet


contient :

714 lignes


Les contrôles ont également confirmé l'absence de doublons SKU après dédoublonnage.

Fusion

La liaison permet de faire correspondre les produits ERP et Web.

Le fichier fusionné contient :

714 lignes


Contrôle effectué :

product_id    id_web
3847          15298
3849          15296
3850          15300
...


Les doublons de product_id après fusion ont été contrôlés et aucun doublon n'a été détecté.

Calcul du chiffre d'affaires

Le chiffre d'affaires obtenu est :

70 568,60 €


Il correspond exactement à la valeur de référence d'Octave.

Contrôles qualité

Plusieurs contrôles ont été réalisés :

prix négatifs : 0

quantités vendues négatives : 0

stocks négatifs : 1

Le stock négatif identifié est :

product_id : 5700
sku        : 14736
stock      : -1


Ce cas a été identifié et contrôlé.

Les tests locaux ont finalement donné :

5 passed


Puis un contrôle supplémentaire a été ajouté pour les vins premium.

Z-score

Le calcul du z-score est réalisé en Python, conformément à la consigne.

Script :

scripts/z_score.py


Le script produit :

outputs/vins_premium.csv
outputs/vins_non_premium.csv


Résultat :

Vins premium détectés : 30


La valeur correspond exactement à la référence d'Octave.

3. Tests

Les tests ont été conservés avec quelques contrôles supplémentaires.

Les valeurs contrôlées sont notamment :

ERP                  825
Liaison              825
Web clean           1428
Web dédoublonné      714
Fusion               714
CA              70568,60 €
Vins premium          30


Il a été décidé de conserver les tests supplémentaires même si la consigne demande 5 tests.

Les tests seront placés après les tâches nominales dans Kestra.

4. Organisation SQL

Le script :

scripts/execute_sql.py


orchestre actuellement les quatre fichiers SQL dans cet ordre :

sql/clean.sql
sql/deduplicate.sql
sql/merge.sql
sql/sales.sql


Exécution locale validée :

Script SQL exécuté : sql/clean.sql
Script SQL exécuté : sql/deduplicate.sql
Script SQL exécuté : sql/merge.sql
Script SQL exécuté : sql/sales.sql


L'organisation est donc :

convert_to_parquet
        ↓
execute_sql
        ↓
z_score
        ↓
tests

5. Docker

Un Dockerfile a été créé avec Python 3.12 et les dépendances :

pandas
pyarrow
openpyxl
duckdb
pytest


L'image a été construite avec succès.

Le conteneur fonctionne également en local.

Test réalisé :

docker run ...


Résultat :

clean.sql          ✓
deduplicate.sql    ✓
merge.sql          ✓
sales.sql          ✓


Les dossiers du projet sont séparés :

data/
work/
outputs/


Le code est dans l'image Docker tandis que les données et résultats restent à l'extérieur.

6. Docker Compose / Kestra

Kestra fonctionne déjà avec Docker Compose.

Le compose contient notamment :

postgres
kestra


et Kestra dispose de l'accès au Docker socket :

/var/run/docker.sock:/var/run/docker.sock


Un montage du projet a été ajouté au conteneur Kestra :

./:/app/project


Cependant, ce montage n'est pas automatiquement transmis aux conteneurs créés par le Docker Task Runner de Kestra.

7. Dernier problème rencontré

Le premier test du flow Kestra a échoué avec :

cd: can't cd to /app/project


Cause :

Le conteneur créé pour la tâche Kestra ne voit pas le volume /app/project qui existe dans le conteneur Kestra.

Ce n'est donc pas un problème avec Python, le code ou l'image Docker.

Le warning :

Could not infer Python version from container image
Using fallback version '3.13'


n'est pas la cause de l'échec. Il faudra simplement préciser :

pythonVersion: "3.12"


dans la tâche.

8. Ce qu'il reste à faire
Priorité 1 — Corriger les volumes Kestra

Faire en sorte que les conteneurs des tâches Kestra puissent accéder à :

data/
work/
outputs/


C'est le point exact où nous nous sommes arrêtés.

La commande préparée pour demain est :

docker inspect kestra --format '{{json .Mounts}}'


Elle permettra de déterminer le chemin utilisable par les conteneurs lancés par Kestra.

Priorité 2 — Tester convert_to_parquet dans Kestra

Une fois le volume corrigé :

convert_to_parquet


doit produire :

work/parquet/erp.parquet
work/parquet/liaison.parquet
work/parquet/web.parquet

Priorité 3 — Ajouter execute_sql

Ensuite :

execute_sql


doit exécuter :

clean.sql
deduplicate.sql
merge.sql
sales.sql

Priorité 4 — Ajouter z_score

Puis :

z_score


doit produire :

outputs/vins_premium.csv
outputs/vins_non_premium.csv


avec :

30 vins premium

Priorité 5 — Générer le rapport CA Excel

Le pipeline doit produire le rapport :

.xlsx


correspondant au chiffre d'affaires.

Cette partie reste à finaliser.

Priorité 6 — Ajouter les tests dans Kestra

Les tests doivent être exécutés après les tâches nominales.

Architecture finale :

convert_to_parquet
        ↓
execute_sql
        ↓
z_score
        ↓
rapport / exports
        ↓
tests

Priorité 7 — Trigger cron

Configurer Kestra pour exécuter le pipeline :

le 15 de chaque mois à 9h

Priorité 8 — Livrables finaux

Il restera à vérifier :

note de cadrage

backlog OpenProject daté

Kanban à jour

logigramme complet

captures Kestra

README

GitHub

commits réguliers

lien du dépôt

support de présentation

démonstration de 3 minutes

9. État global

Le cœur du traitement est maintenant fonctionnel et validé en local.

Les résultats métier correspondent aux références :

825 → ERP
825 → Liaison
1428 → Web nettoyé
714 → Web dédoublonné
714 → Fusion
70 568,60 € → CA
30 → vins premium


Le prochain travail n'est donc plus de corriger le traitement métier : il s'agit principalement de faire fonctionner correctement ce pipeline dans Kestra et de terminer les livrables.

Point de reprise demain

Commencer par :

docker inspect kestra --format '{{json .Mounts}}'


Puis corriger le partage des volumes entre Kestra et les conteneurs des tâches.