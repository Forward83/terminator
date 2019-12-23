import xml.etree.ElementTree as ET
import os, sys
import getpass
import re

# constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
xml_file = os.path.join(BASE_DIR, "setups.xml")
USER = getpass.getuser()
CONFIG_FILE = '/home/{}/.config/terminator/config'.format(USER)
TEST_FILE = '/home/{}/term_config'.format(USER)
TEMPLATE_FILE = os.path.join(BASE_DIR, 'template.txt')


def create_setup_menu(xml_file):
    """
    Parse xml file, print menu of setups and return data for each setup
    :param xml_file: file with setups description. Located in the same folder
    :return: dictionary of setups data: index is key, array of name, ap, sm, tuples to connect to ap,
    tuples to connect to sm
    """
    f_path = os.path.join(BASE_DIR, xml_file)
    setups_dict = dict()
    print("\n Available setups:\n")
    tree = ET.parse(f_path)
    root = tree.getroot()
    for ind, setup in enumerate(root.iter('SETUP')):
        name = setup.get('name')
        terminal_ip = setup.find('TERMINAL_IP').text
        ap_ip = setup[1].find('HOST_IP').text
        ap_tty = setup[1].find('TTY').text
        sm_ip = setup[2].find('HOST_IP').text
        sm_tty = setup[2].find('TTY').text
        setup_elements = [name, ap_ip, sm_ip, (terminal_ip, ap_tty), (terminal_ip, sm_tty)]
        print("      {}. {}".format(ind+1, name))
        setups_dict[str(ind+1)] = setup_elements
    print('\n')
    return (setups_dict)


def copy_template_to_file(file_path):
    """
    Copy layout template to config file if it is not exist there
    :param file_path: template file path
    :return:
    """
    with open(file_path, 'r+') as cf:
        if 'four_windows' not in cf.read():
            joined_data = []
            with open(TEMPLATE_FILE, 'r') as tf:
                template_data = tf.readlines()
            cf.seek(0)
            cf_data = cf.readlines()
            for cf_line in cf_data:
                joined_data.append(cf_line)
                if re.search('layouts', cf_line):
                    for t_line in template_data:
                        joined_data.append(t_line)
            cf.seek(0)
            for line in joined_data:
                cf.write(line)
                cf.truncate()


def create_config_file():
    """
    Make required modification to terminator config file. Insert template if needed and modify command parameters
    according to selected setup choice.
    :return:
    """
    setups = create_setup_menu(xml_file)
    setup_arr_ind = 1
    i = 1
    start_flag = False
    while True:
        i = input("Select setup index or type 'exit': ")
        if re.match('exit', i, flags=re.IGNORECASE):
            sys.exit(0)
        elif re.match('\d+', str(i)) and i in setups:
            break
        else:
            print("'{}' is Wrong choice. Make another".format(i))
    selected_setup = setups[str(i)]
    copy_template_to_file(CONFIG_FILE)
    with open(CONFIG_FILE, 'r+') as fh:
        data = fh.readlines()
        for line_ind, line in enumerate(data):
            if re.search('four_windows', line):
                start_flag = True
                continue
            if re.search('command', line) and start_flag:
                line = line.rstrip("\r\n")
                if setup_arr_ind < 3:
                    line = '     command = cd {}; python3 connections.py -a {}\n'.format(BASE_DIR, selected_setup[setup_arr_ind])
                    data[line_ind] = line
                elif setup_arr_ind == 3 or setup_arr_ind == 4:
                    terminal_ip, tty = selected_setup[setup_arr_ind]
                    line = '     command = cd {}; python3 connections.py -a {} -t {}\n'.format(BASE_DIR, terminal_ip, tty)
                    data[line_ind] = line
                else:
                    break
                setup_arr_ind += 1
        fh.seek(0)
        for line in data:
            fh.write(line)
        fh.truncate()


if __name__ == '__main__':
    create_config_file()
    os.system('terminator -l four_windows')





