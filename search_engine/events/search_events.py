# events/search_events.py


class SearchInitiatedEvent:
    """
    Triggered when the user initiates a search action. This event is sent from the UI to the engine to perform a search based on the user's query.
    """
    pass

class DisplaySearchResultsEvent:
    """
    Sent from the engine to the UI to display the search results. This event carries the results data and possibly pagination information.
    """
    pass

class SearchDetailsRequestedEvent:
    """
    Triggered when the user requests to see the details of a specific search result. The engine should handle this event to provide detailed information for the specified result.
    """
    pass

class ChangePageEvent:
    """
    Triggered when the user requests to change the search results page (next or previous). The engine should handle this event to update the results displayed based on the new page number.
    """
    pass
