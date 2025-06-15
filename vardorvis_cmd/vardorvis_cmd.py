#!/usr/bin/env python3
"""
Vardorvis Command Line Interface. Some custom logging additions to the cmd2 library.
"""

# pylint: disable=unused-argument

import datetime
import pathlib

from cmd2 import Cmd
from termcolor import colored

VARDORVIS_ASCII_ART = '''
                                        .g88888888888888888p.
                                      .d8888P""       ""Y8888b.
                                      "Y8P"               "Y8P'
                                         `.               ,'
                                           \\     .-.     /
                                            \\   (___)   /
 .------------------._______________________:__________j
/                   |                      |           |`-.,_
\\###################|######################|###########|,-'`
 `------------------'                       :    ___   l
                                            /   (   )   \\
                                           /     `-'     \\
                                         ,'               `.
                                      .d8b.               .d8b.
                                      "Y8888p..       ,.d8888P"
                                        "Y88888888888888888P"
                                           ""YY8888888PP"'''


class VardorvisCmd(Cmd):
    """
    Vardorvis Command Line Interface
    """

    def __init__(self, log_filename: pathlib.Path = pathlib.Path("vardorvis.log")):
        super().__init__()
        self.intro = colored(VARDORVIS_ASCII_ART, "red", attrs=["bold"])
        self.prompt = colored("vardorvis> ", "red", attrs=["bold"])
        self.logging_file = log_filename
        with open(self.logging_file, "w", encoding="utf-8") as f:
            f.close()

    def voutput(self, message: str):
        """
        Print output to console and log to file
        """
        vout = f"{colored("[+]", "green", attrs=["bold"])} {message}"
        self.poutput(vout)
        with open(self.logging_file, "a", encoding="utf-8") as f:
            f.write(f"{vout}\n")

    def async_voutput(self, message: str):
        """
        Print async output to console and log to file
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vout = f"{colored(f"[{timestamp}] [+]", "green", attrs=["bold"])} {message}"
        self.async_alert(vout)
        with open(self.logging_file, "a", encoding="utf-8") as f:
            f.write(f"{vout}\n")

    def vfeedback(self, message: str):
        """
        Print feedback to console and log to file
        """
        vout = f"{colored("[!]", "yellow", attrs=["bold"])} {message}"
        self.pfeedback(vout)
        with open(self.logging_file, "a", encoding="utf-8") as f:
            f.write(f"{vout}\n")

    def async_vfeedback(self, message: str):
        """
        Print async feedback to console and log to file
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vout = f"{colored(f"[{timestamp}] [!]", "yellow", attrs=["bold"])} {message}"
        self.async_alert(vout)
        with open(self.logging_file, "a", encoding="utf-8") as f:
            f.write(f"{vout}\n")

    def verror(self, message: str):
        """
        Print error to console and log to file
        """
        vout = f"{colored("[-]", "red", attrs=["bold"])} {message}"
        self.perror(vout)
        with open(self.logging_file, "a", encoding="utf-8") as f:
            f.write(f"{vout}\n")

    def async_verror(self, message: str):
        """
        Print async error to console and log to file
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vout = f"{colored(f"[{timestamp}] [-]", "red", attrs=["bold"])} {message}"
        self.async_alert(vout)
        with open(self.logging_file, "a", encoding="utf-8") as f:
            f.write(f"{vout}\n")

    def precmd(self, statement):
        """
        Hook called before a command is executed. We can update to alter the command
        before it is executed. This logs the executed command to a file.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        command_line = statement.raw

        with open(self.logging_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] Executed: {command_line}\n")

        return statement

    def do_test(self, args):
        """
        Test the Vardorvis command line interface
        """
        self.voutput("This is a test output")
        self.vfeedback("This is a test feedback")
        self.verror("This is a test error")

    def do_exit(self, args):
        """
        Exit the Vardorvis command line interface
        """
        self.vfeedback("Exiting Vardorvis CLI")
        return True


def main():
    """
    Main function to run the Vardorvis command line interface
    """
    vardorvis_cmd = VardorvisCmd()
    vardorvis_cmd.cmdloop()


if __name__ == "__main__":
    main()


# End of file
