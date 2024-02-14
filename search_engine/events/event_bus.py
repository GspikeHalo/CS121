#  search_engine/events/event_bus.py

class EventBus:
    def __init__(self):
        self._view = None
        self._engine = None

    def set_view(self, view):
        self._view = view

    def set_engine(self, engine):
        self._engine = engine

    def initiate_event(self, event):
        if hasattr(event, "_INTERNAL"):
            # view内部处理
            pass
        else:
            # 进入engine处理
            pass
