from search_engine.events.event_bus import EventBus
# from search_engine.engine.search_engine import SearchEngine  # 假设搜索引擎类是这样的,后续根据实际情况修改
from search_engine.views.main import MainView

def main():
    # 初始化事件总线
    event_bus = EventBus()

    # 初始化搜索引擎，并注册到事件总线 #只是示例，后续根据实际情况修改
    # engine = SearchEngine()
    # event_bus.set_engine(engine)

    # 初始化视图，并注册到事件总线
    main_view = MainView(event_bus)
    event_bus.set_view(main_view)

    # 启动UI事件循环
    main_view.mainloop()

if __name__ == '__main__':
    main()
