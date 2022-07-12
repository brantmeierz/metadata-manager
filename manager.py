import datetime
import os
from os import path
import json
import shutil
import time

extension_synonyms = [
    {'.flac', '.FLAC'},
    {'.jpg', '.JPG', '.jpeg'},
]

JUNK_FILES = {
    '.crdownload',
    '.html'
}

KEEP_JUNK = True
""" Whether or not to automatically delete junk files. If kept, junk files will be moved to a junk folder. """

JUNK_FOLDER = './junk/'
""" The folder to deposit junk files in."""

def get_files_dir(path, ext=''):
    file_list = []
    for entry in os.listdir(path):
        if os.path.isfile(os.path.join(path, entry)):
            if (entry.endswith(ext)):
                file_list.append(entry)
    return file_list

def get_modified_time(file):
    return file.stat().st_mtime

def load_json():
    global runtime_data
    with open("runtime_data.json") as f:
        runtime_data = json.load(f)

def save_json():
    js = json.dumps(runtime_data, indent=1)
    f = open("runtime_data.json", "w")
    f.write(js)
    f.close()

def type_scan(types, dir_list):
    """ Perform a scan of the directories against the supplied types.
        The extensions are counted and junk files can be removed automatically.

    Args:
        types (_type_): _description_
        dir_list (_type_): _description_
    """
    global runtime_data
    run_stamp = str(int(time.time()))
    counts = {}
    other_counts = {}
    for t in types:
        counts[t] = 0
    for m_dir in runtime_data[dir_list]:
        for root, dirs, files in os.walk(m_dir):
            for f in files:
                path = os.path.join(root, f)
                name, ext = os.path.splitext(path)
                head, tail = os.path.split(path)
                if ext in types:
                    counts[ext] += 1
                    #print(path)
                else:
                    if ext in other_counts:
                        other_counts[ext] += 1
                    else:
                        other_counts[ext] = 1

                    if ext in JUNK_FILES:
                        if KEEP_JUNK:
                            shutil.move(path, JUNK_FOLDER + tail.removesuffix(ext) + "_" + run_stamp + ext)

    print("Found:")
    count_list = []
    for key in counts:
        count_list.append((key, counts[key]))
    count_list.sort(key=lambda x: x[1], reverse=True)
    for item in count_list:
        print("  " + item[0] + ":  " + str(item[1]))

    print("With other types:")
    other_count_list = []
    for key in other_counts:
        other_count_list.append((key, other_counts[key]))
    other_count_list.sort(key=lambda x: x[1], reverse=True)
    for item in other_count_list:
        print("  " + item[0] + ":  " + str(item[1]))
    #print("With other data:")
    #print(other_counts)
    #for key in othercounts:
    #    print(key + ": " + str(othercounts[key]))

def scan_m():
    print("====================")
    print("Beginning music scan")
    type_scan({'.flac', '.m4a', '.mp3', '.wav'}, 'm_dirs')
    print("====================")

def scan_v():
    print("====================")
    print("Beginning video scan")
    type_scan({'.mkv', '.mp4'}, 'v_dirs')
    print("====================")

def scan():
    scan_m()
    scan_v()

runtime_data = {}

def main():

    if KEEP_JUNK and not path.exists(JUNK_FOLDER):
        os.mkdir(JUNK_FOLDER)

    if path.exists("runtime_data.json"):
        load_json()
        print("-] Loading previous runtime data")
    
    if 'm_dirs' not in runtime_data:
        runtime_data['m_dirs'] = []

    if 'v_dirs' not in runtime_data:
        runtime_data['v_dirs'] = []

    query = ""
    while query != 'quit':
        query = input("> ").lower().strip()
        query_split = query.split(' ')

        # Add m directory
        if query_split[0] in {'addmdir', 'amd'}:
            if len(query_split) < 2:
                print("!] Missing directory parameter")
            elif os.path.isdir(query.split(' ', 1)[1]):
                if query.split(' ', 1)[1] in runtime_data['m_dirs']:
                    print("!] Directory has already been added")
                else:
                    runtime_data['m_dirs'].append(query.split(' ', 1)[1])
                    save_json()
                    print('-] Added directory')
            else:
                print('!] Invalid directory "' + query.split(' ', 1)[1] + '"')

        # Add v directory
        elif query_split[0] in {'addvdir', 'avd'}:
            if len(query_split) < 2:
                print("!] Missing directory parameter")
            elif os.path.isdir(query.split(' ', 1)[1]):
                if query.split(' ', 1)[1] in runtime_data['v_dirs']:
                    print("!] Directory has already been added")
                else:
                    runtime_data['v_dirs'].append(query.split(' ', 1)[1])
                    save_json()
                    print('-] Added directory')
            else:
                print('!] Invalid directory "' + query.split(' ', 1)[1] + '"')

        # Clear terminal
        elif query in {'clear', 'cls'}:
            os.system('cls')

        # View json
        elif query in {'data', 'json'}:
            print(runtime_data)

        # Help
        elif query in {'help'}:
            print("Use command 'list' to see all available commands, and 'help [command]' to get more specific help information")

        elif query_split[0] in {'help'}:
            if query_split[1] in {'addmdir', 'amd'}:
                print("Adds the directory in the first parameter to the music directory list")

            elif query_split[1] in {'addvdir', 'avd'}:
                print("Adds the directory in the first parameter to the video directory list")
            
            elif query_split[1] in {'clear', 'cls'}:
                print("Clears the terminal")

            elif query_split[1] in {'help'}:
                print("o_o")

            elif query_split[1] in {'json', 'data'}:
                print("Prints the contents of the current session's json data")

            else:
                print("!] Unknown help topic '" + query_split[1] + "'")
        # List available commands
        elif query in {'list'}:
            print("Commands:")
            print('addmdir addvdir clear help json list load quit save scan scanm scanv')
            print("Aliases:")
            print("amd[addmdir] avd[addvdir] cls[clear] data[json] exit[quit] export[save] reload[load]")

        # Load json data
        elif query in {'load', 'reload'}:
            load_json()

        # Quit
        elif query in {'quit', 'exit'}:
            save_json()
            break

        # Scan
        elif query in {'scan'}:
            scan()

        elif query in {'scanm'}:
            scan_m()

        elif query in {'scanv'}:
            scan_v()

        # Save json
        elif query in {'export', 'save'}:
            save_json()
            print("-] Saved json data")

        elif query == '':
            continue

        else:
            print("!] Unrecognized command, use 'help' for assistance")

main()

#print(get_files_dir('C://', '.dat'))