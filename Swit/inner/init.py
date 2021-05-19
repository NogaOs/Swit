from pathlib import Path
from typing import Tuple

from loguru import logger

from Swit.common.paths import cwd


def create_init_files(repo_path: Path, sub_directory_names: Tuple[str, str]) -> None:
    """Creates a `.swit` directory in the current working directory; 
    under it, creates empty dirs `images` and `staging_area`.
    """
    pathz = [repo_path]
    pathz.extend((repo_path / name) for name in sub_directory_names)
    for path in pathz:
        path.mkdir(exist_ok=False)


def create_activated_file(
    repo_path: Path, file_name: str = "activated.txt", content: str = "master"
) -> None:
    """Creates a file named `activated.txt`, that contains the name of the active branch."""
    activated_path = repo_path / file_name
    activated_path.write_text(content)


def inner_init(main_directory_name: str, sub_directory_names: Tuple[str, str]) -> None:
    """Creates a swit repository, containing `staging_area`, `images`, and `activated.txt`. """
    repo_path = cwd / main_directory_name
    create_init_files(repo_path, sub_directory_names)
    create_activated_file(repo_path)


def init() -> bool:
    try:
        inner_init(".swit", ("images", "staging_area"))
    except FileExistsError:
        logger.warning("Cannot initiate a repository inside of another repository.")
        return False
    logger.info(">>> All folders were created.")
    return True
