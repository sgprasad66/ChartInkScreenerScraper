import configparser
import os
import os

# Method to read config file settings
def read_config():
    config = configparser.ConfigParser()
    #config.read('configurations.ini')
    config.read(os.path.join(os.path.dirname(__file__), 'configurations.ini'))
    #config.read('configurations.ini')
    config.read(os.path.join(os.path.dirname(__file__), 'configurations.ini'))
    return config

def set_cmd_title():
    import sys
    import os

    # Retrieve the filename of the Python script
    script_filename = os.path.basename(sys.argv[0])

    # Set the command prompt window title
    if sys.platform.startswith('win'):
        # For Windows
        os.system(f'title {script_filename}')
        os.system(f'title {script_filename}')
    elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        # For Linux and macOS
        os.system(f'echo -ne "\033]0;{script_filename}\007"')