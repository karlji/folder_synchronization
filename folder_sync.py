import logging
import time
from pathlib import Path

class FolderSync():
    def __init__(self, source: str, replica: str, log_file: str, interval: int, debug: bool):
        """
         __init__

        Parameters:
        - source (str): Path to the source folder.
        - replica (str): Path to the replica folder.
        - log_file (str): Path to the log folder.
        - interval (int): Sync interval in seconds.
        - debug (bool): (optional) Sets logging to debug level.

        Returns:
        - void
        """
        self.source = Path(source)
        self.replica = Path(replica)
        self.log_file = log_file
        self.interval = interval
        self.debug = debug
        self.logger = None
        self._setup_logging()


    def _setup_logging(self):
        """
         Sets up logging to both the console and a log file.

        Returns:
        - void
        """
        self.logger = logging.getLogger("FolderSyncLogger")
        self.logger.setLevel(logging.INFO)
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
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

    def _sync_dirs(self):
        """
         Loops through source folders/files and calls compare_and_copy method.

        Parameters:
        - self

        Returns:
        - void
        """
        self.logger.info("Starting sync.")
        for src_path in self.source.rglob('*'):
            relative_path = src_path.relative_to(self.source)
            dest_path = self.replica / relative_path

            if src_path.is_file():
                # Compare and copy files
                self._compare_and_copy(src_path, dest_path)
            elif src_path.is_dir() and not dest_path.exists():
                # Create directories that don't exist in replica
                dest_path.mkdir(parents=True)
                self.logger.info(f"Created directory: {dest_path}")

    def _compare_and_copy(self, src_file: str, dest_file: str):
        pass

    def start_sync_loop(self):
        """
        Starts the periodic sync loop based on the interval provided.

        Returns:
        - void
        """
        self.logger.info(f"Starting sync loop. Syncing every {self.interval} seconds.")
        while True:
            self._sync_dirs()
            self.logger.debug(f"Waiting {self.interval} seconds before the next sync.")
            time.sleep(self.interval)