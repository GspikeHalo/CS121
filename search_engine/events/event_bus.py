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
        result_event = self._engine.process_event(event)
        self._view.event_handler(result_event)
