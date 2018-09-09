class ItemUI:
    def __init__(self, item):
        self.id = item.id
        self.name = item.name
        self.description = item.description
        self.category_id = item.category_id
        self.done = item.done

    def set_resources(self, resources):
        self.resources = resources
