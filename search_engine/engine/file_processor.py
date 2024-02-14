import json
import os


class RawWebpages:
    def __init__(self):
        self._len = 0
        self._pages = {}
        self._root_path = "../../WEBPAGES_RAW"

    def get_len(self) -> int:
        return self._len

    def get_pages(self) -> dict:
        return self._pages

    def initialize_raw_webpage(self):
        file_path = os.path.join(self._root_path, "bookkeeping.json")
        with open(file_path, 'r', encoding='utf-8') as file:
            self._pages = json.load(file)
            self._len = len(self._pages)
            print(self._len)

    def load_raw_webpage_content(self, folder_num, file_num):
        file_path = os.path.join(self._root_path, str(folder_num), str(file_num))
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        return content

class Log:
    def __init__(self, path):
        self._log_path = path

    def update_log(self, new_log):
        with open(self._log_path, "r") as log:
            lines = log.readlines()
            if len(lines) > 10:
                lines.pop(0)
            lines.append(new_log + '\n')

        with open(self._log_path, "w") as log:
            log.writelines(lines)

    def get_latest_log(self):
        try:
            with open(self._log_path, "r") as log:
                lines = log.readlines()
                if lines:
                    return lines[-1]
                else:
                    return ""
        except FileNotFoundError:
            with open(self._log_path, "w") as log:
                pass
            return ""


# if __name__ == '__main__':
#     raw = RawWebpages()
#     content = raw.load_raw_webpage_content(0, 2)
#     print(content)
#     for key, value in Method.calculate_token_weight(content).items():
#         print(key)
#         print(value)
