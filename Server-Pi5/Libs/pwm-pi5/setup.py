import subprocess  
import os  
  
def run_command(cmd):  
    try:  
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)  
        if result.stdout:  
            print("Output:", result.stdout)  
    except subprocess.CalledProcessError as e:  
        print(f"Error executing '{cmd}': {e}")  
  
def copy_file_to_boot_overlay(source_file, dest_dir="/boot/firmware/overlays/"):  
    # 检查目标目录是否存在  
    if not os.path.exists(dest_dir):  
        print(f"Directory {dest_dir} does not exist.")  
        return  
  
    # 复制文件到目标目录  
    try:  
        subprocess.run(["sudo", "cp", source_file, dest_dir], check=True)  
        print(f"File {source_file} copied to {dest_dir}")  
    except subprocess.CalledProcessError as e:  
        print(f"Error copying file: {e}")  

def append_to_config_txt(line_to_append, file_path="/boot/firmware/config.txt"):  
    try:  
        # 读取文件内容  
        with open(file_path, 'r') as file:  
            lines = file.readlines()  
          
        # 检查line_to_append是否已存在于文件中  
        if not any(line.strip() == line_to_append for line in lines):  
            # 如果不存在，则追加到新行  
            with open(file_path, 'a') as file:  
                file.write(line_to_append)  
                print(f"Added '{line_to_append}' to {file_path}")  
        else:  
            print(f"'{line_to_append}' already exists in {file_path}")  
            pass
    except FileNotFoundError:  
        # 如果文件不存在，则创建文件并添加内容  
        with open(file_path, 'w') as file:  
            file.write(line_to_append + '\n')  # 注意：这里通常不会这样做，因为config.txt有特定格式  
            #print(f"Created {file_path} and added '{line_to_append}'")  
        # 但实际上，对于config.txt，您可能只想在文件末尾追加，而不是替换整个文件  
        # 因此，更好的做法是在捕获FileNotFoundError后，直接执行追加操作（但文件实际上不会不存在）  
    except PermissionError:  
        print(f"Permission denied to write to {file_path}. Try running the script with sudo.")  
    except Exception as e:  
        print(f"An error occurred while appending to {file_path}: {e}")  
        
if __name__ == '__main__':  
    dts_file = "pwm-pi5-overlay.dts"  
    dtbo_file = "pwm-pi5.dtbo"  
      
    # 使用dtc将DTS转换为DTB  
    run_command(["dtc", "-I", "dts", "-O", "dtb", "-o", dtbo_file, dts_file])  
      
    # 修改文件权限（考虑使用更安全的权限设置）  
    run_command(["sudo", "chmod", "744", dtbo_file])  # 示例：仅所有者可读写，组和其他用户可读  
      
    # 复制DTBO文件到启动覆盖层目录  
    copy_file_to_boot_overlay(dtbo_file)  
  
    # 在config.txt中添加"dtoverlay=pwm-pi5"  
    line_to_append = "dtoverlay=pwm-pi5"  
    append_to_config_txt(line_to_append) 

    print("Please reboot the Raspberry PI.")