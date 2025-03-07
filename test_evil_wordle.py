"""Evil Wordle Test Suite"""

import unittest
import sys
from unittest.mock import patch
import io
import os
import difflib
import evil_wordle as evil_wordle
from evil_wordle import (
    Keyboard,
    WordFamily,
    CORRECT_COLOR,
    WRONG_SPOT_COLOR,
    NOT_IN_WORD_COLOR,
    NO_COLOR,
    color_word,
    fast_sort,
    get_feedback_colors,
    get_feedback,
)


class TestKeyboardUpdate(unittest.TestCase):
    """Keyboard Update Tests"""

    def check_keyboard_colors(self, keyboard, expected_colors):
        """Helper method to check the entire keyboard color state"""
        for letter, color in expected_colors.items():
            self.assertEqual(
                keyboard.colors[letter],
                color,
                f"Expected '{color_word(keyboard.colors[letter], letter)}' to be {color_word(color, letter)}",
            )

    def test_1(self):
        """update(): Single correct letter 'a' in word 'apple'"""
        keyboard = Keyboard()
        keyboard.update(
            [
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "apple",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "a": CORRECT_COLOR,
                "p": NOT_IN_WORD_COLOR,
                "l": NOT_IN_WORD_COLOR,
                "e": NOT_IN_WORD_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_2(self):
        """update(): Single wrong spot letter 'k' in word 'brick'"""
        keyboard = Keyboard()
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
            ],
            "brick",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "b": NOT_IN_WORD_COLOR,
                "r": NOT_IN_WORD_COLOR,
                "i": NOT_IN_WORD_COLOR,
                "c": NOT_IN_WORD_COLOR,
                "k": WRONG_SPOT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_3(self):
        """update(): WRONG_SPOT_COLOR 'a' maintained even in duplicate letters like 'adapt'"""
        keyboard = Keyboard()

        # First update with WRONG_SPOT_COLOR
        keyboard.update(
            [
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "adapt",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "a": WRONG_SPOT_COLOR,
                "d": NOT_IN_WORD_COLOR,
                "p": NOT_IN_WORD_COLOR,
                "t": NOT_IN_WORD_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

        # Second update with CORRECT_COLOR
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "track",
        )
        expected_colors.update(
            {
                "r": NOT_IN_WORD_COLOR,
                "c": NOT_IN_WORD_COLOR,
                "k": NOT_IN_WORD_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_4(self):
        """update(): Multiple guesses apply CORRECT_COLOR, WRONG_SPOT_COLOR, and NOT_IN_WORD_COLOR"""
        keyboard = Keyboard()

        # First update with 'crate'
        keyboard.update(
            [
                CORRECT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
            ],
            "crate",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "c": CORRECT_COLOR,
                "r": CORRECT_COLOR,
                "a": NOT_IN_WORD_COLOR,
                "t": NOT_IN_WORD_COLOR,
                "e": WRONG_SPOT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

        # Second update with 'clamp'
        keyboard.update(
            [
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "clamp",
        )
        expected_colors.update(
            {
                "l": NOT_IN_WORD_COLOR,
                "m": WRONG_SPOT_COLOR,
                "p": NOT_IN_WORD_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_5(self):
        """update(): Multiple guesses apply CORRECT_COLOR, WRONG_SPOT_COLOR, and NOT_IN_WORD_COLOR"""
        keyboard = Keyboard()

        # First update with 'stark'
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
            ],
            "stark",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "s": NOT_IN_WORD_COLOR,
                "t": NOT_IN_WORD_COLOR,
                "a": CORRECT_COLOR,
                "r": WRONG_SPOT_COLOR,
                "k": CORRECT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

        # Second update with 'track'
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
            ],
            "track",
        )
        expected_colors.update(
            {
                "r": CORRECT_COLOR,
                "c": WRONG_SPOT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_6(self):
        """update(): Entire row marked as WRONG_SPOT_COLOR across multiple guesses"""
        keyboard = Keyboard()

        # First update with 'liver'
        feedback_colors = [WRONG_SPOT_COLOR] * 5
        keyboard.update(feedback_colors, "asdfg")
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update({letter: WRONG_SPOT_COLOR for letter in "asdfg"})
        self.check_keyboard_colors(keyboard, expected_colors)

        # Second update with 'brave'
        keyboard.update(feedback_colors, "ghjkl")
        expected_colors.update({letter: WRONG_SPOT_COLOR for letter in "ghjkl"})
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_7(self):
        """update(): CORRECT_COLOR has priority over WRONG_SPOT_COLOR after multiple updates"""
        keyboard = Keyboard()

        # First update with WRONG_SPOT_COLOR
        keyboard.update(
            [
                CORRECT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            "bobby",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "b": CORRECT_COLOR,
                "o": CORRECT_COLOR,
                "y": CORRECT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

        # Second update with another WRONG_SPOT_COLOR
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            "cabby",
        )
        expected_colors.update(
            {
                "c": NOT_IN_WORD_COLOR,
                "a": NOT_IN_WORD_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_8(self):
        """update(): 's' updates to CORRECT_COLOR from 'basis' and 'swiss'"""
        keyboard = Keyboard()

        # First update with 'basis'
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
            ],
            "basis",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "b": NOT_IN_WORD_COLOR,
                "a": WRONG_SPOT_COLOR,
                "s": WRONG_SPOT_COLOR,
                "i": WRONG_SPOT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

        # Second update with 'swiss'
        keyboard.update(
            [
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            "swiss",
        )
        expected_colors.update(
            {
                "w": NOT_IN_WORD_COLOR,
                "s": CORRECT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_9(self):
        """update(): 'p' and 'i' update to CORRECT_COLOR from 'spike' and 'pipes'"""
        keyboard = Keyboard()

        # First update with 'spike'
        keyboard.update(
            [
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "spike",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "s": CORRECT_COLOR,
                "p": WRONG_SPOT_COLOR,
                "i": WRONG_SPOT_COLOR,
                "k": CORRECT_COLOR,
                "e": NOT_IN_WORD_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

        # Second update with 'pipes'
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
            ],
            "pipes",
        )
        expected_colors.update(
            {
                "p": CORRECT_COLOR,
                "i": CORRECT_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)

    def test_10(self):
        """update(): Same letter with different colors in same word; CORRECT_COLOR takes precedence"""
        keyboard = Keyboard()
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "teeth",
        )
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "teeth",
        )
        expected_colors = {letter: NO_COLOR for letter in "qwertyuiopasdfghjklzxcvbnm"}
        expected_colors.update(
            {
                "t": NOT_IN_WORD_COLOR,
                "e": CORRECT_COLOR,
                "h": NOT_IN_WORD_COLOR,
            }
        )
        self.check_keyboard_colors(keyboard, expected_colors)


class TestKeyboardStr(unittest.TestCase):
    """Keyboard String Representation Tests"""

    def test_1(self):
        """__str__(): Initial string representation with NO_COLOR for all keys"""
        keyboard = Keyboard()
        expected_output = (
            f"{color_word(NO_COLOR, 'q')} {color_word(NO_COLOR, 'w')} {color_word(NO_COLOR, 'e')} "
            f"{color_word(NO_COLOR, 'r')} {color_word(NO_COLOR, 't')} {color_word(NO_COLOR, 'y')} "
            f"{color_word(NO_COLOR, 'u')} {color_word(NO_COLOR, 'i')} {color_word(NO_COLOR, 'o')} "
            f"{color_word(NO_COLOR, 'p')}\n"
            f" {color_word(NO_COLOR, 'a')} {color_word(NO_COLOR, 's')} {color_word(NO_COLOR, 'd')} "
            f"{color_word(NO_COLOR, 'f')} {color_word(NO_COLOR, 'g')} {color_word(NO_COLOR, 'h')} "
            f"{color_word(NO_COLOR, 'j')} {color_word(NO_COLOR, 'k')} {color_word(NO_COLOR, 'l')}\n"
            f"   {color_word(NO_COLOR, 'z')} {color_word(NO_COLOR, 'x')} {color_word(NO_COLOR, 'c')} "
            f"{color_word(NO_COLOR, 'v')} {color_word(NO_COLOR, 'b')} {color_word(NO_COLOR, 'n')} "
            f"{color_word(NO_COLOR, 'm')}"
        )
        self.assertEqual(
            str(keyboard), expected_output, f"\n{keyboard} \n!=\n{expected_output}"
        )

    def test_2(self):
        """__str__(): Single correct letter 'a' in 'apple'"""
        keyboard = Keyboard()
        keyboard.update(
            [
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "apple",
        )
        expected_output = (
            f"{color_word(NO_COLOR, 'q')} {color_word(NO_COLOR, 'w')} {color_word(NOT_IN_WORD_COLOR, 'e')} "
            f"{color_word(NO_COLOR, 'r')} {color_word(NO_COLOR, 't')} {color_word(NO_COLOR, 'y')} "
            f"{color_word(NO_COLOR, 'u')} {color_word(NO_COLOR, 'i')} {color_word(NO_COLOR, 'o')} "
            f"{color_word(NOT_IN_WORD_COLOR, 'p')}\n"
            f" {color_word(CORRECT_COLOR, 'a')} {color_word(NO_COLOR, 's')} {color_word(NO_COLOR, 'd')} "
            f"{color_word(NO_COLOR, 'f')} {color_word(NO_COLOR, 'g')} {color_word(NO_COLOR, 'h')} "
            f"{color_word(NO_COLOR, 'j')} {color_word(NO_COLOR, 'k')} {color_word(NOT_IN_WORD_COLOR, 'l')}\n"
            f"   {color_word(NO_COLOR, 'z')} {color_word(NO_COLOR, 'x')} {color_word(NO_COLOR, 'c')} "
            f"{color_word(NO_COLOR, 'v')} {color_word(NO_COLOR, 'b')} {color_word(NO_COLOR, 'n')} "
            f"{color_word(NO_COLOR, 'm')}"
        )
        self.assertEqual(
            str(keyboard), expected_output, f"\n{keyboard} \n!=\n{expected_output}"
        )

    def test_3(self):
        """__str__(): Single wrong spot letter 'o' in 'loose'"""
        keyboard = Keyboard()
        keyboard.update(
            [
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "loose",
        )
        expected_output = (
            f"{color_word(NO_COLOR, 'q')} {color_word(NO_COLOR, 'w')} {color_word(NOT_IN_WORD_COLOR, 'e')} "
            f"{color_word(NO_COLOR, 'r')} {color_word(NO_COLOR, 't')} {color_word(NO_COLOR, 'y')} "
            f"{color_word(NO_COLOR, 'u')} {color_word(NO_COLOR, 'i')} {color_word(WRONG_SPOT_COLOR, 'o')} "
            f"{color_word(NO_COLOR, 'p')}\n"
            f" {color_word(NO_COLOR, 'a')} {color_word(NOT_IN_WORD_COLOR, 's')} {color_word(NO_COLOR, 'd')} "
            f"{color_word(NO_COLOR, 'f')} {color_word(NO_COLOR, 'g')} {color_word(NO_COLOR, 'h')} "
            f"{color_word(NO_COLOR, 'j')} {color_word(NO_COLOR, 'k')} {color_word(NOT_IN_WORD_COLOR, 'l')}\n"
            f"   {color_word(NO_COLOR, 'z')} {color_word(NO_COLOR, 'x')} {color_word(NO_COLOR, 'c')} "
            f"{color_word(NO_COLOR, 'v')} {color_word(NO_COLOR, 'b')} {color_word(NO_COLOR, 'n')} "
            f"{color_word(NO_COLOR, 'm')}"
        )
        self.assertEqual(
            str(keyboard), expected_output, f"\n{keyboard} \n!=\n{expected_output}"
        )

    def test_4(self):
        """__str__(): CORRECT_COLOR 's' and 't' remain with other updates in 'stone' and 'straw'"""
        keyboard = Keyboard()
        keyboard.update(
            [
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "stone",
        )
        keyboard.update(
            [
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            "straw",
        )
        expected_output = (
            f"{color_word(NO_COLOR, 'q')} {color_word(NOT_IN_WORD_COLOR, 'w')} {color_word(NOT_IN_WORD_COLOR, 'e')} "
            f"{color_word(NOT_IN_WORD_COLOR, 'r')} {color_word(WRONG_SPOT_COLOR, 't')} {color_word(NO_COLOR, 'y')} "
            f"{color_word(NO_COLOR, 'u')} {color_word(NO_COLOR, 'i')} {color_word(NOT_IN_WORD_COLOR, 'o')} "
            f"{color_word(NO_COLOR, 'p')}\n"
            f" {color_word(WRONG_SPOT_COLOR, 'a')} {color_word(CORRECT_COLOR, 's')} {color_word(NO_COLOR, 'd')} "
            f"{color_word(NO_COLOR, 'f')} {color_word(NO_COLOR, 'g')} {color_word(NO_COLOR, 'h')} "
            f"{color_word(NO_COLOR, 'j')} {color_word(NO_COLOR, 'k')} {color_word(NO_COLOR, 'l')}\n"
            f"   {color_word(NO_COLOR, 'z')} {color_word(NO_COLOR, 'x')} {color_word(NO_COLOR, 'c')} "
            f"{color_word(NO_COLOR, 'v')} {color_word(NO_COLOR, 'b')} {color_word(NOT_IN_WORD_COLOR, 'n')} "
            f"{color_word(NO_COLOR, 'm')}"
        )
        self.assertEqual(
            str(keyboard), expected_output, f"\n{keyboard} \n!=\n{expected_output}"
        )


class TestWordFamilyDifficulty(unittest.TestCase):
    """WordFamily Difficulty Calculation Tests"""

    def test_1(self):
        """WordFamily.difficulty: pattern with all CORRECT_COLOR"""
        family = WordFamily(feedback_colors=[CORRECT_COLOR] * 5, words=["salet"])
        self.assertEqual(family.difficulty, 0)

    def test_2(self):
        """WordFamily.difficulty: pattern with all WRONG_SPOT_COLOR"""
        family = WordFamily(
            feedback_colors=[WRONG_SPOT_COLOR] * 5, words=["aster", "tears"]
        )
        self.assertEqual(family.difficulty, 5)

    def test_3(self):
        """WordFamily.difficulty: pattern with all NOT_IN_WORD_COLOR"""
        family = WordFamily(
            feedback_colors=[NOT_IN_WORD_COLOR] * 5, words=["world", "flame"]
        )
        self.assertEqual(family.difficulty, 10)

    def test_4(self):
        """WordFamily.difficulty: mixed pattern of CORRECT_COLOR and WRONG_SPOT_COLOR"""
        family = WordFamily(
            feedback_colors=[
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
            ],
            words=["slate"],
        )
        self.assertEqual(family.difficulty, 2)  # 0 + 1 + 0 + 1 + 0

    def test_5(self):
        """WordFamily.difficulty: pattern with CORRECT_COLOR, WRONG_SPOT_COLOR, and NOT_IN_WORD_COLOR"""
        family = WordFamily(
            feedback_colors=[
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
            ],
            words=["apple"],
        )
        self.assertEqual(family.difficulty, 4)  # 0 + 2 + 1 + 0 + 1

    def test_6(self):
        """WordFamily.difficulty: multiple words, difficulty based only on pattern"""
        family = WordFamily(
            feedback_colors=[
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
            ],
            words=["fried", "dried"],
        )
        self.assertEqual(family.difficulty, 5)  # 1 + 0 + 2 + 0 + 2


class TestWordFamilyComparison(unittest.TestCase):
    """Tests for the __lt__ method of WordFamily"""

    def test_1(self):
        """__lt__: fewer words compared to more words"""
        family1 = WordFamily(
            [
                CORRECT_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["break", "bream"],
        )
        family2 = WordFamily(
            [
                CORRECT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["broad"],
        )

        self.assertTrue(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_2(self):
        """__lt__: more words compared to fewer words"""
        family1 = WordFamily(
            [
                CORRECT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["bread"],
        )
        family2 = WordFamily(
            [
                CORRECT_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["break", "bream"],
        )
        self.assertFalse(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_3(self):
        """__lt__: same sizes and difficulty, lexicographically smaller pattern"""
        family1 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["angle", "angel"],
        )
        family2 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            ["store", "stove"],
        )
        self.assertTrue(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_4(self):
        """__lt__: same sizes and difficulty, lexicographically larger pattern"""
        family1 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            ["store", "stove"],
        )
        family2 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["angle", "angel"],
        )
        self.assertFalse(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_5(self):
        """__lt__: same sizes but larger difficulty (7 vs 5)"""
        family1 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["angle", "angel"],
        )
        family2 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            ["grain", "groin"],
        )
        self.assertTrue(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_6(self):
        """__lt__: same sizes but smaller difficulty (5 vs 7)"""
        family1 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            ["grain", "groin"],
        )
        family2 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["angle", "angel"],
        )
        self.assertFalse(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_7(self):
        """__lt__: same families"""
        family1 = WordFamily(
            [
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["apple"],
        )
        family2 = WordFamily(
            [
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                CORRECT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["apple"],
        )
        self.assertFalse(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_8(self):
        """__lt__: fewer words and lower difficulty compared to more words and higher difficulty"""
        family1 = WordFamily([NOT_IN_WORD_COLOR] * 5, ["ample", "apple"])
        family2 = WordFamily([CORRECT_COLOR] * 5, ["apply"])
        self.assertTrue(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_9(self):
        """__lt__: more words and lower difficulty compared to fewer words and higher difficulty"""
        family1 = WordFamily(
            [NOT_IN_WORD_COLOR] + [CORRECT_COLOR] * 4,
            ["fight", "light", "might", "sight"],
        )
        family2 = WordFamily([NOT_IN_WORD_COLOR] * 5, ["ample", "apple"])
        self.assertTrue(family1 < family2, f"Family1: {family1}, Family2: {family2}")

    def test_10(self):
        """__lt__: fewer words but same difficulty"""
        family1 = WordFamily(
            [
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["brain", "drain"],
        )
        family2 = WordFamily(
            [
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            ["chair"],
        )
        self.assertTrue(family1 < family2, f"Family1: {family1}, Family2: {family2}")


class TestFastSort(unittest.TestCase):
    """Tests for the fast_sort function with different types of lists"""

    def test_1(self):
        """fast_sort: empty list"""
        self.assertEqual(fast_sort([]), [])

    def test_2(self):
        """fast_sort: single-element list"""
        self.assertEqual(fast_sort([10]), [10])

    def test_3(self):
        """fast_sort: already sorted list of integers"""
        self.assertEqual(fast_sort([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])

    def test_4(self):
        """fast_sort: unsorted list of integers"""
        self.assertEqual(fast_sort([4, 2, 5, 1, 3]), [1, 2, 3, 4, 5])

    def test_5(self):
        """fast_sort: unsorted list of floats"""
        self.assertEqual(
            fast_sort([4.5, 2.1, 3.3, 1.0, 5.6]), [1.0, 2.1, 3.3, 4.5, 5.6]
        )

    def test_6(self):
        """fast_sort: already sorted list of strings"""
        self.assertEqual(
            fast_sort(["apple", "banana", "cherry"]), ["apple", "banana", "cherry"]
        )

    def test_7(self):
        """fast_sort: unsorted list of strings"""
        self.assertEqual(
            fast_sort(["cherry", "apple", "banana"]), ["apple", "banana", "cherry"]
        )

    def test_8(self):
        """fast_sort: already sorted list of WordFamily objects by size"""
        family1 = WordFamily(
            feedback_colors=[
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                CORRECT_COLOR,
                CORRECT_COLOR,
                CORRECT_COLOR,
            ],
            words=["fight", "light", "might", "sight"],
        )
        family2 = WordFamily(
            feedback_colors=[
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            words=["brain", "drain"],
        )
        family3 = WordFamily(
            feedback_colors=[
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            words=["grant"],
        )
        self.assertEqual(
            fast_sort([family1, family2, family3]), [family1, family2, family3]
        )

    def test_9(self):
        """fast_sort: unsorted list of WordFamily objects by difficulty"""
        family1 = WordFamily(feedback_colors=[CORRECT_COLOR] * 5, words=["apple"])
        family2 = WordFamily(feedback_colors=[NOT_IN_WORD_COLOR] * 5, words=["round"])
        family3 = WordFamily(
            feedback_colors=[CORRECT_COLOR] * 4 + [NOT_IN_WORD_COLOR], words=["apply"]
        )
        self.assertEqual(
            fast_sort([family1, family2, family3]), [family2, family3, family1]
        )

    def test_10(self):
        """fast_sort: list of multiple WordFamily objects"""
        family1 = WordFamily(
            feedback_colors=[
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
            ],
            words=["bread", "break", "bream"],
        )
        family2 = WordFamily(
            feedback_colors=[
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            words=["dandy", "dawns"],
        )
        family3 = WordFamily(
            feedback_colors=[
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            words=["brain", "broad"],
        )
        family4 = WordFamily(
            feedback_colors=[
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
                WRONG_SPOT_COLOR,
                NOT_IN_WORD_COLOR,
            ],
            words=["plant", "slant"],
        )
        family5 = WordFamily(
            feedback_colors=[
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
                NOT_IN_WORD_COLOR,
                NOT_IN_WORD_COLOR,
                CORRECT_COLOR,
            ],
            words=["dance", "haste"],
        )
        self.assertEqual(
            fast_sort([family2, family3, family1, family4, family5]),
            [family1, family2, family3, family4, family5],
        )


class TestGetFeedbackColors(unittest.TestCase):
    """Get Feedback Color Tests"""

    def test_1(self):
        """get_feedback_colors(): secret word basil and guessed word basil"""
        secret_word = "basil"
        guessed_word = "basil"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_2(self):
        """get_feedback_colors(): secret word lever and guessed word light"""
        secret_word = "lever"
        guessed_word = "light"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_3(self):
        """get_feedback_colors(): secret word llama and guessed word ladle"""
        secret_word = "llama"
        guessed_word = "ladle"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            CORRECT_COLOR,
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_4(self):
        """get_feedback_colors(): secret word aback and guessed word abaca"""
        secret_word = "aback"
        guessed_word = "abaca"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_5(self):
        """get_feedback_colors(): secret word hello and guessed word label"""
        secret_word = "hello"
        guessed_word = "label"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            WRONG_SPOT_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_6(self):
        """get_feedback_colors(): secret word gaily and guessed word hello"""
        secret_word = "gaily"
        guessed_word = "hello"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_7(self):
        """get_feedback_colors(): secret word riped and guessed word crown"""
        secret_word = "riped"
        guessed_word = "crown"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_8(self):
        """get_feedback_colors(): secret word table and guessed word metal"""
        secret_word = "table"
        guessed_word = "metal"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            WRONG_SPOT_COLOR,
            WRONG_SPOT_COLOR,
            WRONG_SPOT_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_9(self):
        """get_feedback_colors(): secret word index and guessed word linen"""
        secret_word = "index"
        guessed_word = "linen"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            WRONG_SPOT_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )

    def test_10(self):
        """get_feedback_colors(): secret word bleak and guessed word helix"""
        secret_word = "bleak"
        guessed_word = "helix"
        actual = get_feedback_colors(secret_word, guessed_word)
        expected = [
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
        ]
        self.assertEqual(
            actual,
            expected,
            f"got {color_word(actual, guessed_word)} but expected {color_word(expected, guessed_word)}",
        )


class TestGetFeedback(unittest.TestCase):
    """Tests for the get_feedback function with different guess and word family scenarios"""

    def test_1(self):
        """get_feedback: pick largest word family"""
        remaining_secret_words = ["bread", "break", "bream"]
        guessed_word = "broad"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            CORRECT_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(sorted(words), ["break", "bream"])

    def test_2(self):
        """get_feedback: both families are equal sized, tie broken by difficulty"""
        remaining_secret_words = [
            "ample",
            "apple",
            "bread",
            "break",
            "bream",
            "stale",
        ]
        guessed_word = "fable"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(sorted(words), ["bread", "break", "bream"])

    def test_3(self):
        """get_feedback: word family larger but with same difficulty as other families"""
        remaining_secret_words = [
            "alone",
            "clone",
            "dance",
            "dandy",
            "chard",
            "charm",
            "chasm",
            "store",
            "stove",
        ]
        guessed_word = "night"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(sorted(words), ["alone", "clone", "dance", "dandy"])

    def test_4(self):
        """get_feedback: only 1 word family with 1 word which is guessed"""
        remaining_secret_words = ["prana"]
        guessed_word = "prana"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(words, ["prana"])

    def test_5(self):
        """get_feedback: equal sized families, tie broken by difficulty (4 vs 0)"""
        remaining_secret_words = ["grant", "prana"]
        guessed_word = "grant"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            NOT_IN_WORD_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(words, ["prana"])

    def test_6(self):
        """get_feedback: equal sized families, tie broken by difficulty (5 vs 2)"""
        remaining_secret_words = ["grain", "grant", "prana", "train"]
        guessed_word = "drain"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            NOT_IN_WORD_COLOR,
            CORRECT_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(sorted(words), ["grant", "prana"])

    def test_7(self):
        """get_feedback: pick largest family of size 5"""
        remaining_secret_words = [
            "chain",
            "chair",
            "chant",
            "chard",
            "charm",
            "chasm",
            "drain",
            "grain",
            "grant",
            "hoard",
            "prana",
            "train",
        ]
        guessed_word = "chasm"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            CORRECT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(
            sorted(words), sorted(["drain", "grain", "grant", "prana", "train"])
        )

    def test_8(self):
        """get_feedback: equal difficulty word families, but first tiebreaker is family size (4 vs 1)"""
        remaining_secret_words = ["shalt", "grain", "grant", "prana", "train"]
        guessed_word = "hoard"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            CORRECT_COLOR,
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(sorted(words), sorted(["grain", "grant", "prana", "train"]))

    def test_9(self):
        """get_feedback: two families have equal difficulty and size, tie broken by the pattern's ASCII comparison"""
        remaining_secret_words = sorted(
            [
                "heaps",
                "heard",
                "heart",
                "stone",
                "store",
                "stove",
                "dandy",
                "dawns",
                "brain",
                "broad",
            ]
        )
        guessed_word = "fable"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            WRONG_SPOT_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(words, sorted(["heaps", "heard", "heart"]))

    def test_10(self):
        """get_feedback: equal length families, each length 2, tie broken by difficulty (9 vs 5)"""
        remaining_secret_words = [
            "alone",
            "ample",
            "ample",
            "angle",
            "angle",
            "apple",
            "apply",
            "dandy",
            "dawns",
            "eagle",
            "fable",
        ]
        guessed_word = "ample"
        feedback, words = get_feedback(remaining_secret_words, guessed_word)
        expected_feedback = (
            WRONG_SPOT_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
            NOT_IN_WORD_COLOR,
        )
        self.assertEqual(feedback, expected_feedback)
        self.assertEqual(words, ["dandy", "dawns"])

class TestWordle(unittest.TestCase):

    def check_diff(self, actual_output, output_file):
        """Helper function to check differences between actual output and the expected file content"""

        with open(
            os.path.join("expected_default_outputs", output_file), "r", encoding="UTF-8"
        ) as outfile:
            expected_default_output = outfile.read()

        with open(
            os.path.join("expected_high_contrast_outputs", output_file),
            "r",
            encoding="UTF-8",
        ) as outfile:
            expected_high_contrast_output = outfile.read()

        default_diff = list(
            difflib.unified_diff(
                expected_default_output.splitlines(keepends=True),
                actual_output.splitlines(keepends=True),
                fromfile="expected output",
                tofile="actual output",
                lineterm="",
            )
        )

        high_contrast_diff = list(
            difflib.unified_diff(
                expected_high_contrast_output.splitlines(keepends=True),
                actual_output.splitlines(keepends=True),
                fromfile="expected output",
                tofile="actual output",
                lineterm="",
            )
        )

        if len(default_diff) <= len(high_contrast_diff):
            diff_result = default_diff
        else:
            diff_result = high_contrast_diff

        if diff_result:
            diff_output = "\n".join(diff_result)
            self.fail(
                f"Differences found between actual output and {output_file}:\n{diff_output}"
            )

    def run_wordle_with_input(self, input_file):
        """Helper function to run wordle.py with input from a file, and capture output as a string"""
        with open(input_file, "r") as infile:
            inputs = infile.read().splitlines()
        i = 0

        # Function to mock each input call
        def input_mock(prompt=""):
            nonlocal i
            # Print or log each input as it's read from the file
            if i < len(inputs):
                current_input = inputs[i]
                print(f"{prompt}{current_input}")
                i += 1
                return current_input
            raise EOFError("EOF when reading a line")

        output_buffer = io.StringIO()
        with patch("builtins.input", input_mock), patch(
            "sys.stdout", new=output_buffer
        ):
            sys.argv = ["evil_wordle.py"]
            evil_wordle.main()

        return output_buffer.getvalue()

    def run_test_case(self, test_case):
        """Helper function to handle test case execution and diff checking"""
        input_file = f"{test_case}.in"
        output_file = f"{test_case}.ansi"

        actual_output = self.run_wordle_with_input(input_file)
        self.check_diff(actual_output, output_file)

    def test_banns(self):
        """python3 evil_wordle.py < banns.in"""
        self.run_test_case("banns")

    def test_boozy(self):
        """python3 evil_wordle.py < boozy.in"""
        self.run_test_case("boozy")

    def test_judge(self):
        """python3 evil_wordle.py < judge.in"""
        self.run_test_case("judge")

    def test_kakas(self):
        """python3 evil_wordle.py < kakas.in"""
        self.run_test_case("kakas")

    def test_kooks(self):
        """python3 evil_wordle.py < kooks.in"""
        self.run_test_case("kooks")

    def test_pared(self):
        """python3 evil_wordle.py < pared.in"""
        self.run_test_case("pared")

    def test_sages(self):
        """python3 evil_wordle.py < sages.in"""
        self.run_test_case("sages")

    def test_sixes(self):
        """python3 evil_wordle.py < sixes.in"""
        self.run_test_case("sixes")

    def test_wides(self):
        """python3 evil_wordle.py < wides.in"""
        self.run_test_case("wides")

    def test_woozy(self):
        """python3 evil_wordle.py < woozy.in"""
        self.run_test_case("woozy")

if __name__ == "__main__":
    unittest.main()
