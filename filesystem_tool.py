import os
import shutil
import time
import pickle
import random
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import subprocess
import platform

class FileSystem:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.journal_file = os.path.join(self.current_dir, "filesystem_journal.log")
        self.backup_dir = os.path.join(self.current_dir, "backup")
        self.cache = {}
        self.load_journal()
        self.create_backup_dir()

    def create_backup_dir(self):
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def load_journal(self):
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
        with open(self.journal_file, "wb") as f:
            pickle.dump(self.cache, f)

    def create_file(self, file_path, content):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(content)
            self.cache[file_path] = content
            self.save_journal()
            self.backup_file(file_path)
            print(f"File '{file_path}' created.")
            return True
        except (IOError, OSError) as e:
            print(f"Error creating file: {e}")
            return False

    def delete_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")
        try:
            os.remove(file_path)
            if file_path in self.cache:
                del self.cache[file_path]
            self.save_journal()
            print(f"File '{file_path}' deleted.")
            return True
        except (IOError, OSError) as e:
            print(f"Error deleting file: {e}")
            return False

    def create_directory(self, dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"Directory '{dir_path}' created.")
            return True
        except (IOError, OSError) as e:
            print(f"Error creating directory: {e}")
            return False

    def delete_directory(self, dir_path):
        if not os.path.exists(dir_path):
            raise FileNotFoundError(f"Directory '{dir_path}' not found.")
        try:
            shutil.rmtree(dir_path)
            for cached_path in list(self.cache.keys()):
                if cached_path.startswith(dir_path):
                    del self.cache[cached_path]
            self.save_journal()
            print(f"Directory '{dir_path}' deleted.")
            return True
        except (IOError, OSError) as e:
            print(f"Error deleting directory: {e}")
            return False

    def rename_file_or_folder(self, old_path, new_path):
        if not os.path.exists(old_path):
            raise FileNotFoundError(f"'{old_path}' not found.")
        if os.path.exists(new_path):
            raise FileExistsError(f"'{new_path}' already exists.")
        try:
            os.rename(old_path, new_path)
            if old_path in self.cache:
                self.cache[new_path] = self.cache.pop(old_path)
            self.save_journal()
            self.backup_file(new_path)
            print(f"Renamed '{old_path}' to '{new_path}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error renaming: {e}")
            return False

    def move_file_or_folder(self, source_path, destination_dir):
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"'{source_path}' not found.")
        dest_path = os.path.join(destination_dir, os.path.basename(source_path))
        if os.path.exists(dest_path):
            raise FileExistsError(f"'{os.path.basename(source_path)}' already exists in destination.")
        try:
            shutil.move(source_path, destination_dir)
            if source_path in self.cache:
                del self.cache[source_path]
            self.save_journal()
            print(f"Moved '{source_path}' to '{destination_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error moving: {e}")
            return False

    def copy_file_or_folder(self, source_path, destination_dir):
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"'{source_path}' not found.")
        dest_path = os.path.join(destination_dir, os.path.basename(source_path))
        if os.path.exists(dest_path):
            raise FileExistsError(f"'{os.path.basename(source_path)}' already exists in destination.")
        try:
            if os.path.isdir(source_path):
                shutil.copytree(source_path, dest_path)
            else:
                shutil.copy2(source_path, dest_path)
            print(f"Copied '{source_path}' to '{destination_dir}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error copying: {e}")
            return False

    def list_files_and_folders(self, path=None):
        target_dir = path if path else self.current_dir
        try:
            return os.listdir(target_dir)
        except (IOError, OSError) as e:
            print(f"Error listing directory: {e}")
            return []

    def change_directory(self, path):
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
        try:
            backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
            shutil.copy2(file_path, backup_path)
            print(f"Backup created for '{file_path}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error creating backup: {e}")
            return False

    def restore_file(self, backup_name, restore_path=None):
        backup_path = os.path.join(self.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup for '{backup_name}' not found.")
        if restore_path is None:
            restore_path = os.path.join(self.current_dir, backup_name)
        try:
            shutil.copy2(backup_path, restore_path)
            with open(restore_path, "r") as f:
                self.cache[restore_path] = f.read()
            self.save_journal()
            print(f"File '{backup_name}' restored to '{restore_path}'.")
            return True
        except (IOError, OSError) as e:
            print(f"Error restoring file: {e}")
            return False

    def corrupt_file(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{file_path}' not found.")
        try:
            with open(file_path, "wb") as f:
                f.write(os.urandom(100))
            if file_path in self.cache:
                del self.cache[file_path]
            self.save_journal()
            print(f"File '{file_path}' corrupted.")
            return True
        except (IOError, OSError) as e:
            print(f"Error corrupting file: {e}")
            return False

    def simulate_crash(self):
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
        print("Defragmenting... This may take a while.")
        try:
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
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Color palette
        self.bg_color = '#f5f6fa'
        self.header_color = '#353b48'
        self.primary_color = '#40739e'
        self.success_color = '#44bd32'
        self.warning_color = '#fbc531'
        self.danger_color = '#e84118'
        self.light_text = '#f5f6fa'
        self.dark_text = '#2f3640'
        
        # Configure styles
        self.root.configure(bg=self.bg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Header.TLabel', 
                           background=self.header_color,
                           foreground=self.light_text,
                           font=('Segoe UI', 11, 'bold'),
                           padding=10)
        self.style.configure('Section.TLabelframe', 
                           background=self.bg_color,
                           foreground=self.dark_text,
                           font=('Segoe UI', 10, 'bold'),
                           borderwidth=2,
                           relief='groove')
        self.style.configure('Section.TLabelframe.Label', 
                           background=self.bg_color,
                           foreground=self.primary_color)
        self.style.configure('Primary.TButton',
                           background=self.primary_color,
                           foreground=self.light_text,
                           borderwidth=1,
                           font=('Segoe UI', 9),
                           padding=6)
        self.style.map('Primary.TButton',
                     background=[('active', '#487eb0')])
        self.style.configure('Success.TButton',
                           background=self.success_color,
                           foreground=self.light_text)
        self.style.map('Success.TButton',
                     background=[('active', '#4cd137')])
        self.style.configure('Danger.TButton',
                           background=self.danger_color,
                           foreground=self.light_text)
        self.style.map('Danger.TButton',
                     background=[('active', '#c23616')])
        self.style.configure('Warning.TButton',
                           background=self.warning_color,
                           foreground=self.dark_text)
        self.style.map('Warning.TButton',
                     background=[('active', '#e1b12c')])

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill='x', pady=(0, 10))
        
        self.dir_label = ttk.Label(
            header_frame,
            text=f"📁 Current Directory: {self.fs.current_dir}",
            style='Header.TLabel',
            anchor='w'
        )
        self.dir_label.pack(fill='x', padx=10)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_file_operations_tab(notebook)
        self.create_directory_operations_tab(notebook)
        self.create_advanced_operations_tab(notebook)
        self.create_recovery_tab(notebook)
        
        # Console
        console_frame = ttk.LabelFrame(
            main_frame,
            text='Console Output',
            style='Section.TLabelframe'
        )
        console_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='white',
            fg=self.dark_text,
            padx=10,
            pady=10,
            height=10
        )
        self.console.pack(fill='both', expand=True)

    def create_file_operations_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='📄 File Operations')
        
        frame = ttk.LabelFrame(tab, text='File Operations', style='Section.TLabelframe')
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        buttons = [
            ('Create File', self.create_file, 'Success.TButton', '📝'),
            ('Open File', self.open_file, 'Primary.TButton', '📂'),
            ('Delete File', self.delete_file, 'Danger.TButton', '❌'),
            ('Corrupt File', self.corrupt_file, 'Warning.TButton', '⚠️')
        ]
        
        for i, (text, command, style, icon) in enumerate(buttons):
            btn = ttk.Button(frame, text=f"{icon} {text}", command=command, style=style)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            frame.grid_columnconfigure(i, weight=1)

    def create_directory_operations_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='📂 Directory Operations')
        
        frame = ttk.LabelFrame(tab, text='Directory Operations', style='Section.TLabelframe')
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        buttons = [
            ('Create Directory', self.create_directory, 'Success.TButton', '📁'),
            ('Delete Directory', self.delete_directory, 'Danger.TButton', '🗑️'),
            ('Rename File/Folder', self.rename_file_or_folder, 'Primary.TButton', '✏️'),
            ('Change Directory', self.change_directory, 'Primary.TButton', '🔄')
        ]
        
        for i, (text, command, style, icon) in enumerate(buttons):
            btn = ttk.Button(frame, text=f"{icon} {text}", command=command, style=style)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            frame.grid_columnconfigure(i, weight=1)

    def create_advanced_operations_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='⚙️ Advanced Operations')
        
        frame = ttk.LabelFrame(tab, text='Advanced Operations', style='Section.TLabelframe')
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        buttons = [
            ('Move File/Folder', self.move_file_or_folder, 'Primary.TButton', '➡️'),
            ('Copy File/Folder', self.copy_file_or_folder, 'Primary.TButton', '📋'),
            ('List Contents', self.list_files_and_folders, 'Primary.TButton', '📜')
        ]
        
        for i, (text, command, style, icon) in enumerate(buttons):
            btn = ttk.Button(frame, text=f"{icon} {text}", command=command, style=style)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            frame.grid_columnconfigure(i, weight=1)

    def create_recovery_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text='🔧 Recovery Tools')
        
        frame = ttk.LabelFrame(tab, text='Recovery Tools', style='Section.TLabelframe')
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        buttons = [
            ('Simulate Crash', self.simulate_crash, 'Warning.TButton', '💥'),
            ('Defragment', self.defragment, 'Primary.TButton', '🔧'),
            ('Restore File', self.restore_file, 'Success.TButton', '⏮️')
        ]
        
        for i, (text, command, style, icon) in enumerate(buttons):
            btn = ttk.Button(frame, text=f"{icon} {text}", command=command, style=style)
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
            frame.grid_columnconfigure(i, weight=1)

    # All original methods remain unchanged below...
    def update_dir_label(self):
        self.dir_label.config(text=f"📁 Current Directory: {self.fs.current_dir}")

    def create_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Create File",
            initialdir=self.fs.current_dir,
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            content = simpledialog.askstring("File Content", "Enter file content:")
            if content is not None:
                try:
                    success = self.fs.create_file(file_path, content)
                    if success:
                        self.console.insert(tk.END, f"File '{file_path}' created.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to create file '{file_path}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def open_file(self):
        file_path = filedialog.askopenfilename(
            title="Open File",
            initialdir=self.fs.current_dir
        )
        if file_path:
            try:
                if platform.system() == 'Windows':
                    os.startfile(file_path)
                elif platform.system() == 'Darwin':
                    subprocess.call(('open', file_path))
                else:
                    subprocess.call(('xdg-open', file_path))
                self.console.insert(tk.END, f"Opened file '{file_path}' with default application.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def open_folder(self):
        folder_path = filedialog.askdirectory(
            title="Open Folder",
            initialdir=self.fs.current_dir
        )
        if folder_path:
            try:
                if platform.system() == 'Windows':
                    os.startfile(folder_path)
                elif platform.system() == 'Darwin':
                    subprocess.call(('open', folder_path))
                else:
                    subprocess.call(('xdg-open', folder_path))
                self.console.insert(tk.END, f"Opened folder '{folder_path}' in file explorer.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open folder: {str(e)}")

    def delete_file(self):
        file_path = filedialog.askopenfilename(
            title="Delete File",
            initialdir=self.fs.current_dir
        )
        if file_path:
            try:
                success = self.fs.delete_file(file_path)
                if success:
                    self.console.insert(tk.END, f"File '{file_path}' deleted.\n")
                else:
                    self.console.insert(tk.END, f"Failed to delete file '{file_path}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def create_directory(self):
        dir_path = filedialog.askdirectory(
            title="Select Parent Directory",
            initialdir=self.fs.current_dir
        )
        if dir_path:
            name = simpledialog.askstring("Create Directory", "Enter directory name:")
            if name:
                full_path = os.path.join(dir_path, name)
                try:
                    success = self.fs.create_directory(full_path)
                    if success:
                        self.console.insert(tk.END, f"Directory '{full_path}' created.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to create directory '{full_path}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def delete_directory(self):
        dir_path = filedialog.askdirectory(
            title="Delete Directory",
            initialdir=self.fs.current_dir
        )
        if dir_path:
            try:
                success = self.fs.delete_directory(dir_path)
                if success:
                    self.console.insert(tk.END, f"Directory '{dir_path}' deleted.\n")
                else:
                    self.console.insert(tk.END, f"Failed to delete directory '{dir_path}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def rename_file_or_folder(self):
        old_path = filedialog.askopenfilename(
            title="Select File/Folder to Rename",
            initialdir=self.fs.current_dir
        )
        if not old_path:
            old_path = filedialog.askdirectory(
                title="Select File/Folder to Rename",
                initialdir=self.fs.current_dir
            )
        if old_path:
            new_name = simpledialog.askstring("Rename", "Enter new name:")
            if new_name:
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                try:
                    success = self.fs.rename_file_or_folder(old_path, new_path)
                    if success:
                        self.console.insert(tk.END, f"Renamed '{old_path}' to '{new_path}'.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to rename '{old_path}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def move_file_or_folder(self):
        source_path = filedialog.askopenfilename(
            title="Select File/Folder to Move",
            initialdir=self.fs.current_dir
        )
        if not source_path:
            source_path = filedialog.askdirectory(
                title="Select File/Folder to Move",
                initialdir=self.fs.current_dir
            )
        if source_path:
            destination_dir = filedialog.askdirectory(
                title="Select Destination Directory",
                initialdir=self.fs.current_dir
            )
            if destination_dir:
                try:
                    success = self.fs.move_file_or_folder(source_path, destination_dir)
                    if success:
                        self.console.insert(tk.END, f"Moved '{source_path}' to '{destination_dir}'.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to move '{source_path}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def copy_file_or_folder(self):
        source_path = filedialog.askopenfilename(
            title="Select File/Folder to Copy",
            initialdir=self.fs.current_dir
        )
        if not source_path:
            source_path = filedialog.askdirectory(
                title="Select File/Folder to Copy",
                initialdir=self.fs.current_dir
            )
        if source_path:
            destination_dir = filedialog.askdirectory(
                title="Select Destination Directory",
                initialdir=self.fs.current_dir
            )
            if destination_dir:
                try:
                    success = self.fs.copy_file_or_folder(source_path, destination_dir)
                    if success:
                        self.console.insert(tk.END, f"Copied '{source_path}' to '{destination_dir}'.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to copy '{source_path}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

    def list_files_and_folders(self):
        dir_path = filedialog.askdirectory(
            title="Select Directory to List",
            initialdir=self.fs.current_dir
        )
        if dir_path:
            try:
                files = self.fs.list_files_and_folders(dir_path)
                self.console.insert(tk.END, f"Files/Folders in '{dir_path}':\n")
                for item in files:
                    self.console.insert(tk.END, f"- {item}\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def change_directory(self):
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
        success = self.fs.simulate_crash()
        if success:
            self.console.insert(tk.END, "Simulated disk crash: Journal file deleted.\n")
        else:
            self.console.insert(tk.END, "Failed to simulate disk crash.\n")

    def defragment(self):
        self.console.insert(tk.END, "Starting defragmentation...\n")
        self.root.update()
        success = self.fs.defragment()
        if success:
            self.console.insert(tk.END, "Defragmentation complete.\n")
        else:
            self.console.insert(tk.END, "Defragmentation failed.\n")

    def corrupt_file(self):
        file_path = filedialog.askopenfilename(
            title="Select File to Corrupt",
            initialdir=self.fs.current_dir
        )
        if file_path:
            try:
                success = self.fs.corrupt_file(file_path)
                if success:
                    self.console.insert(tk.END, f"File '{file_path}' corrupted.\n")
                else:
                    self.console.insert(tk.END, f"Failed to corrupt file '{file_path}'.\n")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def restore_file(self):
        backup_file = filedialog.askopenfilename(
            title="Select Backup File to Restore",
            initialdir=self.fs.backup_dir
        )
        if backup_file:
            restore_path = filedialog.asksaveasfilename(
                title="Select Restore Location",
                initialdir=self.fs.current_dir,
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if restore_path:
                try:
                    success = self.fs.restore_file(os.path.basename(backup_file), restore_path)
                    if success:
                        self.console.insert(tk.END, f"File restored to '{restore_path}' from backup.\n")
                    else:
                        self.console.insert(tk.END, f"Failed to restore file to '{restore_path}'.\n")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    
    # Window configuration
    window_width = 900
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.minsize(800, 600)
    
    # Try to set window icon (optional)
    try:
        root.iconbitmap('filesystem_icon.ico')  # Provide your own icon file
    except:
        pass
    
    app = FileSystemGUI(root)
    root.mainloop()