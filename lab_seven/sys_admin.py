# John Paul Larkin
# C00001754
# Scripting Lab seven
# 1/12/24

from datetime import datetime
from os import system   
import os
import shutil
import sys
import zipfile
import psutil

 # Use the user's home directory for the backup folderd
 # in order to avoid permission issues
BACKUP_FOLDER = '~/backup'

def copy_files_by_extension():
    # Clear the terminal screen
    clear_terminal()
    # Ask the user for the source folder - strip any whitespace
    print("Enter the source folder to search for files: ")
    # Print the current working folder for context
    print("The current directory is: ", os.getcwd())
    source_folder = input('\nEnter the source folder: ').strip()
    # Ask the user for the file extension - strip any whitespace
    extension = input("Enter the extension: eg .txt .py .jpg etc: ").strip()
    
    # Log the start of the backup process
    log_backup_start(f"Copying files with extension: {extension}")
    print_and_log(f"Source folder: {source_folder}")
    
    # PWD to the user's home directory for the backup folder
    destination_folder = os.path.expanduser(BACKUP_FOLDER)
    
    try:
        # Create destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)
    except Exception as e:
        # Exit the function if we can't create the destination folder
        print(f"Error creating destination folder: {e}")
        input("Press any key to continue...")
        return  
    
    # Check if the source folder exists
    if not validate_folder(source_folder):
        return
    
    print('source folder: ', source_folder)
    input("Press any key to continue...")
    
    count_files_copied = 0
    
    # Walk through the source folder 
    for root, _dirs, files in os.walk(source_folder):
        # Iterate through each file in the source folder
        for file in files:
            print(f"Checking {file}")
            # Check if the file has the specified extension
            if file.endswith(extension):
                print_and_log(f"Copying {file}")
                # Create the full path for the source file
                source_path = os.path.join(root, file)
                # Create the full path for the destination file
                dest_path = os.path.join(destination_folder, file)
                try:
                    # Copy the file to the destination folder
                    shutil.copy2(source_path, dest_path)
                    print_and_log(f"Copied: {file}")
                    # Increment the count of files copied
                    count_files_copied += 1
                except Exception as e:
                    print_and_log(f"Error copying {file}: {e}")
    
    # Print the total number of files copied
    print_and_log(f"\nTotal {extension} files backedup: {count_files_copied}")
    # Log the end of the backup process
    print_and_log(f"Backup completed at: {datetime.now()}")
    input("Press any key to continue...")


def incremental_backup():
    # Clear the terminal screen
    clear_terminal()
    log_backup_start("Starting Incremental backup")
    
    # Ask the user for the source folder - strip any whitespace
    source_folder = input("Enter the source folder to scan: ").strip()
    
    # PWD to the user's home directory for the backup folder
    destination_folder = os.path.expanduser(BACKUP_FOLDER)
    
    # Check if the source folder exists
    if not validate_folder(source_folder):
        return
    
    # Ensure the backup folder exists
    os.makedirs(destination_folder, exist_ok=True)
    
    # Track logs for each action
    new_files = []
    modified_files = []
    unchanged_files = []
    
    # Walk through the source folder
    for root, _dirs, files in os.walk(source_folder):
        # Iterate through each file in the source folder
        for file in files:
            # Full path for the source and destination files
            source_path = os.path.join(root, file)
            dest_path = os.path.join(destination_folder, file)
            try:
                if not os.path.exists(dest_path):
                    # File does not exist in the backup folder - copy it
                    shutil.copy2(source_path, dest_path)
                    # Add the file to the list of new files
                    new_files.append(file)
                else:
                    # File exists, check modification time of both files
                    source_mtime = os.path.getmtime(source_path)
                    dest_mtime = os.path.getmtime(dest_path)
                    # If the source file is newer
                    if source_mtime > dest_mtime:
                        # then overwrite it in the backup folder
                        shutil.copy2(source_path, dest_path)
                        # Add the file to the list of modified files
                        modified_files.append(file)
                    else:
                        # File is unchanged - add it to the unchanged list
                        unchanged_files.append(file)
            except Exception as e:
                print(f"Error processing {file}: {e}")
    
    # Print summary
    print_and_log("\nIncremental Backup Summary:")
    print_and_log(f"New files copied: {len(new_files)}")
    # If there are new files
    if new_files:
        # Print the list of new files 
        print_and_log("\n".join(new_files))
    
    print_and_log(f"\nModified files updated: {len(modified_files)}")
    # If there are modified files
    if modified_files:
        print_and_log("\n".join(modified_files))
        
    print_and_log(f"\nUnchanged files: {len(unchanged_files)}")
    # If there are unchanged files
    if unchanged_files:
        print_and_log("\n".join(unchanged_files))
    
    # Log the end of the backup process
    print_and_log(f"Backup completed at: {datetime.now()}")
    
    input("\nPress any key to continue...")
    

def create_compressed_archive():
      # Clear the terminal screen
    clear_terminal()
    
    # Log the start of the backup process
    print_and_log(f"Starting compressed archive at: {datetime.now()}")
    
    # Define the source folder (backup folder)
    source_folder = os.path.expanduser(BACKUP_FOLDER)
    
    # Check if the source folder exists
    if not validate_folder(source_folder):
        return
    

    # Generate a string timestamp in the format - YYYYMMDD_HHMMSS ie 20241201_120000
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Create the zip file name using the timestamp
    zip_file_name = f"backup_{timestamp}.zip"
    # Create the full path for the output zip file by joining the users home directory and the zip file name
    zip_file_path = os.path.join(os.path.expanduser('~'), zip_file_name)
    
    try:
        # Create a zip file 
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the source folder
            for root, _dirs, files in os.walk(source_folder):
                # Iterate through each file in the source folder
                for file in files:
                    # Full path of the file
                    file_path = os.path.join(root, file)
                    # Add file to the zip archive with a relative path
                    arcname = os.path.relpath(file_path, source_folder)
                    # Write the file to the zip archive
                    zipf.write(file_path, arcname)
                    print(f"Added {arcname} to the archive")    
        # Print confirmation of success
        print_and_log(f"\nCompressed archive created successfully: {zip_file_path}")
    except Exception as e:
        print_and_log(f"Error creating compressed archive: {e}")
    
    # Log the end of the backup process
    print_and_log(f"Finish compress process at: {datetime.now()}")
    
    input("Press any key to continue...")

# Helper function to clear the terminal screen
def clear_terminal():
       # Clear the terminal screen
    if sys.platform.startswith('win'):  # For Windows
        _ = system('cls')
    else:  # For Unix/Linux/MacOS
        _ = system('clear')
        
# Helper function to log messages to a file - but also print them to the terminal
def print_and_log(message):
    print(message)
    # Log the message to a file
    with open('backup_log.txt', 'a') as log_file:
        log_file.write(message + '\n')

# Helper function to validate that a folder exists
def validate_folder(source_folder):
    # Return false if the folder does not exist
    if not os.path.exists(source_folder):
        print(f"Error: The directory '{source_folder}' does not exist!")
        input("Press any key to continue...")
        return False
    # Return true if the folder does exist
    return True

def log_backup_start(message):
    print_and_log(f"Starting {message} at: {datetime.now()}")
    # Get overall CPU usage percentage - measure over 1 second
    cpu_usage = psutil.cpu_percent(interval=1) 
    print_and_log(f"CPU Usage: {cpu_usage}%")
    
    # Get memory usage percentage
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent
    print_and_log(f"Memory Usage: {memory_usage}%")

    # Get disk usage for the root directory
    disk_usage = psutil.disk_usage('/')

    # Display total, used, and free space in gigabytes - rounded to 2 decimal places
    # 1024 ** 3 to convert bytes to gigabytes
    print_and_log(f"Total Disk Space: {disk_usage.total / (1024 ** 3):.2f} GB")
    print_and_log(f"Used Disk Space: {disk_usage.used / (1024 ** 3):.2f} GB")
    print_and_log(f"Free Disk Space: {disk_usage.free / (1024 ** 3):.2f} GB")
    print_and_log(f"Disk Usage Percentage: {disk_usage.percent}%")
 
    # Get the operating system 
    os_name = os.name
    print_and_log(f"Operating System: {os_name}")

def main():    
    while True:
        clear_terminal()
        # Display the menu options
        print("1. Copy files by extension")
        print("2. Incremental backup")
        print("3. Create a compressed archive")
        print("4. Exit")
        # Get the users choice
        choice = input("Enter your choice: ")
        
        # Select the function based on the users choice
        if(choice == "1"):
            copy_files_by_extension()
        elif(choice == "2"):
            incremental_backup()
        elif(choice == "3"):
            create_compressed_archive()
        elif(choice == "4" or choice.lower() == "exit"):
            break
        else:
            print("Invalid choice")
            

if __name__ == "__main__":  
    main()     