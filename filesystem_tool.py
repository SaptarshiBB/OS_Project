import os
import shutil
import time
import pickle
import random
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, simpledialog
import subprocess
import platform

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
            try:
                with open(self.journal_file, "rb") as f:
                    self.cache = pickle.load(f)
                print("Recovered from journal file.")
            except (pickle.PickleError, EOFError):
                print("Journal file corrupted, starting fresh.")
                self.cache = {}
        else:
            self.cache = {}

    def save_journal(self):
        """Save the current state to the journal file."""
        with open(self.journal_file, "wb") as f:
            pickle.dump(self.cache, f)

    def create_file(self, name, content):
        """Create a file with the given content."""
        file_path = os.path.join(self.current_dir, name)
        try:
            with open(file_path, "w") as f:
                f.write(content)
            self.cache[file_path] = content
            self.save_journal()
            self.backup_file(file_path)
            print(f"File '{name}' created in '{self.current_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error creating file: {e}")
            return False

    def delete_file(self, name):
        """Delete a file."""
        file_path = os.path.join(self.current_dir, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{name}' not found in '{self.current_dir}'.")
        try:
            os.remove(file_path)
            if file_path in self.cache:
                del self.cache[file_path]
            self.save_journal()
            print(f"File '{name}' deleted from '{self.current_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error deleting file: {e}")
            return False

    def create_directory(self, name):
        """Create a new directory in the current directory."""
        dir_path = os.path.join(self.current_dir, name)
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Directory '{name}' created in '{self.current_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error creating directory: {e}")
            return False

    def delete_directory(self, name):
        """Delete a directory and its contents."""
        dir_path = os.path.join(self.current_dir, name)
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory '{name}' not found in '{self.current_dir}'.")
        try:
            shutil.rmtree(dir_path)
            # Remove any cached files from this directory
            for cached_path in list(self.cache.keys()):
                if cached_path.startswith(dir_path):
                    del self.cache[cached_path]
            self.save_journal()
            print(f"Directory '{name}' deleted from '{self.current_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error deleting directory: {e}")
            return False

    def rename_file_or_folder(self, old_name, new_name):
        """Rename a file or folder with proper path handling."""
        old_path = os.path.join(self.current_dir, old_name)
        new_path = os.path.join(self.current_dir, new_name)
        
        if not os.path.exists(old_path):
            raise FileNotFoundError(f"'{old_name}' not found in '{self.current_dir}'.")
        if os.path.exists(new_path):
            raise FileExistsError(f"'{new_name}' already exists in '{self.current_dir}'.")
        
        try:
            os.rename(old_path, new_path)
            # Update cache if the old path was cached
            if old_path in self.cache:
                self.cache[new_path] = self.cache.pop(old_path)
            self.save_journal()
            self.backup_file(new_path)
            print(f"Renamed '{old_name}' to '{new_name}' in '{self.current_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error renaming: {e}")
            return False

    def move_file_or_folder(self, name, destination):
        """Move a file or folder to a new location with proper path handling."""
        source_path = os.path.join(self.current_dir, name)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"'{name}' not found in '{self.current_dir}'.")
        
        dest_path = os.path.join(destination, name)
        if os.path.exists(dest_path):
            raise FileExistsError(f"'{name}' already exists in destination.")
        
        try:
            shutil.move(source_path, destination)
            if source_path in self.cache:
                del self.cache[source_path]
            self.save_journal()
            print(f"Moved '{name}' to '{destination}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error moving: {e}")
            return False

    def copy_file_or_folder(self, name, destination):
        """Copy a file or folder to a new location."""
        source_path = os.path.join(self.current_dir, name)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"'{name}' not found in '{self.current_dir}'.")
        
        dest_path = os.path.join(destination, name)
        if os.path.exists(dest_path):
            raise FileExistsError(f"'{name}' already exists in destination.")
        
        try:
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
            print(f"Copied '{name}' to '{destination}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error copying: {e}")
            return False

    def list_files_and_folders(self):
        """List all files and directories in the current directory."""
        try:
            return os.listdir(self.current_dir)
        except (IOError, OSError) as e:
            print(f"Error listing directory: {e}")
            return []

    def change_directory(self, path):
        """Change the current directory with proper validation."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory '{path}' not found.")
        if not os.path.isdir(path):
            raise NotADirectoryError(f"'{path}' is not a directory.")
        try:
            self.current_dir = os.path.abspath(path)
            print(f"Changed to directory '{self.current_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error changing directory: {e}")
            return False

    def backup_file(self, file_path):
        """Backup a file to the backup directory."""
        try:
            backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"Backup created for '{file_path}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error creating backup: {e}")
            return False

    def restore_file(self, name):
        """Restore a file from the backup directory."""
        backup_path = os.path.join(self.backup_dir, name)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup for '{name}' not found.")
        try:
            restore_path = os.path.join(self.current_dir, name)
            shutil.copy2(backup_path, restore_path)
            # Update cache
            with open(restore_path, "r") as f:
                self.cache[restore_path] = f.read()
            self.save_journal()
            print(f"File '{name}' restored from backup.")
            return True
        except (IOError, OSError) as e:
            print(f"Error restoring file: {e}")
            return False

    def corrupt_file(self, name):
        """Simulate file corruption by overwriting with random data."""
        file_path = os.path.join(self.current_dir, name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{name}' not found in '{self.current_dir}'.")
        try:
            with open(file_path, "wb") as f:
                f.write(os.urandom(100))  # Overwrite with 100 random bytes
            if file_path in self.cache:
                del self.cache[file_path]
            self.save_journal()
            print(f"File '{name}' corrupted.")
            return True
        except (IOError, OSError) as e:
            print(f"Error corrupting file: {e}")
            return False

    def simulate_crash(self):
        """Simulate a disk crash by deleting the journal file."""
        try:
            if os.path.exists(self.journal_file):
                os.remove(self.journal_file)
                print("Simulated disk crash: Journal file deleted.")
                return True
            else:
                print("No journal file found to simulate a crash.")
                return False
        except (IOError, OSError) as e:
            print(f"Error simulating crash: {e}")
            return False

    def defragment(self):
        """Simulate defragmentation (real defrag would require admin rights)."""
        print("Defragmenting... This may take a while.")
        try:
            # In a real implementation, we would call system defrag tools here
            # This is just a simulation
            time.sleep(2)
            print("Defragmentation complete.")
            return True
        except Exception as e:
            print(f"Error during defragmentation: {e}")
            return False

class FileSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File System Recovery and Optimization Tool")
        self.fs = FileSystem()

        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        """Create and arrange GUI components."""
        # Current directory display
        self.dir_label = tk.Label(self.root, text=f"Current Directory: {self.fs.current_dir}", anchor='w')
        self.dir_label.grid(row=0, column=0, padx=10, pady=5, sticky='ew')

        # Frame for file operations
        file_frame = tk.LabelFrame(self.root, text="File Operations", padx=10, pady=10)
        file_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(file_frame, text="Create File", command=self.create_file).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(file_frame, text="Open File", command=self.open_file).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(file_frame, text="Open Folder", command=self.open_folder).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(file_frame, text="Delete File", command=self.delete_file).grid(row=0, column=3, padx=5, pady=5)

        # Frame for directory operations
        dir_frame = tk.LabelFrame(self.root, text="Directory Operations", padx=10, pady=10)
        dir_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(dir_frame, text="Create Directory", command=self.create_directory).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(dir_frame, text="Delete Directory", command=self.delete_directory).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(dir_frame, text="Rename File/Folder", command=self.rename_file_or_folder).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(dir_frame, text="Change Directory", command=self.change_directory).grid(row=0, column=3, padx=5, pady=5)

        # Frame for advanced operations
        advanced_frame = tk.LabelFrame(self.root, text="Advanced Operations", padx=10, pady=10)
        advanced_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(advanced_frame, text="Move File/Folder", command=self.move_file_or_folder).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(advanced_frame, text="Copy File/Folder", command=self.copy_file_or_folder).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(advanced_frame, text="List Files/Folders", command=self.list_files_and_folders).grid(row=0, column=2, padx=5, pady=5)

        # Frame for recovery and optimization
        recovery_frame = tk.LabelFrame(self.root, text="Recovery and Optimization", padx=10, pady=10)
        recovery_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        tk.Button(recovery_frame, text="Simulate Disk Crash", command=self.simulate_crash).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(recovery_frame, text="Defragment", command=self.defragment).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(recovery_frame, text="Corrupt File", command=self.corrupt_file).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(recovery_frame, text="Restore File", command=self.restore_file).grid(row=0, column=3, padx=5, pady=5)

        # Output console
        self.console = scrolledtext.ScrolledText(self.root, width=80, height=20)
        self.console.grid(row=5, column=0, padx=10, pady=10)

    def update_dir_label(self):
        """Update the current directory label."""
        self.dir_label.config(text=f"Current Directory: {self.fs.current_dir}")

    def create_file(self):
        """Create a file."""
        name = filedialog.asksaveasfilename(
            title="Create File",
            initialdir=self.fs.current_dir,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if name:
            content = simpledialog.askstring("File Content", "Enter file content:")
            if content is not None:  # User pressed OK
                success = self.fs.create_file(os.path.basename(name), content)
                if success:
                    self.console.insert(tk.END, f"File '{os.path.basename(name)}' created.\n")
                else:
                    self.console.insert(tk.END, f"Failed to create file '{os.path.basename(name)}'.\n")

    def open_file(self):
        """Open a file with the system's default application."""
        name = filedialog.askopenfilename(
            title="Open File",
            initialdir=self.fs.current_dir
        )
        if name:
            try:
                # Platform-specific file opening
                if platform.system() == 'Windows':
                    os.startfile(name)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', name))
                else:  # Linux and other Unix-like systems
                    subprocess.call(('xdg-open', name))
                
                self.console.insert(tk.END, f"Opened file '{os.path.basename(name)}' with default application.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def open_folder(self):
        """Open a folder in the system's file explorer."""
        folder = filedialog.askdirectory(
            title="Open Folder",
            initialdir=self.fs.current_dir
        )
        if folder:
            try:
                if platform.system() == 'Windows':
                    os.startfile(folder)
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', folder))
                else:  # Linux and other Unix-like systems
                    subprocess.call(('xdg-open', folder))
                
                self.console.insert(tk.END, f"Opened folder '{os.path.basename(folder)}' in file explorer.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {str(e)}")

    def delete_file(self):
        """Delete a file."""
        name = filedialog.askopenfilename(
            title="Delete File",
            initialdir=self.fs.current_dir
        )
        if name:
            try:
                success = self.fs.delete_file(os.path.basename(name))
                if success:
                    self.console.insert(tk.END, f"File '{os.path.basename(name)}' deleted.\n")
                else:
                    self.console.insert(tk.END, f"Failed to delete file '{os.path.basename(name)}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_directory(self):
        """Create a directory."""
        name = simpledialog.askstring("Create Directory", "Enter directory name:")
        if name:
            success = self.fs.create_directory(name)
            if success:
                self.console.insert(tk.END, f"Directory '{name}' created.\n")
            else:
                self.console.insert(tk.END, f"Failed to create directory '{name}'.\n")

    def delete_directory(self):
        """Delete a directory."""
        name = filedialog.askdirectory(
            title="Delete Directory",
            initialdir=self.fs.current_dir
        )
        if name:
            try:
                success = self.fs.delete_directory(os.path.basename(name))
                if success:
                    self.console.insert(tk.END, f"Directory '{os.path.basename(name)}' deleted.\n")
                else:
                    self.console.insert(tk.END, f"Failed to delete directory '{os.path.basename(name)}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def rename_file_or_folder(self):
        """Rename a file or folder."""
        old_name = filedialog.askopenfilename(
            title="Select File/Folder to Rename",
            initialdir=self.fs.current_dir
        )
        if not old_name:
            old_name = filedialog.askdirectory(
                title="Select File/Folder to Rename",
                initialdir=self.fs.current_dir
            )
        
        if old_name:
            new_name = simpledialog.askstring("Rename", "Enter new name:")
            if new_name:
                try:
                    success = self.fs.rename_file_or_folder(os.path.basename(old_name), new_name)
                    if success:
                        self.console.insert(tk.END, f"Renamed '{os.path.basename(old_name)}' to '{new_name}'.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to rename '{os.path.basename(old_name)}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def move_file_or_folder(self):
        """Move a file or folder."""
        name = filedialog.askopenfilename(
            title="Select File/Folder to Move",
            initialdir=self.fs.current_dir
        )
        if not name:
            name = filedialog.askdirectory(
                title="Select File/Folder to Move",
                initialdir=self.fs.current_dir
            )
        
        if name:
            destination = filedialog.askdirectory(
                title="Select Destination",
                initialdir=self.fs.current_dir
            )
            if destination:
                try:
                    success = self.fs.move_file_or_folder(os.path.basename(name), destination)
                    if success:
                        self.console.insert(tk.END, f"Moved '{os.path.basename(name)}' to '{destination}'.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to move '{os.path.basename(name)}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def copy_file_or_folder(self):
        """Copy a file or folder."""
        name = filedialog.askopenfilename(
            title="Select File/Folder to Copy",
            initialdir=self.fs.current_dir
        )
        if not name:
            name = filedialog.askdirectory(
                title="Select File/Folder to Copy",
                initialdir=self.fs.current_dir
            )
        
        if name:
            destination = filedialog.askdirectory(
                title="Select Destination",
                initialdir=self.fs.current_dir
            )
            if destination:
                try:
                    success = self.fs.copy_file_or_folder(os.path.basename(name), destination)
                    if success:
                        self.console.insert(tk.END, f"Copied '{os.path.basename(name)}' to '{destination}'.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to copy '{os.path.basename(name)}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def list_files_and_folders(self):
        """List files and folders."""
        try:
            files = self.fs.list_files_and_folders()
            self.console.insert(tk.END, f"Files/Folders in '{self.fs.current_dir}':\n")
            for item in files:
                self.console.insert(tk.END, f"- {item}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_directory(self):
        """Change the current directory."""
        path = filedialog.askdirectory(
            title="Change Directory",
            initialdir=self.fs.current_dir
        )
        if path:
            try:
                success = self.fs.change_directory(path)
                if success:
                    self.update_dir_label()
                    self.console.insert(tk.END, f"Changed to directory '{path}'.\n")
                else:
                    self.console.insert(tk.END, f"Failed to change to directory '{path}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def simulate_crash(self):
        """Simulate a disk crash."""
        success = self.fs.simulate_crash()
        if success:
            self.console.insert(tk.END, "Simulated disk crash: Journal file deleted.\n")
        else:
            self.console.insert(tk.END, "Failed to simulate disk crash.\n")

    def defragment(self):
        """Defragment the current directory."""
        self.console.insert(tk.END, "Starting defragmentation...\n")
        self.root.update()  # Update GUI to show the message
        success = self.fs.defragment()
        if success:
            self.console.insert(tk.END, "Defragmentation complete.\n")
        else:
            self.console.insert(tk.END, "Defragmentation failed.\n")

    def corrupt_file(self):
        """Corrupt a file."""
        name = filedialog.askopenfilename(
            title="Select File to Corrupt",
            initialdir=self.fs.current_dir
        )
        if name:
            try:
                success = self.fs.corrupt_file(os.path.basename(name))
                if success:
                    self.console.insert(tk.END, f"File '{os.path.basename(name)}' corrupted.\n")
                else:
                    self.console.insert(tk.END, f"Failed to corrupt file '{os.path.basename(name)}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def restore_file(self):
        """Restore a file from backup."""
        name = filedialog.askopenfilename(
            title="Select File to Restore",
            initialdir=self.fs.current_dir
        )
        if name:
            try:
                success = self.fs.restore_file(os.path.basename(name))
                if success:
                    self.console.insert(tk.END, f"File '{os.path.basename(name)}' restored from backup.\n")
                else:
                    self.console.insert(tk.END, f"Failed to restore file '{os.path.basename(name)}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

# Main Function
if __name__ == "__main__":
    root = tk.Tk()
    app = FileSystemGUI(root)
    root.mainloop()