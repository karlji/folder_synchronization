import logging
import time


class FolderSync:
    def __init__(self, source: str, replica: str, log_file: str, interval: int):
        """
         __init__

        Parameters:
        - source (str): Path to the source folder.
        - replica (str): Path to the replica folder.
        - log_file (str): Path to the log folder.
        - interval (int): Sync interval in seconds.

        Returns:
        - void
        """
        self.source = source
        self.replica = replica
        self.log_file = log_file
        self.interval = interval
        self.logger = None
        self.setup_logging()

    def setup_logging(self):
        """
         Sets up logging to both the console and a log file.

        Parameters:
        - self

        Returns:
        - void
        """
        self.logger = logging.getLogger("FolderSyncLogger")
        self.logger.setLevel(logging.INFO)
        # Create handlers for both file and console logging
        file_handler = logging.FileHandler(self.log_file)
        console_handler = logging.StreamHandler()
        # Set log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def start_sync_loop(self):
        """
        Starts the periodic sync loop based on the interval provided.

        Parameters:
        - self

        Returns:
        - void
        """
        self.logger.info(f"Starting sync loop. Syncing every {self.interval} seconds.")
        while True:
            self.sync()
            self.logger.info(f"Waiting {self.interval} seconds before the next sync.")
            time.sleep(self.interval)

    def sync(self):
        raise NotImplementedError("Subclasses must implement this method")


class WindowsFolderSync(FolderSync):
    def __init__(self, source: str, replica: str, log_file: str, interval: int):
        # Call the parent (FolderSync) constructor
        super().__init__(source, replica, log_file, interval)

    def sync(self):
        print(f"Syncing on Windows with source: {self.source} and replica: {self.replica}")


class LinuxFolderSync(FolderSync):
    def __init__(self, source: str, replica: str, log_file: str, interval: int):
        # Call the parent (FolderSync) constructor
        super().__init__(source, replica, log_file, interval)

    def sync(self):
        print(f"Syncing on Linux with source: {self.source} and replica: {self.replica}")
