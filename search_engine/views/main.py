# views/main.py

import tkinter as tk
from tkinter import messagebox
from search_engine.events.search_events import SearchInitiatedEvent, SearchDetailsRequestedEvent, \
    ChangePageEvent


class MainView(tk.Tk):
    def __init__(self, event_bus):
        super().__init__()
        self.event_bus = event_bus
        self.event_bus.set_view(self)  # 注册当前视图到事件总线

        # 设置窗口标题
        self.title("Search Engine")

        # 设置窗口的初始大小
        self.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        """
        创建并布局UI组件。
        """
        # 创建搜索框和搜索按钮的容器
        self.search_frame = tk.Frame(self)
        self.search_frame.pack(fill = tk.X, padx = 5, pady = 5)

        # 搜索输入框，让用户可以输入搜索关键词
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side = tk.LEFT, expand = True, fill = tk.X, padx = 5)

        # 搜索按钮，用户点击后触发搜索操作
        self.search_button = tk.Button(self.search_frame, text = "Search", command = self.on_search)
        self.search_button.pack(side = tk.LEFT, padx = 5)

        # 搜索结果列表的容器，展示搜索结果
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(fill = tk.BOTH, expand = True, pady = 5)

        # 搜索结果列表，展示搜索结果摘要信息
        self.results_list = tk.Listbox(self.results_frame)
        self.results_list.pack(side = tk.LEFT, fill = tk.BOTH, expand = True, padx = 5, pady = 5)

        # 详情查看和分页控制的容器
        self.detail_frame = tk.Frame(self)
        self.detail_frame.pack(fill = tk.X, padx = 5, pady = 5)

        # 详细信息查看输入框，用户输入结果编号查看详情
        self.detail_entry = tk.Entry(self.detail_frame, width = 5)
        self.detail_entry.pack(side = tk.LEFT, padx = 5)

        # 显示详细信息的按钮
        self.detail_button = tk.Button(self.detail_frame, text = "Show Detail",
                                       command = self.on_show_detail)
        self.detail_button.pack(side = tk.LEFT, padx = 5)

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
        self.event_bus.initiate_event(SearchInitiatedEvent(query))

    def on_show_detail(self):
        """
        处理显示详细信息按钮点击事件，请求显示选定搜索结果的详情。
        """
        try:
            index = int(self.detail_entry.get()) - 1
            self.event_bus.initiate_event(SearchDetailsRequestedEvent(index))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid result number.")

    def on_change_page(self, direction):
        """
        处理分页按钮点击事件，请求翻页。
        """
        self.event_bus.initiate_event(ChangePageEvent(direction))

    # 可能需要的其他方法，比如更新UI显示搜索结果