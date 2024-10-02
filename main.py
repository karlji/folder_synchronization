import argparse
import platform
import os


class FolderSync:
    def __init__(self, source, replica, interval, log_file):
        self.source = source
        self.replica = replica
        self.interval = interval
        self.log_file = log_file

    def start_sync_loop(self):
        self.sync()

    def sync(self):
        raise NotImplementedError("Subclasses must implement this method")


class WindowsFolderSync(FolderSync):
    def __init__(self, source, replica, interval, log_file):
        # Call the parent (FolderSync) constructor
        super().__init__(source, replica, interval, log_file)

    def sync(self):
        print(f"Syncing on Windows with source: {self.source} and replica: {self.replica}")


class LinuxFolderSync(FolderSync):
    def __init__(self, source, replica, interval, log_file):
        # Call the parent (FolderSync) constructor
        super().__init__(source, replica, interval, log_file)

    def sync(self):
        print(f"Syncing on Linux with source: {self.source} and replica: {self.replica}")


def parse_arguments():
    """
    Parses command-line arguments for source, replica, interval, and log file.
    """
    parser = argparse.ArgumentParser(description='Sync folders between source and replica.')

    parser.add_argument('--source', type=str, required=True, help='Path to the source folder.')
    parser.add_argument('--replica', type=str, required=True, help='Path to the replica folder.')
    parser.add_argument('--interval', type=int, required=True, help='Sync interval in seconds.')
    parser.add_argument('--log', type=str, required=True, help='Path to the log file.')

    return parser.parse_args()


def check_names(path):
    if os.path.exists(path):
        return path
    else:
        "fail"

def main():
    args = parse_arguments()

    source = check_names(args.source)
    replica = args.replica
    interval = args.interval
    log_file = args.log

    # Detect the OS platform
    current_os = platform.system()
    if current_os == "Windows":
        syncer = WindowsFolderSync(source, replica, interval, log_file)
    elif current_os == "Linux":
        syncer = LinuxFolderSync(source, replica, interval, log_file)
    else:
        print("Unsupported operating system. This script only supports Windows and Linux.")
        return

    # Start the sync process
    syncer.start_sync_loop()


if __name__ == "__main__":
    main()
