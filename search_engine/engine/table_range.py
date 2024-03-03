#  .search_engine/engine/table_range.py

import json


class TableRange:
    def __init__(self, filepath='../../database/table_ranges.json'):
        self.filepath = filepath
        self.table_ranges = self._load_table_ranges()

    def update_table_ranges(self, table_ranges: list[tuple]) -> None:
        for table_name, start_doc_id, end_doc_id in table_ranges:
            self.table_ranges[table_name] = {
                'start_doc_id': start_doc_id,
                'end_doc_id': end_doc_id
            }
        self._save_table_ranges()

    def get_table_ranges(self) -> list[tuple]:
        return [(table_name, info['start_doc_id'], info['end_doc_id']) for table_name, info in self.table_ranges.items()]

    def get_table_name_for_doc_id(self, doc_id: str) -> str:
        doc_id_num = tuple(map(int, doc_id.split('/')))
        for table_name, range_info in self.table_ranges.items():
            start_num = tuple(map(int, range_info['start_doc_id'].split('/')))
            end_num = tuple(map(int, range_info['end_doc_id'].split('/')))
            if start_num <= doc_id_num <= end_num:
                return table_name
        return ""

    def _load_table_ranges(self):
        try:
            with open(self.filepath, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(self.filepath, 'w') as file:
                json.dump({}, file)  # 创建一个空的JSON对象
            return {}
        except json.JSONDecodeError:
            return {}

    def _save_table_ranges(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.table_ranges, file, indent=4)

