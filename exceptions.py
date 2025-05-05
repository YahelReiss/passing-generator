class ExcitedSiteswapError(Exception):
    """Exception raised when the siteswap is 'excited' and calculation cannot proceed."""

    def __init__(
        self,
        message="The siteswap pattern is excited and cannot be calculated without more information.",
    ):
        self.message = message
        super().__init__(self.message)


class NotValidSiteswapError(Exception):
    """Exception raised when a non-valid siteswap is given."""

    def __init__(self, message="this siteswap is not valid"):
        self.message = message
        super().__init__(self.message)
