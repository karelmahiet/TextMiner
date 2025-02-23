#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Code utilitaire pour gérer l'impression

    Copyright 2025 F. Mailhot et Université de Sherbrooke
"""
import io
import sys
import os


class PrintUtil:
    """Classe permettant la gestion de l'impression :

        - Permet de définir où se fera l'impression des messages de test (écran ou fichier de log)
        - Permet de désactiver les impressions effectuées dans le code étudiant
        - Cette classe est utilisée directement, sans instance, en utilisant uniquement :
            - des attributs de classe
            - des méthodes de classe
        - Les attributs de classe utilisés sont:
            - class_stdout : sys.stdout par défaut, peut être redéfini, utilisé par log_print()
            - sys_stdout : copie de sys.stdout, ne peut être modifié, conserve le "vrai" sys.stdout
                - utilisé pour revenir à sys.stdout après blocage des print()

    Copyright 2025, F. Mailhot et Université de Sherbrooke
    """
    # Voir: https://www.toptal.com/python/python-class-attributes-an-overly-thorough-guide
    class_stdout = sys.stdout
    sys_stdout = sys.stdout
    new_sys_stdout = None

    @classmethod
    def set_stdout(cls, log_stdout: io.TextIOWrapper) -> None:
        """Redéfinit stdout pour l'impression effectuée par la classe (méthode log_print) :
            - Permet d'identifier où se fera l'impression (écran ou fichier de log)

        Args :
            log_stdout (io.TextIOWrapper) : Le nouveau fichier de log

        Returns :
            (void) : Au retour, stdout est redéfini pour la méthode log_print

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """
        cls.class_stdout = log_stdout
        return

    @classmethod
    def get_stdout(cls):
        """Retourne le stdout utilisé pour l'impression avec la méthode log_print :

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """
        return cls.class_stdout

    @classmethod
    def close_stdout(cls):
        """Ferme le fichier associé au stdout utilisé par la méthode log_print :
            - Appelé à la fin, pour fermer correctement le fichier de log
            - Si le "fichier" de log est l'écran (sys.stdout), ne fait rien

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """
        if cls.class_stdout != cls.sys_stdout:
            PrintUtil.class_stdout.close()
        return

    @classmethod
    def get_sys_stdout(cls):
        """Retourne la version originale de sys.stdout :

       Returns :
            (void) : Au retour, sys.stdout original est retourné

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """
        return cls.sys_stdout

    @classmethod
    def block_stdout(cls):
        """Redéfinit stdout pour l'impression dans le code étudiant (print standards) :
            - Remplace stdout par /dev/null (impression inactive)

        Returns :
            (void) : Au retour, sys.stdout est redéfini vers os.devnull

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """
        f = open(os.devnull, "w")
        PrintUtil.new_sys_stdout = f
        sys.stdout = f
        return

    @classmethod
    def unblock_stdout(cls):
        """Remet la valeur par défaut de sys.stdout :
            - Permet d'imprimer de nouveau normalement avec print()
            - N'est utilisé que si block_stdout a été utilisé auparavant

        Returns :
            (void) : Au retour, sys.stdout original est revenu

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """
        if PrintUtil.new_sys_stdout and PrintUtil.new_sys_stdout != PrintUtil.sys_stdout:
            PrintUtil.new_sys_stdout.close()
            sys.stdout = cls.get_sys_stdout()
            PrintUtil.new_sys_stdout = None
        return

    @classmethod
    def log_print(cls, *args, **kwargs):
        """Imprime dans le fichier de log :

        Args :
            args :      Paramètres habituels de print()
            kwargs :    Paramètres habituels de print()

        Returns :
            (void) : Au retour, l'impression a eu lieu dans le fichier de log

        Copyright 2025, F. Mailhot et Université de Sherbrooke
        """
        print(*args, **kwargs, file=cls.class_stdout)
        return
