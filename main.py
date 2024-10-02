import argparse
import platform
import os
import sys


class FolderSync:
    def __init__(self, source, replica, log_file, interval,):
        self.source = source
        self.replica = replica
        self.log_file = log_file
        self.interval = interval

    def start_sync_loop(self):
        self.sync()

    def sync(self):
        raise NotImplementedError("Subclasses must implement this method")


class WindowsFolderSync(FolderSync):
    def __init__(self, source, replica, log_file, interval):
        # Call the parent (FolderSync) constructor
        super().__init__(source, replica, log_file, interval)

    def sync(self):
        print(f"Syncing on Windows with source: {self.source} and replica: {self.replica}")


class LinuxFolderSync(FolderSync):
    def __init__(self, source, replica, log_file, interval):
        # Call the parent (FolderSync) constructor
        super().__init__(source, replica, log_file, interval)

    def sync(self):
        print(f"Syncing on Linux with source: {self.source} and replica: {self.replica}")

def parse_arguments():
    """
    Parses command-line arguments for source, replica, interval, and log file.
    """
    parser = argparse.ArgumentParser(description='Sync folders between source and replica.')

    parser.add_argument('--source', type=str, required=True, help='Path to the source folder.')
    parser.add_argument('--replica', type=str, required=True, help='Path to the replica folder.')
    parser.add_argument('--log', type=str, required=True, help='Path to the log file.')
    parser.add_argument('--interval', type=int, required=True, help='Sync interval in seconds.')

    return parser.parse_args()


def check_path(path):
    """
    Checks whether provided directory path exists. If not, asks user to create new folder.
    """
    path = path + "_new3"
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

def main():
    args = parse_arguments()

    source = check_path(args.source)
    replica = check_path(args.replica)
    log_file = check_path(args.log)
    interval = args.interval

    # Detect the OS platform
    current_os = platform.system()
    if current_os == "Windows":
        syncer = WindowsFolderSync(source, replica, log_file, interval)
    elif current_os == "Linux":
        syncer = LinuxFolderSync(source, replica, log_file, interval)
    else:
        print("Unsupported operating system. This script only supports Windows and Linux.")
        return

    # Start the sync process
    syncer.start_sync_loop()

if __name__ == "__main__":
    main()
