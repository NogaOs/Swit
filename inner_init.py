from pathlib import Path

from typing import Tuple

from paths import cwd


def create_init_files(repo_path: Path, sub_directory_names: Tuple[str, str]) -> None:
    """Creates a `.wit` directory in the current working directory; under it, creates empty dirs `images` and `staging_area`."""
    pathz = [repo_path]
    pathz.extend((repo_path / name) for name in sub_directory_names)
    for path in pathz:
        path.mkdir(exist_ok=False)


def create_activated_file(
    repo_path: Path, file_name="activated.txt", content="master"
) -> None:
    """Creates a file named `activated.txt`, that contains the name of the active branch."""
    activated_path = repo_path / file_name
    with open(activated_path, "w") as f:
        f.write(content)


def inner_init(main_directory_name: str, sub_directory_names: Tuple[str, str]) -> None:
    repo_path = cwd / main_directory_name
    create_init_files(repo_path, sub_directory_names)
    create_activated_file(repo_path)