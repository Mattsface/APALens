class HttpAdapterException(Exception):
    """
    Exception raised for errors in the HTTP adapter.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
