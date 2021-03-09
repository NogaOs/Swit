class WitDirectoryNotFoundError(FileNotFoundError):
    """Failed to find a .wit directory."""

    pass


class CommitIdError(FileNotFoundError):
    """User input is not a branch name, nor a commit id."""

    pass


class ImpossibleMergeError(Exception):
    """The content of staging_area is not the same as the HEAD image."""

    pass
