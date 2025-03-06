#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Ce fichier contient la classe TextAn, à utiliser pour résoudre la problématique.
    C'est un gabarit pour l'application de traitement des fréquences de mots dans les oeuvres d'auteurs divers.

    Les méthodes apparaissant dans ce fichier définissent une API qui est utilisée par l'application
    de test test_textan.py
    Les paramètres d'entrée et de sortie (Application Programming Interface, API) sont définis,
    mais le code est à écrire au complet.
    Vous pouvez ajouter toutes les méthodes et toutes les variables nécessaires au bon fonctionnement du système

    La classe TextAn est invoquée par la classe TestTextAn (contenue dans test_textan.py) :

        - Tous les arguments requis sont présents et accessibles dans args (dans le fichier test_textan.py)
        - Les arguments proviennent :
            - soit du fichier de configuration test_textan_config.yml,
            - soit de la ligne de commande
        - Note : vous pouvez tester votre code en utilisant les commandes :
            + "python test_textan.py"
            + "python test_textan.py -h" (donne la liste des arguments possibles)
            + "python test_textan.py -v" (mode "verbose", qui indique les valeurs de tous les arguments)
        - Note (2) : vous pouvez modifier le fichier test_textan_config.yml :
            - Vous le trouverez dans le répertoire de travail (Problematique/data)
            - Les mêmes options existent dans le fichier test_textan_config.yml et en ligne de commande
            - Les paramètres passés en ligne de commande ont priorité sur ceux définis dans le fichier de configuration

    Copyright 2018-2025, F. Mailhot et Université de Sherbrooke
"""
import io
import math  # Au besoin, retirer le commentaire de cette ligne
import random # Au besoin, retirer le commentaire de cette ligne
from textan_common import TextAnCommon


class TextAn(TextAnCommon):
    """Classe à utiliser pour coder la solution à la problématique :

        - La classe héritée TextAnCommon contient certaines fonctions de base pour faciliter le travail :
            - recherche des auteurs
            - ouverture des répertoires
            - obtention de la liste des oeuvres d'un auteur (get_aut_files(auteur))
            - et autres (voir la classe TextAnCommon pour plus d'information)
        - Les interfaces du code à développer sont présentes, mais tout le code est à écrire
        - En particulier, il faut compléter les fonctions suivantes :
            - add_dict(dict1, dict2)
            - analyze()
            - dot_product_dict (dict1, dict2)
            - find_author (oeuvre)
            - gen_text_dict(auteur_dict, taille, to_file)
            - get_kth_element (auteur, k)
            - get_ngram_occurrence (auteur, ngram)
            - get_total_occurrences (auteur)
            - get_vector_size(dict)
            - normalize_vector(dict)


    Copyright 2018-2025, F. Mailhot et Université de Sherbrooke
    """

    # Signes de ponctuation à traiter comme des mots (compléter cette liste incomplète)
    PONC = ["!", ";","?",":","."]

    # Ajouter les structures de données et les fonctions nécessaires à l'analyse des textes,
    # la production de textes aléatoires, la détection d'oeuvres inconnues,
    # l'identification des k-ièmes mots les plus fréquents.
    #
    # Les méthodes qui suivent doivent toutes être complétées pour que le système soit opérationnel
    # et que le harnais de test (test_textan.py) puisse exécuter tous les tests requis.
    #
    #  Note : Voir
    #

    @staticmethod
    def get_vector_size(dict_de_ngrams: dict) -> float:
        """Calcule la longueur (norme) du vecteur (dictionnaire) de ngrams contenus dans un dictionnaire

        Args :
            dict_de_ngrams (dict) : le vecteur de ngrams (dict) en question

        Returns :
            taille (float) : La norme du vecteur (dict) est retournée

        Copyright 2024-2025, F. Mailhot et Université de Sherbrooke
        """
        return math.sqrt(sum(value ** 2 for value in dict_de_ngrams.values()))

    def normalize_vector(self, dict_de_ngrams: dict) -> dict:
        """Normalize le vecteur (dictionnaire), en divisant chaque occurrence par la taille totale

        Args :
            dict_de_ngrams (dict) : le vecteur de n-grammes (dict) en question

        Returns :
            (dict) : Une nouvelle version normalisée du dictionnaire est retournée

        Copyright 2024-2025, F. Mailhot et Université de Sherbrooke
        """
        #calcule norme
        norm = math.sqrt(sum(value ** 2 for value in dict_de_ngrams.values()))

        #nouveau dict normalise
        norm_dict = {}
        for k, v in dict_de_ngrams.items():
            if norm !=0:
                norm_dict[k] = v / norm
            else:
                norm_dict[k] = 0.0 #si norme=0, normale=0

        return norm_dict

    @staticmethod
    def add_dict(dict1: dict, dict2: dict) -> dict:
        """Additionne deux vecteurs représentés par des dictionnaires
        Note : le vecteur de retour n'est PAS NORMALISÉ

        Args :
            dict1 (dict) : le premier vecteur
            dict2 (dict) : le deuxième vecteur

        Returns :
            sum_dict (dict) : La somme des deux vecteurs passés en paramètre

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """

        sum_dict = {}
        for k in dict1:
            sum_dict[k] = dict1[k] + dict2[k]
        return sum_dict

    @staticmethod
    def dot_product_dict(dict1: dict, dict2: dict) -> float:
        """Calcule le produit scalaire de deux vecteurs représentés par des dictionnaires
            Note : ce produit scalaire n'est PAS normalisé

        Args :
            dict1 (dict) : le premier vecteur
            dict2 (dict) : le deuxième vecteur

        Returns :
            dot_product (float) : Le produit scalaire normalisé de deux vecteurs

        Copyright 2024-2025, F. Mailhot et Université de Sherbrooke
        """

        dot_product = 0.0  # Initialisation à 0.0, car nous allons additionner les produits
        for key, value in dict1.items():
            if key in dict2:  # Assurez-vous que la clé est présente dans dict2
                dot_product += value * dict2[key]
        return dot_product

    def find_author(self, oeuvre: str) -> []:
        """Après analyse des textes d'auteurs connus, retourner la liste d'auteurs
            et le niveau de proximité (un nombre entre 0 et 1) de l'oeuvre inconnue
            avec les écrits de chacun d'entre eux

        Args :
            oeuvre (str) : Nom du fichier contenant l'oeuvre d'un auteur inconnu

        Returns :
            resultats (Liste[(string, float)]) : Liste de tuples (auteurs, niveau de proximité),
            où la proximité est un nombre entre 0 et 1)
        """
        mots = open(oeuvre,"r", encoding="utf-8").read().split()
        ngram_frequencies = {}

        for i in range(len(mots) - self.ngram_size + 1):
            ngram = " ".join(mots[i:i + self.ngram_size])
            ngram_frequencies[ngram] = ngram_frequencies.get(ngram, 0) + 1

        #normaliser vecteur
        oeuvre_normalisee = self.normalize_vector(ngram_frequencies)

        #liste de score de similarite
        resultats = []

        #comparer avec auteur connu
        for auteur, ngrams_auteur in self.ngrams_auteurs.items():
            #norme
            auteur_normalise = self.normalize_vector(ngrams_auteur)

            #produit scalaire
            dot_product = self.dot_product_dict(oeuvre_normalisee, auteur_normalise)

            #norme des deux
            norme_oeuvre = math.sqrt(sum(value ** 2 for value in oeuvre_normalisee.values()))
            norme_auteur = math.sqrt(sum(value ** 2 for value in auteur_normalise.values()))

            #similarite
            if norme_oeuvre == 0 or norme_auteur == 0:
                similarite = 0
            else:
                similarite = dot_product / norme_oeuvre * norme_auteur

            #add result a la liste
            resultats.append((auteur, similarite))

        return resultats

    def get_ngram_occurrence(self, auteur: str, ngram: str) -> int:
        """Retourne le nombre d'occurrences du n-gramme pour cet auteur

        Args :
            auteur (string) : le nom de l'auteur
            ngram (objet de type ngram) : le n-gramme dont on désire la fréquence

        Returns :
            int : retourne le nombre d'occurrences du n-gramme pour l'auteur donné

        Copyright 2024-2025, F. Mailhot et Université de Sherbrooke
        """
        tmp_str = ""
        for string in ngram:
                tmp_str = " ".join(string)

        occurences = 0
        for k in self.ngrams_auteurs[auteur]:
            if tmp_str.__contains__(k):
                occurences += 1
        return occurences

    def get_total_occurrences(self, auteur: str) -> int:
        """Retourne le nombre total d'occurrences de n-grammes pour cet auteur
            - Représente le total de n-grammes pour l'ensemble des oeuvres de cet auteur
            - Ce nombre est différent de la norme du vecteur :
                - il s'agit seulement du total d'occurrences de l'ensemble des ngrammes
                - Le calcul doit donner la somme des valeurs, et non la racine carrée de la somme des carrés des valeurs

        Args :
            auteur (string) : le nom de l'auteur

        Returns :
            int : retourne le nombre total d'occurrences pour l'auteur donné

        Copyright 2024-2025, F. Mailhot et Université de Sherbrooke
        """
        occurences = 0
        if auteur in self.ngrams_auteurs:
            for ngram, count in self.ngrams_auteurs[auteur].items():
                occurences += count
        return occurences

    def gen_text_dict(self, auteur_dict: dict, taille: int, to_file: io.TextIOWrapper) -> None:
        """Après analyse des textes d'auteurs connus, produire un texte selon des statistiques d'un dictionnaire

        Args :
            auteur_dict (dict) : Dictionnaire à utiliser (soit d'un auteur, ou d'un amalgame)
            taille (int) : Taille du texte à générer
            to_file (io.TextIOWrapper) : Pointeur vers le fichier à créer.

        Returns :
            void : ne retourne rien, le texte produit doit être écrit dans le fichier fourni
        """
        # #dict en liste ngram
        # ngrams = list(auteur_dict.keys())
        # frequencies = list(auteur_dict.values())
        #
        # #norm freq pour prob
        # total_frequencies = sum(frequencies)
        # probabilites = [freq / total_frequencies for freq in frequencies]
        #
        # #generer le texte
        # generated_text = []
        # current_ngram = random.choices(ngrams, weights=probabilites, k=1)[0]
        # generated_text.extend(current_ngram.split())
        #
        # while len(generated_text) < taille:
        #     prefix = " ".join(generated_text[- (self.ngram_size - 1):])
        #     possible_ngrams = [ngram for ngram in ngrams if ngram.startswith(prefix)]
        #
        #     if not possible_ngrams:
        #         #si rien correspond, aleatoire
        #         current_ngram = random.choices(ngrams, weights=probabilites, k=1)[0]
        #     else:
        #         possible_frequencies = [auteur_dict[ngram] for ngram in possible_ngrams]
        #         current_ngram = random.choices(possible_ngrams, weights=possible_frequencies, k=1)[0]
        #
        #     #add dernier mot du ngram
        #     generated_text.append(current_ngram.split()[-1])
        #
        # #write dans fichier
        # to_file.write("\n".join(generated_text[:taille]))

        """Génère un texte aléatoire basé sur les statistiques d'un dictionnaire de n-grammes."""
        # Convertir le dictionnaire en liste de n-grammes et de fréquences
        ngrams = list(auteur_dict.keys())
        frequencies = list(auteur_dict.values())

        # Vérifier que les listes ne sont pas vides et ont la même longueur
        if not ngrams or not frequencies or len(ngrams) != len(frequencies):
            print("Les listes de n-grammes et de fréquences doivent être non vides et de même longueur.")

        # Normaliser les fréquences pour en faire des probabilités
        total_frequencies = sum(frequencies)
        if total_frequencies <= 0:
            print("La somme des fréquences doit être supérieure à zéro.")
        probabilites = [freq / total_frequencies for freq in frequencies]

        # Créer un dictionnaire inversé pour les préfixes
        prefix_dict = {}
        for ngram in ngrams:
            prefix = " ".join(ngram.split()[:-1])
            if prefix not in prefix_dict:
                prefix_dict[prefix] = []
            prefix_dict[prefix].append(ngram)

        # Générer le texte
        generated_text = []

        current_ngram = random.choices(ngrams, weights=probabilites, k=1)[0]
        generated_text.extend(current_ngram.split())


        while len(generated_text) < taille:
            prefix = " ".join(generated_text[-(self.ngram_size - 1):])
            possible_ngrams = prefix_dict.get(prefix, [])

            if not possible_ngrams:
                # Si aucun n-gramme ne correspond, choisir un n-gramme aléatoire

                current_ngram = random.choices(ngrams, weights=probabilites, k=1)[0]

            else:
                possible_frequencies = [auteur_dict[ngram] for ngram in possible_ngrams]

                current_ngram = random.choices(possible_ngrams, weights=possible_frequencies, k=1)[0]


            # Ajouter le dernier mot du n-gramme choisi au texte généré
            generated_text.append(current_ngram.split()[-1])

        tempstring = " ".join(generated_text[:taille]).encode("utf-8")

        to_file.write(tempstring.__str__())



    def get_kth_element(self, auteur: str, k: int) -> [[str]]:
        """Après analyse des textes d'auteurs connus, retourner la liste des k-ièmes plus fréquents
         n-grammes de l'auteur indiqué
         Note : il peut y avoir plus d'un n-gramme avec le même nombre d'occurrences.

        Args :
            auteur (str) : Nom de l'auteur à utiliser
            k (int) : Indice du n-gramme à retourner

        Returns :
            ngram (List[Liste[string]]) : Liste de listes de mots composant le n-gramme recherché
            (il est possible qu'il y ait plus d'un n-gramme au même rang)
        """
        #check si auteur existe
        if auteur not in self.ngrams_auteurs:
            return []

        #recupere dict ngram auteur
        ngram_dict = self.ngrams_auteurs[auteur]

        #trier par freq decroissante
        sorted_ngrams = sorted(ngram_dict.items(), key=lambda x: x[1], reverse=True)

        #trier au k ieme rang
        if k < 1 or k > len(sorted_ngrams):
            return []

        #get freq du k ieme ngram
        kth_frequency = sorted_ngrams[k-1][1]
        normFreq = (kth_frequency / (sum(ngram_dict.values())))

        #find ngram meme freq
        kth_ngrams = [ngram for ngram, freq in sorted_ngrams if freq == kth_frequency]

        #convert ngram en liste mots
        result = [ngram.split() for ngram in kth_ngrams]

        return result, kth_frequency, normFreq

    def analyze(self) -> None:
        """Fait l'analyse des textes fournis, en traitant chaque oeuvre de chaque auteur

        Args :
            void : toute l'information est contenue dans l'objet TextAn

        Returns :
            void : ne retourne rien, toute l'information extraite est conservée dans des structures internes
        """

        for auteur in self.auteurs:
            oeuvres = self.get_aut_files(auteur)
            ngram_comptes = {}

            for oeuvre in oeuvres:
                try:
                    with open(oeuvre, "r", encoding="utf-8") as f:
                        texte = f.read().split()
                        for i in range(len(texte) - self.ngram_size + 1):
                            ngram = ' '.join(texte[i:i + self.ngram_size])
                            if ngram in ngram_comptes:
                                ngram_comptes[ngram] += 1
                            else:
                                ngram_comptes[ngram] = 1
                except FileNotFoundError:
                    print(f"Fichier non trouvé: {oeuvre}")

            self.ngrams_auteurs[auteur] = ngram_comptes
        return

    def __init__(self) -> None:
        """Initialize l'objet de type TextAn lorsqu'il est créé

        Args :
            (void) : Utilise simplement les informations fournies dans la classe TextAnCommon

        Returns :
            (void) : Ne fait qu'initialiser l'objet de type TextAn
        """

        # Initialisation des champs nécessaires aux fonctions fournies
        super().__init__()

        # Au besoin, ajouter votre code d'initialisation de l'objet de type TextAn lors de sa création

        self.set_ngram_size(1)

        return
