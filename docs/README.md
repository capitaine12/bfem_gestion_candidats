## Bibliothèques Utilisées

- `PyQt5 V5.15.11` : Pour l'interface graphique.
- `Matplotlib V3.10.0` : Pour la visualisation des données .
- `Pandas V2.2.3` : Pour manipuler des dataframes utilisées ici pour uploader les   donnée de la fichier excel vers la BDD.
- `reportlab V4.3.1` : Pour générer des documents PDF.

## EXTENTION    
- `SQLite` A telecharger sur vs-code qui vous permeteras de mieux visualisé les fichier BDD.db dans votre editeur

- `SQLlite Viewer`  A telecharger sur vs-code qui vous permetera de lancer des requettes SQL vous pouvez un fichier -- SQLite.sql dans le dossier --> data/-- SQLite.sql

## SUPPORT DE TESTE SUR LES FORMULAIRES AJOUTER/MODIFIER CANDIDAT


``✅ Test des champs vides``

Laisse certains champs vides et clique sur "Enregistrer".
Attendu : Un message d’erreur doit s’afficher : "Tous les champs doivent être remplis."

``✅ Test du numéro de table``

Entre un numéro de table invalide (ex: "ABC" ou "12.5").
Attendu : Un message d’erreur doit s’afficher : "Le numéro de table doit être un nombre entier."

``✅ Test du prénom et du nom``

Saisis des chiffres ou caractères spéciaux dans Prénom/Nom (ex: "Jean123", "@Ali").
Attendu : Un message d’erreur doit s’afficher : "Le prénom/le nom ne doit contenir que des lettres, espaces ou tirets."

``✅ Test du lieu de naissance``

Entre un lieu de naissance invalide (ex: "Dakar123").
Attendu : Un message d’erreur doit s’afficher : "Le lieu de naissance ne doit contenir que des lettres."

``✅ Test de la nationalité``

Entre une nationalité incorrecte (ex: "SENEGAL" au lieu de "SEN").
Attendu : Un message d’erreur doit s’afficher : "La nationalité doit être un code de 3 lettres (ex: SEN, FRA, USA)."

``✅ Test de la date de naissance``

Entre une date invalide (ex: "32-13-2025" ou "2005/12/31").
Attendu : Un message d’erreur doit s’afficher : "La date de naissance doit être au format YYYY-MM-DD."

``✅ Test d'une date de naissance future``

Entre une date après aujourd’hui (ex: "2030-01-01").
Attendu : Un message d’erreur doit s’afficher : "La date de naissance ne peut pas être dans le futur."

``✅ Test d’un âge hors limite (moins de 13 ans ou plus de 30 ans)``

Entre une date de naissance qui donne un âge incorrect (ex: "2018-05-10" ou "1985-10-15").
Attendu : Un message d’erreur doit s’afficher : "L'âge du candidat doit être compris entre 10 et 30 ans."

``✅ Test d’un numéro de table déjà existant``

Ajoute un candidat avec un num_table qui existe déjà.
Attendu : Un message d’erreur doit s’afficher : "Le candidat N° X existe déjà."