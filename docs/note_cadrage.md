## Besoin métier

Le Comptoir des Coteaux souhaite automatiser le traitement mensuel des ventes afin de remplacer le rapprochement manuel réalisé par Octave. Le pipeline doit réconcilier les données de l'ERP et de la boutique en ligne, calculer le chiffre d'affaires par produit et le chiffre d'affaires total, puis produire les listes de vins premium et ordinaires. Les résultats doivent être disponibles automatiquement le 15 de chaque mois à 9h.

## Périmètre technique

Le pipeline s'appuiera sur Kestra pour l'orchestration, DuckDB pour les traitements SQL et Python avec pandas pour le calcul statistique du z-score. Les trois sources sont `Fichier_erp.xlsx`, `fichier_liaison.xlsx` et `Fichier_web.xlsx`. Les traitements devront nettoyer et dédoublonner les sources avant leur rapprochement, puis produire un rapport Excel et deux fichiers CSV.

## Contraintes identifiées

L'ERP contient 825 produits avec des `product_id` uniques et aucune valeur manquante, mais présente notamment un prix minimum de -8 et un stock minimum de -1. La table de liaison contient 825 `product_id`, dont 91 `id_web` manquants. Le fichier web contient 1 513 lignes, dont 716 produits, avec 2 produits sans sku et un doublon sur `sku`. Les règles de nettoyage devront respecter les résultats de référence fournis par Octave.

## Questions en attente

Il faudra confirmer les règles précises de gestion des valeurs atypiques de l'ERP et le comportement attendu en cas d'échec d'une tâche ou d'indisponibilité d'un service. La conception devra également permettre d'intégrer ultérieurement une nouvelle source de données sans remettre en cause l'ensemble du pipeline.