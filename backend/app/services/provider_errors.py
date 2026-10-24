"""Expected, classified provider failures; raw upstream details remain private."""


class ProviderError(Exception):
    def __init__(self, message: str = "The provider could not produce a candidate.", *, reason: str = "provider_error"):
        self.reason = reason
        super().__init__(message)
