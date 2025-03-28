# OS_Project
# File System Recovery and Optimization Tool

A Python-based GUI application for file system operations with crash recovery and optimization features.

## Features

### File Operations
- **Create File**: Create new text files with custom content
- **Open File**: Open files with system default applications
- **Open Folder**: Open folders in system file explorer
- **Delete File**: Permanently delete files

### Directory Operations
- **Create Directory**: Create new folders/directories
- **Delete Directory**: Permanently delete folders and their contents
- **Rename File/Folder**: Rename both files and folders
- **Change Directory**: Navigate through the filesystem

### Advanced Operations
- **Move File/Folder**: Move items to new locations
- **Copy File/Folder**: Duplicate items to new locations
- **List Files/Folders**: View directory contents

### Recovery and Optimization
- **Simulate Disk Crash**: Test the journaling recovery system
- **Defragment**: Simulate disk defragmentation
- **Corrupt File**: Intentionally corrupt files (for testing)
- **Restore File**: Recover files from backup

## Technical Features
- **Journaling System**: Automatic crash recovery
- **File Caching**: Improved performance for frequent operations
- **Automatic Backups**: Important files are backed up automatically
- **Cross-platform**: Works on Windows, macOS, and Linux

## Requirements
- Python 3.6+
- Tkinter (usually included with Python)
- Standard Python libraries: os, shutil, time, pickle, random, subprocess, platform

## Installation
1. Clone the repository or download the source files
2. Ensure Python 3.6+ is installed
3. Run the application:
   ```bash
   python filesystem_tool.py
