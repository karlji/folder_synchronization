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