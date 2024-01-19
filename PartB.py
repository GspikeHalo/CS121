# Name: Shenghao Fu
# Student ID: 80409258
#
# This module provides functionality to read contents from files, tokenize the contents into words,
# count the unique words, and find the number of common words between two files.
# Time Complexity: O(n)

import sys


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


def count_words(str_content: str) -> set:
    """
    Counts the unique words in the given string and returns a set containing these words.

    The function first tokenizes the input string and then creates a set
    to keep track of the presence of each word.

    Time Complexity: O(n)

    :param str_content: str, the string from which to count words.
    :return: set, a set where keys are unique words from the input string.
    """
    set_words: set = set()
    try:
        if not isinstance(str_content, str):
            raise TypeError("Input must be a string")

        words: list = tokenize(str_content)
        set_words: set = set(words)

    except TypeError as e:
        print(f"Error: {e} - 'count_words' function expects a string input")
    except Exception as e:
        print(f"Error: An unexpected error occurred while count words: {e}")

    return set_words


def get_intersection_num(file1: set, file2: set) -> int:
    """
    Calculates the number of intersecting keys between two sets.

    The function iterates through each key in 'file1' and checks for its presence in 'file2',
    incrementing the count for each found key.

    Time Complexity: O(n)

    :param file1: set, the first set.
    :param file2: set, the second set.
    :return: int, the count of intersecting keys between the two sets.
    """
    count: int = 0
    try:
        if not isinstance(file1, set) or not isinstance(file2, set):
            raise TypeError("Both file1 and file2 must be sets")

        for word in file1:
            if word in file2:
                count += 1

    except TypeError as e:
        print(f"Error: {e} - 'get_intersection_num' function expects a set input")
    except Exception as e:
        print(f"Error: An unexpected error occurred while get intersection number: {e}")

    return count


if __name__ == '__main__':
    args = get_comm_line_args(2)  # O(1)
    file1_name: str = args[0]  # O(1)
    file2_name: str = args[1]  # O(1)
    file1_content: str = get_content(file1_name)  # O(n)
    file2_content: str = get_content(file2_name)  # O(n)
    file1_words: set = count_words(file1_content)  # O(n)
    file2_words: set = count_words(file2_content)  # O(n)
    intersection_num: int = get_intersection_num(file1_words, file2_words)  # O(n)
    print(intersection_num)  # O(1)
