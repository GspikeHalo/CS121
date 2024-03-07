#  .search_engine/engine/file_processor.py

import json
import os


class RawWebpages:
    """
    A class to manage and access the content of raw webpages stored in files.
    """
    def __init__(self):
        self._len = 0
        self._pages = {}
        self._root_path = None

    def set_root_path(self, path="../../"):
        self._root_path = os.path.join(path, "WEBPAGES_RAW")

    def get_len(self) -> int:
        """
        Get the number of webpages managed by this instance.

        :return: The length of the _pages dictionary.
        """
        return self._len

    def get_pages(self) -> dict:
        """
        Get the dictionary of webpages.

        :return: The _pages dictionary, key is doc_id and value is url.
        """
        return self._pages

    def initialize_raw_webpage(self) -> None:
        """
        Initializes the webpage metadata from a JSON file.

        :return: None
        """
        file_path = os.path.join(self._root_path, "bookkeeping.json")
        with open(file_path, 'r', encoding='utf-8') as file:
            self._pages = json.load(file)
            self._len = len(self._pages)

    def load_raw_webpage_content(self, folder_num: int | str, file_num: int | str) -> str:
        """
        Loads the content of a specific raw webpage given its folder and file number.

        :param folder_num: The folder number part of the webpage's path.
        :param file_num: The file number part of the webpage's path.
        :return: The content of the specified raw webpage.
        """
        file_path = os.path.join(self._root_path, str(folder_num), str(file_num))
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content


class Log:
    """
    A class for managing a simple log file.
    """

    def __init__(self, path):
        self._log_path = path

    def update_log(self, new_log: str) -> None:
        """
        Updates the log file with a new log entry, maintaining a maximum of 10 entries.

        :param new_log: The new log entry to add.
        :return:
        """
        with open(self._log_path, "r") as log:
            lines = log.readlines()
            if len(lines) > 10:
                lines.pop(0)
            lines.append(new_log + '\n')

        with open(self._log_path, "w") as log:
            log.writelines(lines)

    def get_latest_log(self) -> str:
        """
        Retrieves the latest log entry from the log file.

        :return: The latest log entry as a string, or an empty string if no entries exist.
        """
        try:
            with open(self._log_path, "r") as log:
                lines = [line.strip() for line in log.readlines() if line.strip()]
                if lines:
                    return lines[-1]
                else:
                    return ""
        except FileNotFoundError:
            with open(self._log_path, "w") as log:
                pass
            return ""
