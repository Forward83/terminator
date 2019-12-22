import pexpect, struct, fcntl, termios, signal, sys
import time
from pexpect import spawn

global_pexpect_instance = None
short_timeout = 2   # Is used for ssh connection
long_timeout = 5    # Is used for console connection


def sigwinch_passthrough (sig, data):
    s = struct.pack("HHHH", 0, 0, 0, 0)
    a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s))
    if not global_pexpect_instance.closed:
        global_pexpect_instance.setwinsize(a[0], a[1])


def connect_to_host(ip):
    """
    Connect to host and configure local port forwarding from port 70+last 2 digits from last ip octet to board http
    :param ip: host ip address
    :return:
    """
    global global_pexpect_instance
    port = ip.split('.')[-1]
    port = port[1:]
    port_forward = "-L 70{}:169.254.1.1:80".format(port)
    child = spawn("ssh root@{} {}".format(ip, port_forward), timeout=short_timeout)
    index = child.expect(["assword:", pexpect.TIMEOUT])
    if index == 0:
        child.sendline("azsxdc")
        inner_ind = child.expect([':~#', 'assword'])
        if inner_ind == 1:
            sys.exit('Connection to host {} failed. Password is wrong, verify it in connection script'.format(ip))
        print(child.before.decode('utf-8'))
        print('\nPort forward 70{}:169.254.1.1:80 configured\n'.format(port))
        print()
        child.send('\r')
        child.setwinsize(32, 80)
        global_pexpect_instance = child
        signal.signal(signal.SIGWINCH, sigwinch_passthrough)
        child.interact()
    elif index == 1:
        sys.exit('Connection to host {} timed out'.format(ip))


def connect_to_board(ip, tty):
    """
    :param ip: terminal server ip
    :param tty: console port connected to board
    :return: interactive terminal for user
    """
    global global_pexpect_instance
    tty_number = tty.split('/')[-1]
    child = spawn("ssh root@{}".format(ip), timeout=short_timeout)
    log_file = open('logs/{}_log'.format(tty_number), 'wb')
    child.logfile = log_file
    index = child.expect(["assword:", pexpect.TIMEOUT])
    if index == 0:
        child.sendline("azsxdc")
        inner_ind = child.expect([':~#', 'assword'])
        if inner_ind == 1:
            sys.exit('Connection to host {} failed. Password is wrong, verify it in connection script'.format(ip))
    elif index == 1:
        sys.exit('Connection to host {} timed out'.format(ip))
    print(child.before.decode('utf-8'))
    time.sleep(1)
    child.sendline("minicom -D {}".format(tty))
    child.sendline('\r')
    index = child.expect(['login:\s(\r|\n)', ':~#', pexpect.TIMEOUT], timeout=long_timeout)
    if index == 0:
        child.sendline('root')
        child.expect('Password:')
        child.sendline('X0feu86@cvk')
        print(child.before.decode('utf-8'))
    elif index == 2:
        child.sendline('\r')
        try:
            index = child.expect(['login:\s(\r|\n)', ':~#'], timeout=long_timeout)
            child.sendline('root')
            child.expect('Password:')
            child.sendline('X0feu86@cvk')
            print(child.before.decode('utf-8'))
        except (pexpect.TIMEOUT, pexpect.EOF):
            print("\nCouldn't connect to {} from host {}.\n".format(tty, ip))
    global_pexpect_instance = child
    (rows, cols) = child.getwinsize()
    child.setwinsize(100, 80)
    signal.signal(signal.SIGWINCH, sigwinch_passthrough)
    child.interact()

def run_with_params():
    """
    Read user input and define correct function
    :return:
    """
    if len(sys.argv) == 3 and sys.argv[1] == '-a':
        connect_to_host(sys.argv[2])
    elif len(sys.argv) == 5 and sys.argv[3] == '-t' and sys.argv[4].startswith('/dev/ttyUSB'):
        connect_to_board(sys.argv[2], sys.argv[4])
    else:
        sys.exit('Please, run -h to read help for this tool')


if __name__ == '__main__':
    run_with_params()


