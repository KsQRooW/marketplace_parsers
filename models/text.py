from string import punctuation
from pymorphy3 import MorphAnalyzer


class Text:
    def __init__(self, word: str | set = ''):
        self.__word = word
        self.analyzer = MorphAnalyzer()

    @property
    def word(self):
        return self.__word

    @word.setter
    def word(self, word: str | set):
        if not isinstance(word, (set, str)):
            raise TypeError(f"Передан класс {type(word)}. Ожидался класс str или set.")
        self.__word = word

    @staticmethod
    def punct_remover(word: str, set_punctuation: set) -> str:
        """
        Удаление пунктуации/служебных символов из слова

        :param word: слово, из которого будет удалена пунктуация
        :param set_punctuation: множество всех символов, которые используются при пунктуации
        :return: очищенное слово от пунктуации
        """
        intersection = set_punctuation.intersection(word)
        for symbol in intersection:
            word = word.replace(symbol, '')
        return word

    def remove_punctuation(self) -> str | set:
        """
        Удаление пунктуации из слова self.word для случая:
            - если self.word - set
            - если self.word - str
        :return: очищенный от пунктуации self.word
        """
        set_punctuation = set(punctuation)
        if isinstance(self.word, str):
            result = self.punct_remover(self.word, set_punctuation)
            self.word = result
        elif isinstance(self.word, set):
            result = set()
            for one_word in self.word:
                result.add(self.punct_remover(one_word, set_punctuation))
            self.word = result
        return self.word

    def normal_form(self) -> str | set:
        """
        Приведение слова к нормальной форме (лемматизация) слова (или множества слов) из self.word
        :return: возвращает слово (или множество слов) в нормальной форме
        """
        if isinstance(self.word, str):
            try:
                self.word = self.analyzer.normal_forms(self.word)[0]
            except Exception:
                self.word = ''
        elif isinstance(self.word, set):
            result = set()
            for one_word in self.word:
                result.add(self.analyzer.normal_forms(one_word)[0])
            self.word = result
        return self.word

    def word_cleaning(self, word: str) -> str:
        """
        Очищает слово от пунктуации и приводит к нормальной форме.
        :param word: Слово
        :return: Очищенное от пунктуации слово и приведенное к нормальной форме
        """
        self.word = word
        self.remove_punctuation()
        self.normal_form()
        return self.word

    def str_to_clean_set(self, text: str) -> set:
        """
        Превращает str в set из лемматизированных и очищенных от пунктуации слов
        :param text: Текст
        :return: Множество лемматизированных и очищенных от пунктуации слов
        """
        result = set()
        for word in text.split():
            clean_word = self.word_cleaning(word)
            result.add(clean_word)
        return result

    def is_one_word_in_set(self, text: str, set_: set) -> bool:
        """
        Присутствует ли хотя бы одно слово из text в set_?
        :param text: Текст
        :param set_: Множество слов, в котором ищем слово из text
        :return: True или False (True - присутствует)
        """
        check = False
        for word in text.split():
            clean_word = self.word_cleaning(word)
            if clean_word in set_:
                check = True
                break
        return check

    def text_accuracy(self, text_1: str | set, text_2: str | set) -> float:
        """
        Проверяет сколько слов из text_1 встречается в text_2. Возвращается коэффициент в диапазоне от 0 до 1,
        где:
            0 - ни одного слова из text_1 не нашлось в text_2
            1 - все слова из text_1 нашлись в text_2
        :param text_1: Текст, слова из которого ищем в text_2
        :param text_2: Текст, в котором осуществляется поиск слов из text_1
        :return: Коэффициент в диапазоне от 0 до 1
        """
        if not isinstance(text_1, (str, set)):
            raise TypeError(f"Передан класс {type(text_1)}. Ожидался класс str или set.")
        if not isinstance(text_2, (str, set)):
            raise TypeError(f"Передан класс {type(text_2)}. Ожидался класс str или set.")

        if isinstance(text_1, str):
            text_1 = self.str_to_clean_set(text_1)
        if isinstance(text_2, str):
            text_2 = self.str_to_clean_set(text_2)

        return len(text_1 & text_2) / len(text_1) if text_1 else 0
