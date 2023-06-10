import configparser

# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    config.read('configurations.ini')
    return config

def set_cmd_title():
    import sys
    import os

    # Retrieve the filename of the Python script
    script_filename = os.path.basename(sys.argv[0])

    # Set the command prompt window title
    if sys.platform.startswith('win'):
        # For Windows
        os.system(f' File Title->  {script_filename}')
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        # For Linux and macOS
        os.system(f'echo -ne "\033]0;{script_filename}\007"')