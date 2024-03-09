from search_engine.events.event_bus import EventBus
from search_engine.engine.main import Engine
from search_engine.views.main import MainView


def main():
    event_bus = EventBus()
    engine = Engine()
    main_view = MainView(event_bus)
    event_bus.set_engine(engine)
    event_bus.set_view(main_view)
    main_view.set_db("./")
    main_view.run()


if __name__ == '__main__':
    main()
