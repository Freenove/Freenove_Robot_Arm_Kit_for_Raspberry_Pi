import os

def run_command(command):
    """Execute the specified shell command"""
    print(f"Running: {command}")
    result = os.system(command)
    if result != 0:
        raise Exception(f"Command failed: {command}")

def clone_with_retry(repo_url, max_retries=3):
    """Clone repository with retry mechanism"""
    for attempt in range(max_retries):
        try:
            print(f"Attempting to clone repository (attempt {attempt + 1}/{max_retries})")
            run_command(f"git clone {repo_url}")
            print("Repository cloned successfully")
            return True
        except Exception as e:
            print(f"Clone attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
            else:
                print("All retry attempts failed")
                return False
    return False

def main():
    try:
        # Step 1: Install dependency packages
        run_command("sudo apt update")  # Update package list

        try:
            username = os.getlogin()
            home_dir = os.path.expanduser(f"~{username}")
        except Exception:
            # If getting username fails, use default pi user
            home_dir = "/home/pi"
            print("Warning: Unable to get current username, using default path /home/pi")
        
        # Change to home directory using Python's method
        os.chdir(home_dir)

        # Install required development tools and libraries
        run_command("sudo apt install build-essential cmake device-tree-compiler libfdt-dev libgnutls28-dev libpio-dev")

        # Step 2: Clone repository from GitHub
        # Check if directory already exists before cloning
        folder_path = os.path.join(home_dir, "utils")
        if os.path.exists(folder_path):
            print("Repository directory already exists, skipping clone step")
        else:
            # Clone with retry mechanism
            success = clone_with_retry("https://github.com/Freenove/utils.git")
            if not success:
                raise Exception("Failed to clone repository after multiple attempts")

        # Step 3: Change permissions
        run_command(f"sudo chmod 777 * -R -f")

        # Step 4: Enter directory and execute cmake configuration
        # Use Python's chdir instead of shell command
        target_dir = os.path.join(home_dir, "utils", "piolib", "example")
        if not os.path.exists(target_dir):
            # Try alternative path
            target_dir = os.path.join(home_dir, "utils", "piolib", "examples")
            if not os.path.exists(target_dir):
                raise Exception(f"Neither 'example' nor 'examples' directory found in {os.path.join(home_dir, 'utils', 'piolib')}")
        
        os.chdir(target_dir)
        print(f"Changed to directory: {target_dir}")
        run_command("cmake -S . -B build")  # Configure project with CMake

        # Step 5: Enter build directory and install
        os.chdir("build")  # Use Python's chdir
        run_command("sudo make install")  # Compile and install the project
        os.chdir(home_dir)  # Return to home directory

        # Step 6: Remove __pycache__
        run_command("sudo rm __pycache__ -R -f")

    except Exception as e:
        # Handle exceptions and print error message
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Entry point of the script
    main()
