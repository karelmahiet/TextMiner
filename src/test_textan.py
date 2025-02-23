#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Programme python pour l'évaluation du code de détection des auteurs et de génération de textes

    Copyright 2018-2025 F. Mailhot et Université de Sherbrooke
"""
import copy
import importlib
import os.path
import sys
from typing import Any
from datetime import date, datetime
from tabulate import tabulate

from test_textan_parsing import ParsingClassTextAn
from test_textan_command import *
from text_beautifier import TextBeautifier
from print_util import PrintUtil


class TestTextAn(ParsingClassTextAn):
    """Classe à utiliser pour valider la résolution de la problématique :
        - Contient tout le nécessaire pour tester la problématique.

    Pour valider la solution de la problématique, effectuer :
        - python test_textan.py -help (Indique tous les arguments et options disponibles)
        - Vous pouvez aussi modifier le fichier test_textan_config.yml

    Copyright 2018-2025, F. Mailhot et Université de Sherbrooke
    """

    @staticmethod
    def add_cwd_to_sys_path() -> None:
        """Ajoute le répertoire d'exécution local aux chemins utilisés par le système.
           Sinon, si test_textan.py est un lien symbolique, les fichiers textan_CIP1_CIP2.py ne sont pas trouvés

        Args :
            (void) : Utilisation des informations système

        Returns :
            (void) : Au retour, le répertoire d'exécution est ajouté au chemin système
        """
        sys.path.append(os.getcwd())
        return

    @staticmethod
    def sort_author_distance(author_res: [str, float]) -> float:
        """Retourne le deuxième élément du vecteur (auteur, proximité) (utilisé pour le tri de la liste des auteurs)

        Args :
            ([str, float]) : Liste des auteurs et valeur de proximité avec le texte inconnu
            (résultat du produit scalaire) pour chacun des auteurs

        Returns :
            (float) : Valeur de la proximité de l'auteur avec le texte inconnu
        """
        return author_res[1]

    # Si mode verbose, refléter les valeurs des paramètres passés sur la ligne de commande
    def print_params(self) -> None:
        """Mode verbose, imprime l'ensemble des paramètres utilisés pour ce test :
            - Valeur des paramètres par défaut s'ils n'ont pas été modifiés sur la ligne de commande
            - Ensemble des tests demandés

        Returns :
            (void) : Ne fait qu'imprimer les valeurs contenues dans self
        """
        if not self.args.v:
            return

        PrintUtil.log_print("\tMode verbose: ", self.cip)

        if self.args.f and self.args.f != 'None':
            PrintUtil.log_print("\tFichier inconnu à étudier: " + self.args.f)
            if self.oeuvre:
                PrintUtil.log_print(f"\tChemin complet de l'oeuvre inconnue: {self.oeuvre}")
        if self.args.F:
            PrintUtil.log_print("\tListe des fichiers inconnus à étudier: " + self.args.F)
            PrintUtil.log_print("\tFichiers inconnus:")
            for oeuvre in self.oeuvre:
                PrintUtil.log_print("\t\t" + oeuvre)

        PrintUtil.log_print("\tCalcul avec des " + str(self.args.m) + "-grammes")

        if self.args.K:
            if self.args.K == 1:
                PrintUtil.log_print("\tLe premier ngramme le plus fréquent sera trouvé")
            else:
                PrintUtil.log_print(
                    "\tLe "
                    + str(self.args.K)
                    + "e ngramme le plus fréquent sera trouvé"
                )

        if self.args.g and self.args.g != 'None':
            PrintUtil.log_print("\tCréation d'un fichier aléatoire")
        if self.args.G and self.args.G != 'None':
            PrintUtil.log_print("\tCréation de multiples fichiers aléatoires")
        if self.args.G_fusion and self.args.G_fusion != 'None':
            PrintUtil.log_print("\tCréation d'un fichier aléatoire avec auteurs multiples")
        if ((self.args.g and self.args.g != 'None')
                or (self.args.G and self.args.G != 'None')
                or (self.args.G_fusion and self.args.G_fusion != 'None')):
            PrintUtil.log_print("\tNom du fichier aléatoire: " + self.args.g_name)

        if self.args.noPonc:
            PrintUtil.log_print("\tRetrait des signes de ponctuation")
        else:
            PrintUtil.log_print("\tConservation des signes de ponctuation")

        if self.args.G and self.args.G != 'None':
            self.auteurs.sort()
            PrintUtil.log_print(
                "\tGénération d'un texte de "
                + str(self.args.G)
                + " mots, pour les auteurs: ",
                self.auteurs
            )
            auteurs_string = str(self.auteurs)
            PrintUtil.log_print("\tLe nom du fichier généré sera: " + self.get_gen_file_name(auteurs_string))

        if self.args.recursion:
            PrintUtil.log_print("\tRécursion maximale: ", sys.getrecursionlimit())

        PrintUtil.log_print("\tTemps d'exécution maximal: ", self.timeout, " secondes")

        PrintUtil.log_print("\tCalcul avec les auteurs du répertoire: " + self.args.d)
        PrintUtil.log_print("\tListe des auteurs:")
        self.auteurs.sort()
        for a in self.auteurs:
            aut = a.split("/")
            PrintUtil.log_print("\t\t" + aut[-1])

        if self.args.compare_auteurs:
            PrintUtil.log_print("\tLa proximité des textes de l'ensemble des auteurs sera calculée")

        return

    def setup_instance_param(self) -> None:
        """Définit les paramètres de l'instance (étudiante) à tester

        Returns :
            (void) : Rien n'est retourné
        """
        # Ajout de l'information nécessaire dans l'instance à tester de la classe TextAn sous étude
        self.textan.set_ngram_size(self.ngram_size)
        self.textan.set_aut_dir(self.dir)
        self.auteurs = self.textan.auteurs
        self.print_params()  # Imprime l'état de l'instance (si le mode verbose a été utilisé sur la ligne de commande)
        return

    def get_gen_file_name(self, auteur) -> str:
        """Définit le nom du fichier à générer

        Args :
            auteur (str) : Nom de l'auteur à utiliser dans le nom du fichier
        Returns :
            name (str) : Nom du fichier à générer
        """
        name = self.cip + auteur + ".txt"
        if self.g_name and self.g_name != "":
            use_cip = self.g_name.find("<CIP>")
            use_auteur = self.g_name.find("<AUT>")
            use_date = self.g_name.find("<DATE>")
            use_hour = self.g_name.find("<HR>")
            use_minute = self.g_name.find("<MIN>")
            use_second = self.g_name.find("<SEC>")
            name = self.g_name
            if use_cip:
                name = name.replace("<CIP>", self.cip)
            if use_auteur:
                name = name.replace("<AUT>", auteur)
            if use_date:
                name = name.replace("<DATE>", str(date.today()))
            if use_hour:
                name = name.replace("<HR>", str(datetime.today().hour))
            if use_minute:
                name = name.replace("<MIN>", str(datetime.today().minute))
            if use_second:
                name = name.replace("<SEC>", str(datetime.today().second))
            return name
        return name

    def get_cips(self) -> None:
        """Lit le fichier etudiants.txt, trouve les CIPs, et retourne la liste
           Le CIP est obtenu du fichier etudiants.txt, dans le répertoire courant
            ou tel qu'indiqué en paramètre (option -dir_code)

        Returns :
            (void) : Au retour, tous les cips sont inclus dans la liste self.cips
        """
        cip_file = self.dir_code + "/" + self.etudiants
        cip_list = open(cip_file, "r")
        lines = cip_list.readlines()
        for line in lines:
            if "#" in line:
                continue
            if "%" in line:
                continue
            for student_cip in line.split():
                self.cips.append(student_cip)

        return

    def import_textan_cip(self, import_cip: str) -> None:
        """Importe le fichier textan_CIP1_CIP2.py, où "CIP1_CIP2" est passé dans le paramètre import_cip

        Args :
            import_cip (str) : Contient "CIP1_CIP2", les cips pour le code à tester

        Returns :
            (void) : Au retour, le module textan_CIP1_CIP2 est importé et remplace le précédent
        """

        if "init_module" in self.init_modules:
            # Deuxième appel (ou subséquents) : enlever tous les modules supplémentaires
            for m in sys.modules.keys():
                if m not in self.init_modules:
                    del sys.modules[m]
        else:
            # Premier appel : identifier tous les modules déjà présents
            self.init_modules = sys.modules.keys()

        self.cip = import_cip
        textan_name = "textan_" + import_cip

        self.textan_module = importlib.import_module(textan_name)

        return

    def check_and_setup_golden(self) -> None:
        """Vérifie si une version "golden" doit être conservée

        Args :
            (void) : Le nom de la version "golden" est disponible dans le champ self.args

        Returns :
            (void) : Au retour, le champ golden_module est initialisé (si nécessaire)
        """
        if self.args.golden and self.args.golden != 'None':
            self.golden_module = importlib.import_module(self.args.golden)
        else:
            self.golden_module: Any = None
        return

    def check_something_to_do(self) -> None:
        """Vérifie que les paramètres d'entrée indiquent quelque chose à faire

        Args :
            (void) : Toute l'information nécessaire est présente dans l'objet

        Returns :
            (void) : Au retour, le champ something_to_do indique le statut.  S'il n'y a rien à faire, sortie
        """

        something_to_do = (
                self.do_gen_text
                | self.do_find_author
                | self.do_get_kth_ngram
                | self.do_print_auteur_distance
        )

        if not something_to_do:
            PrintUtil.log_print("Aucune action à effectuer. Utiliser un paramètre pour:")
            PrintUtil.log_print("\t - Générer un texte aléatoire (-a Auteur -g) ou (-G)")
            PrintUtil.log_print("\t - Trouver l'auteur d'un texte inconnu (-f texte_inconnu.txt)")
            PrintUtil.log_print("\t - Trouver le k-ième n-gramme le plus fréquent d'un auteur (-F k)")
            PrintUtil.log_print("")
            self.parser.print_help()
            exit()
        return

    def load_cip_code(self, student_cip: str) -> None:
        """Charge le code étudiant en mémoire, initialise l'instance, initialise le débogage

        Args : student_cip (str) : Cips de l'ensemble des membres de l'équipe d'APP
        Returns : (void) : Rien n'est retourné : au retour, le code étudiant a été chargé en mémoire
        """
        self.import_textan_cip(
            student_cip
        )  # Chargement du code des étudiants identifiés par cip
        self.textan = self.textan_module.TextAn()
        self.setup_instance_param()
        self.debug_handler.start_execution_timing()  # Permet de mesurer le temps d'exécution du code étudiant
        self.debug_handler.set_student_cip(
            student_cip
        )  # Indique le cip courant au gestionnaire de débogage
        return

    def analyze(self) -> None:
        """Effectue l'analyse des textes fournis (calcul des fréquences pour chacun des auteurs) avec le code étudiant
                - Appelle la méthode d'analyse des textes self.textan.analyze() fournie par les étudiants
                - Normalise les vecteurs de chacun des auteurs

        Returns :
            (void) : Rien n'est retourné : au retour, les textes des auteurs ont été analysés
        """
        self.textan.analyze()
        self.textan.normalize_ngrams_auteurs()
        return

    def join_dicts(self, normalized_auteurs_ngrams) -> dict:
        """Crée un dictionnaire qui combine les statistiques de tous les auteurs
        Args : normalized_auteurs_ngrams ([dict]) : tableau de dictionnaires des auteurs (normalisés)
        Returns : res_dict (dict) : Dictionnaire normalisé de la somme des dictionnaires des auteurs
        """
        res_dict = {}
        for auteur in normalized_auteurs_ngrams:
            dict_auteur = normalized_auteurs_ngrams[auteur]
            self.textan.normalize_vector(dict_auteur)
            res_dict = self.textan.add_dict(res_dict, dict_auteur)
        self.textan.normalize_vector(res_dict)
        return res_dict

    def gen_from_dict(self, auteur: str, gen_dict: dict) -> None:
        """Prépare la génération d'un texte aléatoire et appelle la génération fournie par les étudiants:
            - Prépare le nom du fichier à créer
            - Ouvre le fichier en écriture
            - Appelle la méthode de création de texte aléatoire
            - Ferme le fichier créé

        Args :
            auteur (str) : nom de l'auteur (ou des auteurs) ciblé
            gen_dict (dict) : dictionnaire de n-grammes utilisé pour la génération
        Returns :
            (void) : Rien n'est retourné, le fichier aléatoire est créé dans le système de fichiers
        """
        filename = self.get_gen_file_name(auteur)
        filepath = os.path.join(self.g_dir, filename)
        to_file = open(filepath, 'w')

        PrintUtil.log_print(f'\t\t--> {self.gen_size} mots, style:  {auteur}, nom du fichier: {filename}')
        self.textan.gen_text_dict(gen_dict, self.gen_size, to_file)
        to_file.close()

        if self.beautify:
            self.text_beautifier.prettify_file(filepath)
        return

    def generate(self) -> None:
        """Effectue la génération d'un texte aléatoire suivant les statistiques d'un certain auteur (code étudiant)

        Returns :
            (void) : Rien n'est retourné : au retour, un texte aléatoire a été généré, basé sur les statistiques
                        d'un seul auteur, ou de l'ensemble des auteurs
        """
        PrintUtil.log_print("")
        PrintUtil.log_print("\tcip: ",
                            self.cip,
                            "- Création de texte aléatoire:")
        if self.args.g and self.args.g != 'None':
            auteur = self.args.g
            gen_dict = self.textan.ngrams_auteurs[auteur]
            self.gen_from_dict(auteur, gen_dict)
        elif self.args.G_fusion and self.args.G_fusion != 'None':
            gen_dict = self.join_dicts(self.textan.normalized_ngrams_auteurs)
            auteurs = "".join(f"_{k}_" for k in self.auteurs)
            self.gen_from_dict(auteurs, gen_dict)
        else:
            for auteur in self.auteurs:
                auteur_dict = self.textan.ngrams_auteurs[auteur]
                self.gen_from_dict(auteur, auteur_dict)
        return

    def find(self) -> None:
        """Calcule la proximité d'un certain nombre de textes inconnus avec le "style"
            de chacun des auteurs avec le code étudiant

        Returns :
            (void) : Rien n'est retourné : au retour, les textes inconnus ont été comparés aux textes des auteurs
        """
        if self.do_find_author:
            for oeuvre in self.oeuvre:
                PrintUtil.log_print(
                    f'\tcip: {self.cip} - Calcul des fréquences pour l\'oeuvre "{os.path.basename(oeuvre)}": ')

                self.analysis_result = self.textan.find_author(oeuvre)
                self.analysis_result.sort(key=self.sort_author_distance, reverse=True)

                PrintUtil.log_print("\t\t--> ", end="")
                # https://stackoverflow.com/questions/493386/how-to-print-without-a-newline-or-space
                for item in self.analysis_result:
                    PrintUtil.log_print(f"{item[0]}:{item[1]:.4f} ", end="")
                PrintUtil.log_print("")

        return

    def get_kth_ngram(self) -> None:
        """Obtient le k-ième plus fréquent n-gramme d'un certain auteur avec le code étudiant

        Returns :
            (void) : Rien n'est retourné : au retour, le k-ième n-gramme le plus fréquent a été imprimé
        """
        if self.do_get_kth_ngram:
            if len(self.auteurs) == 0:
                PrintUtil.log_print(
                    "\tPas d'auteur: impossible de donner le k-ième n-gramme")
                return
            for auteur in self.auteurs:
                PrintUtil.log_print(f"\tcip: {self.cip} - Calcul du {self.kth_ngram}e{"r"[:self.kth_ngram == 1]} \\"
                                    f"n-gramme le plus fréquent", end="")
                PrintUtil.log_print(f" de l'auteur: {auteur}:")

                kth_ngram = self.textan.get_kth_element(auteur, self.kth_ngram)

                if not kth_ngram:
                    PrintUtil.log_print(f"\tPas de {self.kth_ngram}e{"r"[:self.kth_ngram == 1]} n-gramme")
                else:
                    total_frequency = self.textan.get_total_occurrences(auteur)
                    frequency = 100 * self.textan.get_ngram_occurrence(auteur, kth_ngram[0]) / total_frequency
                    mantissa, exponent_base10 = self.textan.convert_to_sci_base_10(frequency)

                    PrintUtil.log_print("\t\t--> "
                                        f'{self.kth_ngram}e{"r"[:self.kth_ngram == 1]}'
                                        f' n-gramme de {self.ngram_size} mot{"s"[:self.ngram_size > 1]}: {kth_ngram}'
                                        f' (Fréquence: {mantissa:3.2f} X 10^{exponent_base10} %)')

            return

    def compare_auteurs(self) -> []:
        """Calcule la proximité entre chacun des auteurs (nombre entre 0 et 1) :
            - Effectue le produit scalaire normalisé entre les vecteurs des auteurs

        Returns :
            [] : Retourne un tableau prêt pour l'impression, avec les noms d'auteurs et les valeurs de comparaison
        """
        res_table = []
        auteur_list = []
        closest = [0.0, ("", "")]
        farthest = [1.0, ("", "")]
        res_table.append(auteur_list)  # La première ligne du tableau de résultats contiendra la liste des auteurs
        auteur_list.append("")
        res_buffer = {}  # Tampon pour conserver les valeurs de proximité d'auteurs déjà calculées

        for auteur1 in self.auteurs:
            auteur_res = []
            res_table.append(auteur_res)
            auteur_list.append(auteur1)
            auteur_res.append(auteur1)
            for auteur2 in self.auteurs:
                auteurs_key = tuple(sorted((auteur1, auteur2)))  # Conserver la valeur pour éviter de refaire le calcul
                if auteurs_key in res_buffer:
                    distance = res_buffer[auteurs_key]
                else:
                    dict1 = self.textan.normalized_ngrams_auteurs[auteur1]
                    dict2 = self.textan.normalized_ngrams_auteurs[auteur2]
                    distance = self.textan.dot_product_dict(dict1, dict2)

                    res_buffer[auteurs_key] = distance
                    if distance < farthest[0]:
                        farthest[0] = distance
                        farthest[1] = auteurs_key
                    if (distance > closest[0]) and auteur1 != auteur2:
                        closest[0] = distance
                        closest[1] = auteurs_key
                auteur_res.append(distance)

        return res_table, closest, farthest

    def print_auteur_distance(self) -> None:
        """Calcule et imprime la proximité entre chacun des auteurs (nombre entre 0 et 1)

        Returns :
            void : Rien n'est retourné : au retour, la distance entre les différents auteurs a été imprimée
        """
        if not self.do_print_auteur_distance:  # Par défaut ce calcul n'est pas fait.  Utiliser --compare_auteurs
            return

        PrintUtil.log_print("\tcip:", self.cip, "- Comparaison des auteurs:")

        res_table, closest, farthest = self.compare_auteurs()

        # https://learnpython.com/blog/print-table-in-python/
        res_string = tabulate(res_table, headers="firstrow", tablefmt="fancy_grid")
        res_string = "\t" + res_string
        new_string = '\n\t'.join(res_string.splitlines())  # Add tab at beginning of table (shift table right)
        PrintUtil.log_print(new_string)
        PrintUtil.log_print(f"\tAuteurs les plus proches ({closest[0]:4.3f}): {closest[1][0]}, {closest[1][1]}")
        PrintUtil.log_print(f"\tAuteurs les plus lointains ({farthest[0]:4.3f}): {farthest[1][0]}, {farthest[1][1]}")
        return

    def register_operations(self):
        """Enregistre l'ensemble des méthodes à exécuter pour vérifier le code.
            Les différentes méthodes doivent être enregistrées dans l'ordre dans lequel leur exécution doit s'effectuer

        Args :
            void : L'enregistrement se fait avec les méthodes définies dans l'objet

        Returns :
            void : Rien n'est retourné : au retour, toutes les méthodes ont été enregistrées
        """
        exec_pre_print_banner = ">>>------------>>> " + ExecOperation.REPLACE_CIP + " <<<----------------<<<\n"
        exec_pre_print_banner += "\tTentative de chargement du code textan_" + ExecOperation.REPLACE_CIP + ".py"
        self.command.register_one_operation(True,
                                            exec_pre_print_banner,
                                            self.load_cip_code,
                                            "Load cip code: TestTextAn.load_cip_code()",
                                            True,
                                            "\tChargement réussi")
        # Analyse des textes des auteurs (code étudiant)
        self.command.register_one_operation(True,
                                            "\n\tAppel de la méthode Textan.analyze(): "
                                            "Extraction des n-grammes",
                                            self.analyze,
                                            "Analyze n-grams: TestTextan.analyze()",
                                            False,
                                            "\tAnalyse terminée")

        # Produit un texte aléatoire avec les statistiques de l'auteur choisi
        self.command.register_one_operation(self.do_gen_text,
                                            "\n\tAppel de la méthode Textan.generate(): "
                                            "Génération d'un texte aléatoire",
                                            self.generate,
                                            "Generate text: TestTextan.generate",
                                            False,
                                            "\tGénération de texte terminée")

        # Calcul de proximité entre un texte inconnu et l'ensemble des auteurs (code étudiant),
        self.command.register_one_operation(self.do_find_author,
                                            "\n\tAppel de la méthode Textan.find(): "
                                            "Détection de l'auteur inconnu",
                                            self.find,
                                            "Find auteurs: TestTextan.find()",
                                            False,
                                            "\tFin du calcul de détection d'auteur inconnu")

        # Trouve le k-ième n-gramme le plus fréquent d'un certain auteur (code étudiant)
        self.command.register_one_operation(self.do_get_kth_ngram,
                                            "\n\tAppel de la méthode Textan.get_kth_ngram(): "
                                            "Détection du k-ième n-gramme le plus fréquent",
                                            self.get_kth_ngram,
                                            "Get k-th n-gram: TestTextan.get_kth_ngram()",
                                            False,
                                            "\tFin du calcul du k-ième ngramme le plus fréquent")

        # Calcule la distance entre les auteurs
        self.command.register_one_operation(self.do_print_auteur_distance,
                                            "\n\tAppel de la méthode Textan.print_auteur_distance(): "
                                            "Calcule le cosinus de l'angle entre les vecteurs des auteurs",
                                            self.print_auteur_distance,
                                            "Print auteur distance: TestTextan.print_auteur_distance()",
                                            False,
                                            "\tFin du calcul de proximité entre les auteurs")
        return

    def __init__(self) -> None:
        """Constructeur pour la classe TestTextAn.  Initialisation de l'ensemble des éléments requis :

            - Au besoin, création d'une instance "golden" de TextAn, pour la vérification et la correction
            - Lecture des cips des équipes d'étudiants
            - Mise en mémoire du répertoire de démarrage
            - Validation qu'au moins l'un de :
                - la ligne de commande
                - le fichier de configuration
                - indique une action à effectuer
                    - (génération de texte, découverte d'auteur, calcul du k-ième n-gramme, proximité d'auteurs)
            - Création d'une instance de CommandTextan, pour enregistrer puis exécuter une série de méthodes
            - Utilise le patron de conception (design pattern) "command"
                - Enregistre la séquence d'opérations à exécuter avec le code TextAn :
                    - Charge le code fourni par l'équipe
                    - Invoque la méthode d'analyse de texte de l'équipe
                    - Ensuite, au besoin :
                        - Invoque la méthode de génération de texte aléatoire
                        - Calcule la proximité d'un texte inconnu avec les textes des auteurs fournis
                        - Trouve le k-ième ngramme le plus fréquent pour un certain auteur
                        - Trouve la distance entre les oeuvres des différents auteurs
            - Création d'une instance de TextBeautifier, qui permet d'améliorer le format des textes générés

        Args :
            (void) : Le constructeur lit la ligne de commande et ajuste l'état de l'objet TestTextAn en conséquence

        Returns :
            (void) : Au retour, la nouvelle instance de test est prête à être utilisée
        """

        super().__init__()

        self.check_and_setup_golden()
        self.get_cips()
        self.add_cwd_to_sys_path()
        self.check_something_to_do()

        self.command = CommandTextan()
        self.register_operations()

        self.text_beautifier = TextBeautifier()

        return


def main() -> None:
    """Démarrage de l'exécution du code de la problématique, pour l'ensemble des équipes :
        - Initialiser une instance de test
        - Pour chaque équipe (séquence de cips) :
            - Faire une copie fraiche de l'instance de test
            - Exécuter la série de commandes préparées à l'aide du patron de conception "command" :
                - Préparation effectuée dans le constructeur TestTextAn
        - Si l'ensemble du code est trop long à s'exécuter (par défaut, 2 minutes), interrompre l'exécution
        - Attraper toutes les exceptions non-traitées dans le code étudiant

    Args :
        (void) : Tout ce qui est nécessaire est défini à l'intérieur de la méthode

    Returns :
        (void) : Au retour, l'exécution est terminée
    """
    golden_tta = TestTextAn()  # Initialisation de l'instance de test

    golden_tta.stdout = None
    for cip in golden_tta.cips:  # Permet de tester le code d'une ou plusieurs équipes, à tour de rôle
        tta = copy.deepcopy(
            golden_tta
        )  # Copie fraiche de l'objet, pour isoler les instances des étudiants

        try:
            tta.command.exec_operations(cip)

        # Si le code étudiant est trop lent (120 secondes par défaut), interrompre
        except debug_handler_common.DebugHandlerTimeOutException:
            tta.debug_handler.print_timeout_exception()

        # Mauvaise pratique (attraper toutes les exceptions), mais nécessaire ici, pour du code étudiant inconnu
        except Exception:
            tta.debug_handler.print_general_exception()

        total_run_time = tta.debug_handler.stop_execution_timing()  # Mesure le temps d'exécution du code étudiant
        PrintUtil.log_print(f"\tcip: {cip} - Temps d'exécution total: {total_run_time:.2f} secondes\n")

    # si stdout a été redirigé vers un fichier ; le fermer pour ne rien perdre
    if golden_tta.args.fichier_res and golden_tta.args.fichier_res != 'None':
        PrintUtil.close_stdout()
    return


if __name__ == "__main__":
    main()
