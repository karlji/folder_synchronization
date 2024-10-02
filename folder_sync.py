import logging
import pathlib
import time
from pathlib import Path
import hashlib
import shutil
import os

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

    def _sync_folders(self):
        """
         Logs start and finish of sync and calls _sync_source, _sync_replica

        Returns:
        - void
        """
        self.logger.info("Starting sync.")
        self._sync_source()
        self._sync_replica()
        self.logger.info("Finished sync.")

    def _sync_source(self):
        """
         Loops through source folders/files and calls _compare_files method.

        Returns:
        - void
        """
        try:
            for src_path in self.source.rglob('*'):
                relative_path = src_path.relative_to(self.source)
                dest_path = self.replica / relative_path

                if src_path.is_file():
                    # Compare and copy files from source to replica
                    self._compare_files(src_path, dest_path)
                elif src_path.is_dir() and not dest_path.exists():
                    # Create directories that don't exist in replica
                    dest_path.mkdir(parents=True)
                    self.logger.info(f"Created directory: {dest_path}")
        except FileNotFoundError as e:
            self.logger.error(f"Source folder or file not found: {e}")
            return
        except PermissionError as e:
            self.logger.error(f"Permission denied: {e}")
            return

    def _sync_replica(self):
        """
         Loops through replica folders/files and removes excessive ones.

        Returns:
        - void
        """
        try:
            for rep_path in self.replica.rglob('*'):
                relative_path = rep_path.relative_to(self.replica)
                src_path = self.source / relative_path

                # if file/folder exists in source, skip to next
                if src_path.exists():
                    continue
                if rep_path.is_dir():
                    shutil.rmtree(rep_path)
                    self.logger.info(f"Deleted directory: {rep_path}")
                else:
                    os.remove(rep_path)
                    self.logger.info(f"Deleted file: {rep_path}")
        except FileNotFoundError as e:
            self.logger.error(f"Source folder or file not found: {e}")
            return
        except PermissionError as e:
            self.logger.error(f"Permission denied: {e}")
            return

    def _compare_files(self, src_file: pathlib.Path, dest_file: pathlib.Path):
        """
        Compares two files by their hashes, and if they differ, copies the source file to the replica.

        Parameters:
        - src_file (str): Source file path for comparison
        - dest_file (str): Replica file path for comparison

        Returns:
        - void
        """

        if dest_file.exists():
            # File size or timestamp changed, check hash
            if src_file.stat().st_mtime != dest_file.stat().st_mtime or src_file.stat().st_size != dest_file.stat().st_size:
                # Hash changed, copy
                if self._compute_hash(src_file) != self._compute_hash(dest_file):
                    self.logger.debug(f"File changed {src_file}.")
                    self._copy_file(src_file, dest_file)
                else:
                    self.logger.debug(f"Hash unchanged{src_file}. Skipping copy.")
            else:
                self.logger.debug(f"No changes in {src_file}. Skipping copy.")
        # File doesn't exist, copy
        else:
            self.logger.debug(f"File missing {dest_file}.")
            self._copy_file(src_file, dest_file)


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
            self.logger.error(f"Error copying file: {e}. Attempt: {attempt}")

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
        try:
            while True:
                self._sync_folders()
                self.logger.debug(f"Waiting {self.interval} seconds before the next sync.")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            self.logger.info("Sync process interrupted. Shutting down.")