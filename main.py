import argparse
import platform
import os
import sys
import folder_sync as fs
from pathlib import Path


def _parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for source, replica, interval, and log file.

    Returns:
    - argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Sync folders between source and replica.')

    parser.add_argument('--source', type=str, required=True, help='Path to the source folder.')
    parser.add_argument('--replica', type=str, required=True, help='Path to the replica folder.')
    parser.add_argument('--log', type=str, required=True, help='Path to the log file or directory.')
    parser.add_argument('--interval', type=int, required=True, help='Sync interval in seconds. (1-86400)')
    parser.add_argument('--debug', action='store_true', help='Sets logging to debug level.')
    return parser.parse_args()


def _resolve_log_file(log_path_str: str) -> str:
    """
    Determines whether the log path is a file or directory.
    If it's a directory, a default log file name will be added.

    Parameters:
    - log_path_str (str): The log path provided by the user.

    Returns:
    - str: The resolved log file path.
    """
    log_path = Path(log_path_str)

    # Check if the path is clearly a file (has a file extension)
    if log_path.suffix:  # Suffix will return the file extension like '.log'
        _check_path(str(log_path.parent))  # Check parent directory for the log file
        return str(log_path)
    else:
        # If no file extension, treat it as a directory and append default log filename
        _check_path(str(log_path))  # Ensure the directory exists
        return str(log_path / "logfile.log")


def _check_path(path: str) -> str:
    """
    Checks whether provided directory path exists. If not, asks user to create new folder.

    Parameters:
    - path (str): Path to the directory to check.

    Returns:
    - str: Path of existing directory.
    """
    if not os.path.exists(path):
        print(f"Folder doesn't exist: {path}")
        while True:
            usr_input = input("Create new folder? (y/n): ").lower().strip()
            if usr_input == "y":
                Path(path).mkdir(parents=True)
                print(f"Created new folder: {path}")
            elif usr_input == "n":
                sys.exit()
            else:
                print("Wrong input. Please use y or n.")
                continue
            break
    return path


def _clamp(n: int, minn: int, maxn: int) -> int:
    """
    Clamps a value to be within a specified range.

    Parameters:
    - n (int): The value to clamp.
    - minn (int): Minimum allowed value.
    - maxn (int): Maximum allowed value.

    Returns:
    - int: The clamped value.
    """

    clamped = max(min(maxn, n), minn)
    if clamped != n:
        print(f'The argument value {n} was clamped to {clamped}')
    return clamped


def main():
    args = _parse_arguments()

    #Checking parsed arguments
    try:
        source = _check_path(args.source)
        replica = _check_path(args.replica)
        log_file = _resolve_log_file(args.log)

    except PermissionError as e:
        print(f"Permission error: {e}")
        sys.exit(1)
    interval = _clamp(args.interval, 1, 86400)

    # Detect the OS platform
    current_os = platform.system()
    if current_os not in ["Windows", "Linux"]:
        print(f"Unsupported operating system: {current_os}. This script supports only Windows and Linux.")
        sys.exit(1)

    # Start the sync process
    syncer = fs.FolderSync(source, replica, log_file, interval, args.debug)
    syncer.start_sync_loop()


if __name__ == "__main__":
    main()
