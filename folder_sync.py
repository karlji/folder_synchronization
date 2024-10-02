import logging
import pathlib
import time
from pathlib import Path
import hashlib
import shutil


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
                self._compare_files(src_path, dest_path)
            elif src_path.is_dir() and not dest_path.exists():
                # Create directories that don't exist in replica
                dest_path.mkdir(parents=True)
                self.logger.info(f"Created directory: {dest_path}")

    def _compare_files(self, src_file: pathlib.Path, dest_file: pathlib.Path):
        """
        Compares two files by their hashes, and if they differ, copies the source file to the replica.

        Parameters:
        - self
        - src_file (str): Source file path for comparison
        - dest_file (str): Replica file path for comparison

        Returns:
        - void
        """
        if not dest_file.exists():
            self.logger.debug(f"File missing {dest_file}.")
            self._copy_file(src_file, dest_file)
        elif self._compute_hash(src_file) != self._compute_hash(dest_file):
            self.logger.debug(f"File changed {src_file}.")
            self._copy_file(src_file, dest_file)
        else:
            self.logger.debug(f"No changes in {src_file}. Skipping copy.")

    @staticmethod
    def _compute_hash(file_path: pathlib.Path) -> str:
        """
        Computes the MD5 hash of a file for integrity checking.

        Parameters:
        - file_path (pathlib.Path): Path to input file for hash calculation.

        Returns:
        - str: Calculated hash value.
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _copy_file(self,src_file: pathlib.Path, dest_file: pathlib.Path, max_retries: int = 3, attempt: int = 1):
        """
        Copies a file from source to destination, and logs the action.

        Parameters:
        - src_file (pathlib.Path): Source file path to copy.
        - dest_file (pathlib.Path): Destination file path to copy to.
        - max_retries (int): Maximum number of retries allowed if the file copy fails.
        - attempt (int): Current attempt count for the copy process.

        Returns:
        - void
        """
        self.logger.info(f"Copying file: {src_file} to: {dest_file}")
        try:
            shutil.copy2(src_file, dest_file)
            # Checking hash after copy to ensure integrity
            if self._compute_hash(src_file) == self._compute_hash(dest_file):
                self.logger.info(f"File copied and hash integrity verified for {src_file}")
            else:
                raise ValueError(f"Hash mismatch after copying {src_file} to {dest_file}")

        except Exception as e:
            # Log the failure and attempt retry if below max_retries
            self.logger.error(f"Error copying file: {e}")

            if attempt < max_retries:
                self.logger.info(f"Retrying file copy: {src_file} (Attempt {attempt + 1}/{max_retries})")
                self._copy_file(src_file, dest_file, max_retries, attempt + 1)
            else:
                self.logger.error(f"Failed to copy {src_file} after {max_retries} attempts. Skipping file.")

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