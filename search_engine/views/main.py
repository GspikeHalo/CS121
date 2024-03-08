# views/main.py

import tkinter as tk
from search_engine.events.events import *


class MainView(tk.Tk):
    def __init__(self, event_bus):
        super().__init__()
        self._paged_results = None
        self._current_page = 0
        self._event_bus = event_bus
        self.title("Search Engine")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def set_db(self, path):
        self._event_bus.initiate_event(OpenDatabaseEvent(path))

    def run(self):
        self._create_widgets()
        self.mainloop()

    def _on_close(self):
        self._event_bus.initiate_event(CloseDatabaseEvent())
        self.destroy()

    def _create_widgets(self):
        """
        创建并布局UI组件。
        """
        # 创建搜索框和搜索按钮的容器
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)

        # 创建一个变量来保存单选按钮的选择
        self.search_option = tk.StringVar(value="token")  # 默认选择"token"

        self.url_radiobutton = tk.Radiobutton(self.search_frame, text="URL", variable=self.search_option, value="url")
        self.url_radiobutton.pack(side=tk.LEFT, padx=5)
        self.token_radiobutton = tk.Radiobutton(self.search_frame, text="Token", variable=self.search_option,
                                                value="token")
        self.token_radiobutton.pack(side=tk.LEFT, padx=5)

        # 搜索输入框，让用户可以输入搜索关键词
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.on_search)
        self.search_button.pack(side=tk.LEFT, padx=5)

        # 搜索结果列表的容器，展示搜索结果
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(fill = tk.BOTH, expand = True, pady = 5)

        # 搜索结果列表，展示搜索结果摘要信息
        self.results_list = tk.Listbox(self.results_frame)
        self.results_list.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx = 5, pady = 5)

        # 详情查看和分页控制的容器
        self.detail_frame = tk.Frame(self)
        self.detail_frame.pack(fill = tk.X, padx = 5, pady = 5)

        # 分页按钮的容器，放在detail_frame的最右边
        self.page_navigation_frame = tk.Frame(self.detail_frame)
        self.page_navigation_frame.pack(side = tk.RIGHT, padx = 5)

        # 上一页按钮，查看前一页搜索结果
        self.prev_page_button = tk.Button(self.page_navigation_frame, text = "Previous Page",
                                          command = lambda: self.on_change_page("prev"))
        self.prev_page_button.pack(side = tk.LEFT, padx = 5)

        # 下一页按钮，查看后一页搜索结果
        self.next_page_button = tk.Button(self.page_navigation_frame, text = "Next Page",
                                          command = lambda: self.on_change_page("next"))
        self.next_page_button.pack(side = tk.LEFT, padx = 5)

    def on_search(self):
        """
        处理搜索按钮点击事件，发起搜索。
        """
        query = self.search_entry.get()
        search_option = self.search_option.get()  # 获取单选按钮的选项
        if search_option == "url":
            self._event_bus.initiate_event(SearchURLEvent(query))
        elif search_option == "token":
            self._event_bus.initiate_event(SearchTokenEvent(query))

    def on_change_page(self, direction):
        if direction == "next" and self._current_page < len(self._paged_results) - 1:
            self._current_page += 1
            self._display_current_page()
        elif direction == "prev" and self._current_page > 0:
            self._current_page -= 1
            self._display_current_page()

    def event_handler(self, event):
        if isinstance(event, TokenSearchEvent):
            search_result = event.get_content()
            print(search_result)
            self._paged_results = list(MainView.chunk_list(search_result, 10))
            self._current_page = 0
            self._display_current_page()
        elif isinstance(event, URLSearchEvent):
            search_result = event.get_content()
            self._paged_results = list(MainView.chunk_list(search_result, 10))
            self._current_page = 0
            self._display_current_page()
        elif isinstance(event, DatabaseOpenEvent):
            print("DB connect success")
        elif isinstance(event, DatabaseCloseEvent):
            print("DB close success")

    def _display_current_page(self):
        if self._paged_results:
            current_page_results = self._paged_results[self._current_page]
            self.results_list.delete(0, tk.END)
            for index, info in enumerate(current_page_results, start=self._current_page * 10 + 1):
                result_display = f"{index}. Title: {info.get_title()} - URL: {info.get_url()}"
                self.results_list.insert(tk.END, result_display)
                result_display = f"    Describe: {info.get_first_sentence()}"
                self.results_list.insert(tk.END, result_display)
                self.results_list.insert(tk.END, "")

        else:
            self.results_list.delete(0, tk.END)
            self.results_list.insert(tk.END, "No results found.")

    @staticmethod
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


