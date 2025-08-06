class SemanticRouter:
    """Route queries to the right vector store based on topic/intent."""
    def __init__(self, stores):
        self.stores = stores  # Dict: domain -> vector store

    def route_query(self, query):
        # Simple routing: keyword-based, for demo
        if any(k in query.lower() for k in ["music", "song", "genre", "band"]):
            return self.stores["music"]
        elif any(k in query.lower() for k in ["law", "statute", "section", "case"]):
            return self.stores["law"]
        elif any(k in query.lower() for k in ["tcg", "card", "deck", "pokemon", "magic", "yugioh"]):
            return self.stores["tcg"]
        elif any(k in query.lower() for k in ["website", "html", "css", "react"]):
            return self.stores["web"]
        else:
            return self.stores["general"]

    def query(self, query):
        store = self.route_query(query)
        return store.query(query)