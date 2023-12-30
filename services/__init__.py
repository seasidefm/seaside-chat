class Services:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Services, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass
