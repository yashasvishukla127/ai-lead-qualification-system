class ProviderError(Exception):
    """
    Raised by any provider when the API call fails.
    Wraps provider-specific exceptions into one common type.
    """
    def __init__(
        self,
        provider: str,
        error_type: str,
        detail: str,
        retryable: bool = False
    ):
        self.provider = provider
        self.error_type = error_type
        self.detail = detail
        self.retryable = retryable
        super().__init__(f"[{provider}] {error_type}: {detail}")