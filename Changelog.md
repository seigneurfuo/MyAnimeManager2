# 5 juillet 2018
 - Ajout d'un attribut "langue" pour une saison
 - Correction d'un bug lors de la création d'un nouveau profil: Les paramètre étaients chargés avant que la GUI ne soit initialisée

# 19 mai 2018
 - Déplacement du code SQL dans le fichier "queries"

# 4 mai 2018
 - La configuration de MyAnimeManager est désormais stockée dans le dossier de l'utilisateur dans le dossier .myanimemanager2

# 29 avril 2018
 - Création d'une classe personalisée pour le calendrier: Possibilité d'utiliser une méthode afin de changer l'arrière plan sur certains jours voulus
 - Le calendrier dans l'onglet planning affiche maintenant un fond de couleur sur les jours ou un épisode minimum à été regardé.

# 28 février 2018
 - Correction d'un bug qui n'affichait pas le nombre de saisons pour une série
 - Modification de l'ordre de tri: Si plusieurs séries ont le meme identifiant, le tri se fait alphabétiquement entre elles.

# 13 Février 2018
 - Correction des icones disparus dans la liste d'état d'une saison

# 19 Janvier 2018
 - Suppression d'une commande d'ouverture d'explorateur de fichier
 - Exportation de la fonction d'ouverture d'explorateur de fihier dans le module "utils"
 - Correction de bug: Utilisation d'un nouveau système afin de localiser les ressources "compagnons" peut importe depuis quel endroit on lance l'application
 - Désactivation des boutons de parcours des dossiers si les dossiers ne sont pas accesibles (ex: un dossier distant)

# 20 Décembre 2017
 - Correction de bug d'ouverture de dossier si aucun chemin n'est défini
 - Correction de bug: Zone de scroll non adaptive dans les notes de saisons
 - Correction de bug: L'identifiant de saison n'est pas rechargé lors d'une modification de l'édition d'une série

# 5 décembre 2017
 - L'application est maintenant 100% adaptive
 - Migration des lignes sql vers ./ressources/tables.py

# 19 novembre 2017
 - Ajout d'une option afin d'afficher les saison taggées comme "à voir"

# 16 novembre 2017
 - Résolution de bug qui n'affichait pas les séries dans l'odre des numéros

# 15 novembre 2017
 - Mise en place progressive de fenetre adaptives

﻿# 5 novembre 2017
 - Lors d'une suppression d'une serie / saison, la suppresion enlève également les informations dans le planning (permet de ne pa garder des vieilles informations dans la base de données)
 - Correction de bug: erreur sous windows si un dossier n'existait pas

# 4 novembre 2017
 - Ajout du champ d'entrée des notes dans un scroll area dans la fenetre SeasonModal.

# 1er novembre 2017
 - Migration des dernière lignes utilisant l'ancienne syntaxe sqlite
 - Ajout des notes de saisons dans un objet scroll area pour permettre de taper du texte sir plusieurs lignes.

# 27 octobre 2017
 - Correction de bugs: Si aucun épisode à voir/vu n'est sélectionné, on ne rajoute rien
 - Découpage des classes des fenêtres dans des fichiers distincts
 - Utilisation d'une nouvelle syntaxe sqlite afin d'autoriser les caractères (' ou ") dans les chaînes de texte

# 21 octobre 2017
 - Ajout d'une barre de recherche pour accéder rapidement à une série.
 - Ajout d'un bouton pour vider la barre de recherche.
 - Correction du bug suivant: Les informations de la saison ne sont pas effacées lorsque qu'on passe à une série sans aucune saison.
 - Affichage du nombre d'épisodes vus sur par date dans l'onglet Planning.
 - Correction de bugs mineurs dans sur l'interface.
 - Correction du bug suivant: dans l'onglet planning "ouvrir le dossier" alors qu’aucun épisode n'est sélectionner ouvre tout de même le dossier du dernier élément dans la liste. 
 - Ajout d'une boite de texte pour remplir le chemin de la série. Il est donc possible d'utiliser l'explorateur ou bien de coller le chemin de la série.

# 15 octobre 2017
 - Modification de la disposition de l'onglet Planning.
 - Correction de bug: Le bouton "aujourd’hui" dans l'onglet planning n'avait aucun effet au clic.

# 11 octobre 2017
 - Ajout de notes pour chaque saisons.
 - Modification de la taille des colonnes par défaut.

# 9 octobre 2017
 - Inversion des lignes "Chemin de la série" et "Image de couverture" dans la fenêtre "SerieModal".
 - Ajout d'un bouton sur la planning afin d'ouvrir le dossier de l'animé sélectionné.

# 8 octobre 2017
 - Remise en forme des tableaux dans l'onglet planning.

# 1 octobre 2017
 - Les dossiers de profil sont crées automatiquement si il n'existent pas déjà.
 - Le fichier de paramètres est également crée avec les valeurs par défaut si il n'existe pas déjà.

# 28 septembre 2017
 - Création d'une fonction qui créer une base SQL ainsi que les tables correspondantes.
 - Ajout de messages dans la barre de statut.

# 27 septembre 2017
 - Ajout d'un champ pour le nombre de visionnages d'une série
 - Quand une saison est terminée, le nombre de visionnages s'incrémente de 1

# 19 septembre 2017
 - Correction de bug: Lors de la création d'une saison, celle ci s'enregistrait systématiquement avec le statut "a voir".

# 12 septembre 2017 - 2017.09.12
 - Il est désormais possible de choisir la page de démarrage + fichier de configuration et interface.
 - Correction et documentation de fonctions diverses.
 - Ajout d'un onglet de prise de notes.

# 7 septembre 2017 - 2017.09.07
 - Correction et vérification des entrées contenant des numéros.
 - Possibilité de cocher les séries appréciées.

# 5 septembre 2017 - 2017.09.05
 - Ajout d'une fonction pour ouvrir le dossier la série directement sur la fiche de celle-ci.
 - Un clic sur la ligne dans l'onglet planning permet de d'effectuer l'ajout ou la suppression d'un épisode sans avoir à cliquer sur le bouton.

# 4 septembre 2017 - version 0.6.2-bêta
 - Possibilité de supprimer un épisode vu dans le planning.
 - Correction des valeurs des spin-box d’identifiant à 1 par défaut.
 - Désactivation de l'édition des éléments dans un tableau lors d'un double clic.

# 3 septembre 2017 - version 0.6.1-bêta
 - Correction des valeurs maximales dans les spin-box des informations de séries / saisons (IdMax: 5000, nombre épisode max: 1000).
 - Correction de bug: affichage d'une icône stock en cas de cover introuvable pour la série sélectionnée.
 - Correction de bug: quelques informations ne s’effacent pas de l'affichage: Oubli de nettoyage.

# 31 août 2017 - version 0.6-bêta
 - Création d'un fichier changelog pour montrer l'avancée de l'application, même si le début du développement date d'il y à déjà plus d'un mois.
 - Lorsqu'une saison est terminée, elle passe son état en "vue" et le nombre d'épisodes vus reviennent à 0.

# 10 juillet 2017
 - Reprogrammation de l'application depuis 0. L'occasion de passer sous Python 3 ainsi qu'avec PyQt en version 5.
 - Cette version apportera la gestion des saisons, qui m'avait été impossible de déployer dans l'ancienne version.
