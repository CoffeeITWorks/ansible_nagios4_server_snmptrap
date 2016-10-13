#!/usr/bin/python
# https://media.readthedocs.org/pdf/pynag/latest/pynag.pdf

from pynag.Model import Parsers
import os
from tempfile import mkstemp
from shutil import move
from os import remove, close
import re

nagios_config = '/usr/local/nagios/etc/nagios.cfg'
nagios_sock = '/usr/local/nagios/var/rw/live.sock'

p = Parsers.Livestatus(livestatus_socket_path=nagios_sock, nagios_cfg_file=nagios_config)

filename = "/etc/hosts"

if not os.path.isfile(nagios_config):
    raise SystemExit("file: {} does not exist".format(nagios_config))


hosts = p.get_hosts()

if not os.path.isfile(filename):
    raise SystemExit("file: {} does not exist".format(filename))

new_whitespace = False
replace_list = []
appended_lines = 0
updated_lines = 0
nagios_hosts_readed = 0

# Append nagios hosts addresses to filename
for host in hosts:

    if str(host.get('address', None)):
        nagios_hosts_readed += 1
        address = host['address'].encode('utf-8')
        name = host['name'].encode('utf-8')
        alias = host['alias'].encode('utf-8')
        host_line = "{}    {}  # {} ** Added from nagios **\n".format(address,
                                                                      name,
                                                                      alias)
        with open(filename, "r+") as file:
            for line in file:

                # With regex I can ensure there is an space after the address
                if bool(re.search("{} ".format(address), line)):

                    if not bool(re.search(name.upper(), line.upper())):
                        replace_list.append({'name': name,
                                             'ip': address,
                                             'alias': alias,
                                             'line': line})
                        print("duplicated : {}    {} in line: {} ".format(address, name, line))
                    break
            else:  # not found, we are at the eof
                if not new_whitespace:
                    file.write("\n")
                    new_whitespace = True

                file.write(host_line) # append missing data
                appended_lines += 1


# Replace lines that host and address didn't match
if replace_list:

    file_path = os.path.abspath(filename)
    # Create temp file
    fh, abs_path = mkstemp()
    new_file = open(abs_path, 'w')

    # Open old file
    old_file = open(file_path)
    lines_list = old_file.readlines()  # we will use old_lines as list
    old_file.close()

    for i in range(len(replace_list)):

        address = replace_list[i].get('ip', '')
        name = replace_list[i].get('name', '')
        alias = replace_list[i].get('alias', '')
        old_line = replace_list[i].get('line', '')
        host_line = "{}    {}  # {} ** Updated from nagios **\n".format(address, name, alias)

        # remove the old line
        lines_list.pop(lines_list.index(old_line))
        # add the new one to the list
        lines_list.append(host_line)
        updated_lines += 1

    new_file.writelines(lines_list)
    #close temp file
    new_file.close()
    close(fh)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
    #Allow users to read, change octal mode to 0644
    os.chmod(file_path, 0o644)

print("Updated lines: {} \n "
      "Appended lines: {} \n"
      "Nagios hosts readed {}\n".format(updated_lines,
                                        appended_lines,
                                        nagios_hosts_readed))


