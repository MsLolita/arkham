import random
from RandomWordGenerator import RandomWord

import names


class CustomFaker:
    def __init__(self):
        self.name, self.last_name = names.get_full_name().lower().split(" ")

        self.last_username = None

    def __get_name_username(self):
        username_list = [self.name, self.last_name]
        random.shuffle(username_list)

        return "_".join(username_list)

    def get_username(self):
        username_list = [self.name, self.last_name]
        random.shuffle(username_list)
        self.last_username = f"{random.choice(['_', ''])}".join(username_list) + CustomFaker.get_random_word(7)

        return self.last_username[:-random.randint(1, 3)][:random.randint(8, 15)]

    def get_password(self):
        return f"{random.choice([self.name, self.last_name])}{random.choice(['_', ''])}{CustomFaker.get_random_word(5, True)}"

    @staticmethod
    def get_random_word(max_word_size: int = 10, include_digits: bool = False):
        rw = RandomWord(max_word_size,
                        constant_word_size=True,
                        include_digits=include_digits,
                        special_chars=r"@_!#$%^&*()<>?/\|}{~:",
                        include_special_chars=False)

        return rw.generate()
