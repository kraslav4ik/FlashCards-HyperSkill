import logging
import os
import random
import json
import sys
import argparse
from collections import defaultdict


def init_logger(logger_name) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    while logger.hasHandlers():
        logger.removeHandler(logger.handlers[0])

    fle_handler = logging.FileHandler('logs', mode='w')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    fle_format = logging.Formatter('%(message)s')
    fle_handler.setFormatter(fle_format)
    handler.setFormatter(fle_format)

    logger.addHandler(fle_handler)
    logger.addHandler(handler)
    return logger


class KeyTermExistErr(Exception):
    def __init__(self):
        self.message = 'This term already exists. Try again:'
        super().__init__(self.message)


class ValueTermExistErr(Exception):
    def __init__(self):
        self.message = 'This definition already exists. Try again:'
        super().__init__(self.message)


class IncorrectInputValErr(Exception):
    def __init__(self):
        self.message = 'Incorrect action. Try again:'
        super().__init__(self.message)


class FlashCard:
    def __init__(self):
        self.card_list = {}
        self.mistakes = defaultdict(int)
        self.actions = {'add', 'remove', 'import', 'export', 'ask', 'exit', 'log', 'hardest card', 'reset stats'}
        self.logger = init_logger(self.__class__.__name__)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("--import_from")
        self.parser.add_argument("--export_to")
        self.args = self.parser.parse_args()

    def log_input(self, *args, **kwargs):
        x = input(*args, **kwargs)
        self.logger.debug(x)
        return x

    def add(self) -> None:
        term = self.log_input()
        while term in self.card_list.keys():
            self.logger.info(KeyTermExistErr())
            term = self.log_input()
        definition = self.log_input()
        while definition in self.card_list.values():
            self.logger.info(ValueTermExistErr())
            definition = self.log_input()
        self.card_list[term] = definition
        self.logger.info(f'The pair ("{term}":"{definition}") has been added')
        return

    def remove(self) -> None:
        self.logger.info('Which card?')
        card = self.log_input()
        try:
            del self.card_list[card]
            self.logger.info('The card has been removed.')
        except KeyError:
            self.logger.info(f"Can't remove \"{card}\": there is no such card.")
        return

    def import_cards(self, file_name=None) -> None:
        if not file_name:
            self.logger.info('File name:')
            file_name = self.log_input()
        if file_name in os.listdir(os.getcwd()):
            with open(f"{os.getcwd()}\\{file_name}") as fle:
                self.card_list = json.load(fle)
            self.logger.info(f"{len(self.card_list)} cards have been loaded.")
            return
        self.logger.info("File not found.")
        return

    def export_cards(self, file_name=None) -> None:
        if not file_name:
            self.logger.info('File name:')
            file_name = self.log_input()
        with open(f"{os.getcwd()}\\{file_name}", 'a') as fle:
            json.dump(self.card_list, fle)
        self.logger.info(f"{len(self.card_list)} cards have been saved")
        return

    def ask(self) -> None:
        self.logger.info("How many times to ask?")
        n = int(self.log_input())
        for i in range(n):
            key = random.choice(list(self.card_list.keys()))
            self.logger.info(f'print the definition of "{key}":')
            answer = self.log_input()
            if answer == self.card_list[key]:
                self.logger.info("Correct!")
                continue
            for k, v in self.card_list.items():
                if answer == v:
                    self.logger.info(f'Wrong. The right answer is "{self.card_list[key]}", but your definition is correct for "{k}".')
                    break
            else:
                self.logger.info(f'Wrong. The right answer is "{self.card_list[key]}".')
            self.mistakes[key] += 1
        return

    def log_in_file(self):
        self.logger.info('File name:')
        file_name = self.log_input()
        log_file = open('logs')
        with open(file_name, 'w') as fle:
            for line in log_file:
                fle.write(line)
        log_file.close()
        self.logger.info('The log has been saved.')
        return

    def hardest_card(self) -> None:
        if not self.mistakes:
            self.logger.info('There are no cards with errors.')
            return
        max_errors = max(self.mistakes.values())
        print_list = [term for term in self.mistakes if self.mistakes[term] == max_errors]
        if len(print_list) == 1:
            self.logger.info(f'The hardest card is {print_list[0]}. You have {max_errors} errors answering it')
            return
        self.logger.info(f'The hardest cards are {", ".join(print_list)}')
        return

    def reset(self) -> None:
        self.mistakes.clear()
        self.logger.info('Card statistics have been reset.')
        return

    def menu(self) -> None:
        if self.args.import_from is not None:
            self.import_cards(self.args.import_from)
        while True:
            self.logger.info("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):")
            action = self.log_input()
            try:
                if action not in self.actions:
                    raise IncorrectInputValErr()
                if action == 'add':
                    self.add()
                    continue
                if action == 'remove':
                    self.remove()
                    continue
                if action == 'import':
                    self.import_cards()
                    continue
                if action == 'export':
                    self.export_cards()
                    continue
                if action == 'ask':
                    self.ask()
                    continue
                if action == 'log':
                    self.log_in_file()
                    continue
                if action == 'hardest card':
                    self.hardest_card()
                    continue
                if action == 'reset stats':
                    self.reset()
                    continue
                if action == 'exit':
                    if self.args.export_to is not None:
                        self.export_cards(self.args.export_to)
                    self.logger.info("Bye bye!")
                    break
            except IncorrectInputValErr as err:
                self.logger.info(err)
                continue
        return


if __name__ == '__main__':
    flash_card = FlashCard()
    flash_card.menu()
