class WitDirectoryNotFoundError(FileNotFoundError):
    """Failed to find a .swit directory."""

    pass


class CommitIdError(FileNotFoundError):
    """User input is not a branch name, nor a commit id."""

    pass


class CommitRequiredError(FileNotFoundError):
    """Cannot execute prior to first commit."""

    pass


class ImpossibleMergeError(Exception):
    """The content of staging_area is not the same as the HEAD image."""

    pass


class ImpossibleCheckoutError(Exception):
    """There must be no changes to be committed, not changes not staged for commit."""

    pass


class BranchNameExistsError(Exception):
    """Cannot create branch, as there is another branch with the same name."""

    pass
