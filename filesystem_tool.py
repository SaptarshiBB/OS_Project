import os
import shutil
import time
import pickle
import random

class FileSystem:
    def __init__(self):
        self.current_dir = os.getcwd()  # Start in the current working directory
        self.journal_file = os.path.join(self.current_dir, "filesystem_journal.log")
        self.backup_dir = os.path.join(self.current_dir, "backup")
        self.cache = {}  # Cache for faster file access
        self.load_journal()
        self.create_backup_dir()

    def create_backup_dir(self):
        """Create a backup directory if it doesn't exist."""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def load_journal(self):
        """Load the journal file to recover from a crash."""
        if os.path.exists(self.journal_file):
            with open(self.journal_file, "rb") as f:
                self.cache = pickle.load(f)
            print("Recovered from journal file.")
        else:
            self.cache = {}

    def save_journal(self):
        """Save the current state to the journal file."""
        with open(self.journal_file, "wb") as f:
            pickle.dump(self.cache, f)

    def create_file(self, name, content):
        """Create a file with the given content."""
        file_path = os.path.join(self.current_dir, name)
        with open(file_path, "w") as f:
            f.write(content)
        self.cache[file_path] = content  # Add to cache
        self.save_journal()  # Update journal
        self.backup_file(file_path)  # Create backup
        print(f"File '{name}' created in '{self.current_dir}'.")

    def read_file(self, name):
        """Read the content of a file."""
        file_path = os.path.join(self.current_dir, name)
        if file_path in self.cache:  # Check cache first
            print("Reading from cache...")
            return self.cache[file_path]
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{name}' not found in '{self.current_dir}'.")
        with open(file_path, "r") as f:
            content = f.read()
        self.cache[file_path] = content  # Add to cache
        self.save_journal()  # Update journal
        return content

    def delete_file(self, name):
        """Delete a file."""
        file_path = os.path.join(self.current_dir, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{name}' not found in '{self.current_dir}'.")
        os.remove(file_path)
        if file_path in self.cache:
            del self.cache[file_path]  # Remove from cache
        self.save_journal()  # Update journal
        print(f"File '{name}' deleted from '{self.current_dir}'.")

    def create_directory(self, name):
        """Create a new directory in the current directory."""
        dir_path = os.path.join(self.current_dir, name)
        os.makedirs(dir_path, exist_ok=True)
        print(f"Directory '{name}' created in '{self.current_dir}'.")

    def delete_directory(self, name):
        """Delete a directory."""
        dir_path = os.path.join(self.current_dir, name)
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory '{name}' not found in '{self.current_dir}'.")
        shutil.rmtree(dir_path)
        print(f"Directory '{name}' deleted from '{self.current_dir}'.")

    def rename_file_or_folder(self, old_name, new_name):
        """Rename a file or folder."""
        old_path = os.path.join(self.current_dir, old_name)
        new_path = os.path.join(self.current_dir, new_name)
        if not os.path.exists(old_path):
            raise FileNotFoundError(f"'{old_name}' not found in '{self.current_dir}'.")
        os.rename(old_path, new_path)
        if old_path in self.cache:
            self.cache[new_path] = self.cache.pop(old_path)  # Update cache
        self.save_journal()  # Update journal
        self.backup_file(new_path)  # Create backup
        print(f"Renamed '{old_name}' to '{new_name}' in '{self.current_dir}'.")

    def move_file_or_folder(self, name, destination):
        """Move a file or folder to a new location."""
        source_path = os.path.join(self.current_dir, name)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"'{name}' not found in '{self.current_dir}'.")
        shutil.move(source_path, destination)
        if source_path in self.cache:
            del self.cache[source_path]  # Remove from cache
        self.save_journal()  # Update journal
        print(f"Moved '{name}' to '{destination}'.")

    def copy_file_or_folder(self, name, destination):
        """Copy a file or folder to a new location."""
        source_path = os.path.join(self.current_dir, name)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"'{name}' not found in '{self.current_dir}'.")
        if os.path.isdir(source_path):
            shutil.copytree(source_path, os.path.join(destination, name))
        else:
            shutil.copy2(source_path, destination)
        print(f"Copied '{name}' to '{destination}'.")

    def list_files_and_folders(self):
        """List all files and directories in the current directory."""
        return os.listdir(self.current_dir)

    def change_directory(self, path):
        """Change the current directory."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory '{path}' not found.")
        if not os.path.isdir(path):
            raise NotADirectoryError(f"'{path}' is not a directory.")
        self.current_dir = path
        print(f"Changed to directory '{self.current_dir}'.")

    def backup_file(self, file_path):
        """Backup a file to the backup directory."""
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        print(f"Backup created for '{file_path}'.")

    def restore_file(self, name):
        """Restore a file from the backup directory."""
        backup_path = os.path.join(self.backup_dir, name)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup for '{name}' not found.")
        shutil.copy2(backup_path, os.path.join(self.current_dir, name))
        print(f"File '{name}' restored from backup.")

    def corrupt_file(self, name):
        """Simulate file corruption by overwriting with random data."""
        file_path = os.path.join(self.current_dir, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{name}' not found in '{self.current_dir}'.")
        with open(file_path, "wb") as f:
            f.write(os.urandom(100))  # Overwrite with 100 random bytes
        print(f"File '{name}' corrupted.")

    def simulate_crash(self):
        """Simulate a disk crash by deleting the journal file."""
        if os.path.exists(self.journal_file):
            os.remove(self.journal_file)
            print("Simulated disk crash: Journal file deleted.")
        else:
            print("No journal file found to simulate a crash.")

    def defragment(self):
        """Defragment the current directory to optimize file storage."""
        print("Defragmenting... This may take a while.")
        time.sleep(2)  # Simulate defragmentation process
        print("Defragmentation complete.")

# Main Function
def main():
    fs = FileSystem()

    while True:
        print("\nFile System Menu:")
        print("1. Create File")
        print("2. Read File")
        print("3. Delete File")
        print("4. Create Directory")
        print("5. Delete Directory")
        print("6. Rename File/Folder")
        print("7. Move File/Folder")
        print("8. Copy File/Folder")
        print("9. List Files/Folders")
        print("10. Change Directory")
        print("11. Simulate Disk Crash")
        print("12. Defragment")
        print("13. Corrupt File")
        print("14. Restore File from Backup")
        print("15. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter file name: ")
            content = input("Enter file content: ")
            fs.create_file(name, content)

        elif choice == "2":
            name = input("Enter file name: ")
            try:
                content = fs.read_file(name)
                print(f"File content: {content}")
            except FileNotFoundError as e:
                print(e)

        elif choice == "3":
            name = input("Enter file name: ")
            try:
                fs.delete_file(name)
            except FileNotFoundError as e:
                print(e)

        elif choice == "4":
            name = input("Enter directory name: ")
            fs.create_directory(name)

        elif choice == "5":
            name = input("Enter directory name: ")
            try:
                fs.delete_directory(name)
            except FileNotFoundError as e:
                print(e)

        elif choice == "6":
            old_name = input("Enter current name of file/folder: ")
            new_name = input("Enter new name of file/folder: ")
            try:
                fs.rename_file_or_folder(old_name, new_name)
            except FileNotFoundError as e:
                print(e)

        elif choice == "7":
            name = input("Enter name of file/folder to move: ")
            destination = input("Enter destination path: ")
            try:
                fs.move_file_or_folder(name, destination)
            except FileNotFoundError as e:
                print(e)

        elif choice == "8":
            name = input("Enter name of file/folder to copy: ")
            destination = input("Enter destination path: ")
            try:
                fs.copy_file_or_folder(name, destination)
            except FileNotFoundError as e:
                print(e)

        elif choice == "9":
            files = fs.list_files_and_folders()
            print(f"Files/Folders in '{fs.current_dir}': {files}")

        elif choice == "10":
            path = input("Enter directory path: ")
            try:
                fs.change_directory(path)
            except (FileNotFoundError, NotADirectoryError) as e:
                print(e)

        elif choice == "11":
            fs.simulate_crash()

        elif choice == "12":
            fs.defragment()

        elif choice == "13":
            name = input("Enter file name to corrupt: ")
            try:
                fs.corrupt_file(name)
            except FileNotFoundError as e:
                print(e)

        elif choice == "14":
            name = input("Enter file name to restore: ")
            try:
                fs.restore_file(name)
            except FileNotFoundError as e:
                print(e)

        elif choice == "15":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()