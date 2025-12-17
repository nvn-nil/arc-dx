import os
import subprocess
import datetime
import shutil
import io # Part of the standard library, implicitly used by open() but good practice to acknowledge

def find_and_move_untracked_files(root_dir='.'):
    """
    Finds files in the current working directory that are not tracked by Git,
    moves them into a cleanup folder preserving the structure, and generates a log file.

    Args:
        root_dir (str): The directory to search within (default is current dir).
    """
    try:
        # 1. Setup paths and folder name
        current_date = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        cleanup_folder = f"cleanup_untracked_{current_date}"
        cleanup_path = os.path.join(root_dir, cleanup_folder)
        log_file_name = "cleanup_log.txt"
        log_file_path = os.path.join(cleanup_path, log_file_name)

        print(f"Cleanup folder will be: {cleanup_path}")
        
        # Check if the directory is a git repository
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                       capture_output=True, check=True, cwd=root_dir)

        # 2. Find untracked, non-ignored files
        print("-> Finding untracked, non-ignored files...")
        untracked_result = subprocess.run(
            ['git', 'ls-files', '--others', '--exclude-standard', '--full-name'],
            capture_output=True,
            text=True,
            check=True,
            cwd=root_dir
        )
        
        # Filter the output to only include files (and not directories)
        untracked_files = [
            f for f in untracked_result.stdout.strip().splitlines() 
            if os.path.isfile(os.path.join(root_dir, f))
        ]
        
        if not untracked_files:
            print("No untracked and non-ignored files found to clean up.")
            return

        print(f"Found {len(untracked_files)} untracked files that are not ignored.")
        
        # 3. Create the cleanup directory and initialize log content
        os.makedirs(cleanup_path, exist_ok=True)
        print(f"Created primary cleanup directory: {cleanup_folder}")
        
        log_entries = []
        log_entries.append(f"--- Git Untracked File Cleanup Log ---")
        log_entries.append(f"Date/Time of Execution: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_entries.append(f"Source Directory: {os.path.abspath(root_dir)}")
        log_entries.append(f"Destination Directory: {cleanup_folder}")
        log_entries.append(f"Total Files Found: {len(untracked_files)}\n")
        log_entries.append("Files Moved (Original Path -> Cleanup Path):\n")

        # 4. Move the files while preserving the directory structure
        print("-> Moving files and recreating structure...")
        
        files_moved_count = 0
        
        for relative_path in untracked_files:
            source_path = os.path.join(root_dir, relative_path)
            target_path = os.path.join(cleanup_path, relative_path)
            target_dir = os.path.dirname(target_path)
            
            # Ensure the target subdirectory exists (Key for structure preservation)
            os.makedirs(target_dir, exist_ok=True)
            
            try:
                # Move the file
                shutil.move(source_path, target_path)
                
                # Update the log list
                log_line = f"  MOVED: {relative_path}"
                log_entries.append(log_line)
                files_moved_count += 1
                
                print(f"  {log_line}")
                
            except Exception as e:
                error_line = f"  ERROR: {relative_path} - Failed to move. Reason: {e}"
                log_entries.append(error_line)
                print(error_line)

        log_entries.append(f"\nTotal Files Successfully Moved: {files_moved_count}")
        log_entries.append(f"--- End of Log ---")
        
        # 5. Write the log file
        try:
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(log_entries))
            print(f"\nSuccessfully generated log file: {log_file_name} inside {cleanup_folder}")
        except Exception as e:
            print(f"\nFATAL ERROR: Could not write log file to {log_file_path}. Reason: {e}")


        print("\nCleanup complete!")
        print(f"All untracked, non-ignored files have been moved to: {cleanup_folder}")

    except subprocess.CalledProcessError as e:
        print(f"Error executing git command. Ensure you are in a Git repository and have Git installed. Details: {e.cmd}")
        print(f"Stderr: {e.stderr.strip()}")
    except FileNotFoundError:
        print("Error: The 'git' command was not found. Please ensure Git is installed and in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    find_and_move_untracked_files(os.getcwd())