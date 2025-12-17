import os

def get_raspberry_pi_model():  
    try:  
        with open('/proc/cpuinfo', 'r') as f:  
            cpuinfo = f.readlines()  
        for line in cpuinfo:  
            if line.startswith('Model'):  
                model_info = line.strip().split(':')[-1].strip().split("Model")[0].strip()
                return model_info  
        return 'Unknown Raspberry Pi Model'  
    except Exception as e:  
        print(f"Error reading /proc/cpuinfo: {e}")  
        return 'Error Reading' 

def run_command(command):
    """Execute the specified shell command"""
    print(f"Running: {command}")
    result = os.system(command)
    if result != 0:
        raise Exception(f"Command failed: {command}")

def clone_with_retry(repo_url, max_retries=3, recurse_submodules=False):
    """Clone repository with retry mechanism"""
    for attempt in range(max_retries):
        try:
            print(f"Attempting to clone repository (attempt {attempt + 1}/{max_retries})")
            if recurse_submodules:
                run_command(f"git clone --recurse-submodules {repo_url}")
            else:
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

def install_piolib():
    try:
        username = os.getlogin()
        home_dir = os.path.expanduser(f"~{username}")
    except Exception:
        home_dir = "/home/pi"
        print("Warning: Unable to get current username, using default path /home/pi")
    os.chdir(home_dir)

    run_command("sudo apt install build-essential cmake device-tree-compiler libfdt-dev libgnutls28-dev libpio-dev")
    folder_path = os.path.join(home_dir, "utils")
    if os.path.exists(folder_path):
        print("Repository directory already exists, skipping clone step")
    else:
        success = clone_with_retry("https://github.com/Freenove/utils.git")
        if not success:
            raise Exception("Failed to clone repository after multiple attempts")
    run_command(f"sudo chmod 777 * -R -f")

    target_dir = os.path.join(home_dir, "utils", "piolib", "examples")
    if not os.path.exists(target_dir):
        raise Exception(f"No 'examples' directory found in {os.path.join(home_dir, 'utils', 'piolib')}")
    os.chdir(target_dir)
    print(f"Changed to directory: {target_dir}")
    run_command("cmake -S . -B build") 
    os.chdir("build")  
    run_command("sudo make install") 
    os.chdir(home_dir)  

def install_rpi_ws281x():
    try:
        username = os.getlogin()
        home_dir = os.path.expanduser(f"~{username}")
    except Exception:
        home_dir = "/home/pi"
        print("Warning: Unable to get current username, using default path /home/pi")
    os.chdir(home_dir)
    folder_path = os.path.join(home_dir, "rpi-ws281x-python")
    if os.path.exists(folder_path):
        print("Repository directory already exists, skipping clone step")
    else:
        success = clone_with_retry("https://github.com/rpi-ws281x/rpi-ws281x-python.git", recurse_submodules=True)
        if not success:
            raise Exception("Failed to clone repository after multiple attempts")
    run_command(f"sudo chmod 777 * -R -f")

    target_dir = os.path.join(home_dir, "rpi-ws281x-python", "library")
    if not os.path.exists(target_dir):
        raise Exception(f"No 'library' directory found in {os.path.join(home_dir, 'rpi-ws281x-python', 'library')}")
    os.chdir(target_dir)
    print(f"Changed to directory: {target_dir}")
    run_command("sudo python3 setup.py install")
    os.chdir(home_dir)  

def main():
    try:
        run_command("sudo apt update")  # Update package list

        if "Pi 5" in get_raspberry_pi_model():
            install_piolib()
        else:
            install_rpi_ws281x()

    except Exception as e:
        # Handle exceptions and print error message
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Entry point of the script
    main()
