# Name: Shenghao Fu
# Student ID: 80409258
#
# This module provides a set of functions to read the content from a file, tokenize the content into words,
# calculate the frequency of each word, sort these frequencies, and then print them.
# Time Complexity: O(nlog(n))


import sys
from collections import Counter


def get_comm_line_args(num: int) -> list:
    """
    This function checks if the correct number of command-line arguments are passed to the script.

    It expects 'num' arguments (excluding the script name itself). If the number of arguments
    does not match 'num', it prints an error message and exits the program. Otherwise, it returns
    a list of the provided arguments.

    Time Complexity: O(1)

    :param num: int, the expected number of arguments
    :return: list, a list of command-line arguments provided to the script.
    """
    if len(sys.argv) != num + 1:
        print(f"Error: The program expects {num} parameters, but got {len(sys.argv) - 1}.")
        exit(1)
    return sys.argv[1:]


def get_content(name: str) -> str:
    """
    Reads and returns the contents of the specified file as a string.

    This function opens a file with the given name, reads its content line by line,
    and returns the entire content as a single string. Non-UTF-8 characters are replaced
    with a replacement character.

    Time Complexity: O(n)

    :param name: str, the path or name of the file to read.
    :return:str, a string of the file contents.
    """
    content = []
    try:
        if not isinstance(name, str):
            raise TypeError("Input must be a string")

        with open(name, 'r', encoding = 'utf-8', errors = 'replace') as file:
            for line in file:
                content.append(line)

    except FileNotFoundError:
        print(f"Error: File does not exist - '{name}'")
    except PermissionError:
        print(f"Error: Permission denied when reading the file - '{name}'")
    except UnicodeDecodeError:
        print(f"Error: Unicode decode error while reading the file - '{name}'")
    except TypeError as e:
        print(f"Error: {e} - 'get_content' function expects a string input")
    except Exception as e:
        print(f"Error: An unexpected error occurred while reading the file - '{name}': {e}")

    return ''.join(content)


def is_english_alphanumeric(c: str) -> bool:
    """
    Determines whether the given character is an English alphanumeric character.

    An English alphanumeric character is defined as any of the characters:
    a-z, A-Z, or 0-9.

    Time Complexity: O(1)

    :param c: str, a single character to be checked.
    :return:bool, True if the character is an English letter or digit, False otherwise.
    """
    try:
        if not isinstance(c, str) or len(c) != 1:
            raise TypeError("Input must be a single character")

        return ('a' <= c <= 'z') or ('A' <= c <= 'Z') or ('0' <= c <= '9')

    except TypeError as e:
        print(
            f"Error: {e} - 'is_english_alphanumeric' function expects a string input with length one")
        return False
    except Exception as e:
        print(f"Error: An unexpected error occurred while determine the alphanumeric: {e}")
        return False


def tokenize(str_content: str) -> list:
    """
    Splits a string into words, where each word consists of English letters and digits.

    Each character in the string is checked to see if it's an English alphanumeric character.
    If so, it's added to the current word. If a non-alphanumeric character is encountered,
    the current word is completed and added to the words list.

    Time Complexity: O(n)

    :param str_content: str, the string to be tokenized.
    :return: list, a list of words extracted from the input string.
    """
    words = []
    try:
        if not isinstance(str_content, str):
            raise TypeError("Input must be a string")

        current_word = ''
        for c in str_content:
            if is_english_alphanumeric(c):
                current_word += c
            elif current_word:
                words.append(current_word.lower())
                current_word = ''
        if current_word:
            words.append(current_word.lower())

    except TypeError as e:
        print(f"Error: {e} - 'tokenize' function expects a string input")
    except Exception as e:
        print(f"Error: An unexpected error occurred while tokenize: {e}")

    return words


def get_words_frequency(str_content: str) -> dict:
    """
    Calculates and returns the frequency of each word in the given string.

    The function first tokenizes the input string and then counts the frequency
    of each word using a Counter collection.

    Time Complexity: O(n)

    :param str_content: str, the string from which to calculate word frequencies.
    :return: dict, a dictionary where keys are words and values are their corresponding frequencies.
    """
    words_frequency = {}
    try:
        if not isinstance(str_content, str):
            raise TypeError("Input must be a string")

        words = tokenize(str_content)
        words_frequency = Counter(words)

    except TypeError as e:
        print(f"Error: {e} - 'get_words_frequency' function expects a string input")
    except Exception as e:
        print(f"Error: An unexpected error occurred while get words frequency: {e}")

    return words_frequency


def sort_frequency(words_frequency: dict) -> list[tuple]:
    """
    Sorts the given word frequency dictionary first by frequency in descending order
    and then by word in alphabetical order.

    The function uses Python's built-in sorted function to sort the dictionary items,
    which are word-frequency pairs, based on a custom sorting key.

    Time Complexity: O(nlog(n))

    :param words_frequency: dict, a dictionary where keys are words and values are their frequencies.
    :return: list[tuple], a sorted list of tuples, where each tuple is a word-frequency pair.
    """
    try:
        if not isinstance(words_frequency, dict):
            raise TypeError("Input must be a dictionary")

        return sorted(words_frequency.items(), key=lambda item: (-item[1], item[0]))

    except TypeError as e:
        print(f"Error: {e} - 'sort_frequency' function expects a dictionary input")
    except Exception as e:
        print(f"Error: An unexpected error occurred while sort frequency: {e}")

    return []


def print_frequency(words_frequency: list[tuple]) -> None:
    """
    Prints the frequency of each word in the given list of word-frequency pairs.

    For each word-frequency pair in the list, the function prints the word and its frequency,
    separated by a tab character.

    Time Complexity: O(n)

    :param words_frequency: list[tuple], a list of tuples where each tuple is a word-frequency pair.
    :return: None
    """
    try:
        if not isinstance(words_frequency, list):
            raise TypeError("Input must be a list")

        for pair in words_frequency:
            print(f"{pair[0]}\t{pair[1]}")

    except TypeError as e:
        print(f"Error: {e} - 'print_frequency' function expects a list input")
    except Exception as e:
        print(f"Error: An unexpected error occurred while print frequency: {e}")


if __name__ == '__main__':
    args = get_comm_line_args(1)  # O(1)
    file_name: str = args[0]  # O(1)
    file_content: str = get_content(file_name)  # O(n)
    frequency: dict = get_words_frequency(file_content)  # O(n)
    print_frequency(sort_frequency(frequency))  # O(nlog(n))
