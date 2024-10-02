import argparse
import platform
import os
import sys
import folder_sync as fs

def _parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for source, replica, interval, and log file.

    Parameters:

    Returns:
    - argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Sync folders between source and replica.')

    parser.add_argument('--source', type=str, required=True, help='Path to the source folder.')
    parser.add_argument('--replica', type=str, required=True, help='Path to the replica folder.')
    parser.add_argument('--log', type=str, required=True, help='Path to the log file.')
    parser.add_argument('--interval', type=int, required=True, help='Sync interval in seconds. (1-86400)')
    parser.add_argument('--debug', type=bool, required=False, help='Sets logging to debug level (true/false)')
    return parser.parse_args()


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
                os.mkdir(path)
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
    debug = False

    #Checking parsed arguments
    source = _check_path(args.source)
    replica = _check_path(args.replica)
    log_file = _check_path(args.log) + "\\logfile.log"
    interval = _clamp(args.interval,1,86400)
    if args.debug:
        debug = True

    # Detect the OS platform and create syncer object
    current_os = platform.system()
    if current_os == "Windows" or current_os == "Linux":
        syncer = fs.FolderSync(source, replica, log_file, interval, debug)
    else:
        print("Unsupported operating system. This script only supports Windows and Linux.")
        return

    # Start the sync process
    syncer.start_sync_loop()

if __name__ == "__main__":
    main()
