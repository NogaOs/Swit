class WitDirectoryNotFoundError(FileNotFoundError):
    """Failed to find a .wit directory."""

    pass


class CommitIdError(FileNotFoundError):
    """User input is not a branch name, nor a commit id."""

    pass


class ImpossibleStatusError(FileNotFoundError):
    """Must commit at least once before checking status."""

    pass


class ImpossibleMergeError(Exception):
    """The content of staging_area is not the same as the HEAD image."""

    pass


class ImpossibleCheckoutError(Exception):
    """There must be no changes to be committed, not changes not staged for commit."""

    pass
