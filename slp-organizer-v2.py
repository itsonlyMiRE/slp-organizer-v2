'''
PROGRAM:
slp-organizer-v2

AUTHOR:
mire

DESCRIPTION:
Takes directory of Slippi replay files and generates a dictionary
containing metadata from each one (date, user character, opponent character).
'''

import re
import os
import time
import multiprocessing as mp
import glob
from peppi_py import game as Game
#from slippi import Game

NUM_PROCESSES = mp.cpu_count()
SLP_DIR = '/home/mire/Slippi/'  # this will be set by user
MY_CODE = 'MIRE#409'            # this will be set by user

character_index = {
    '0': 'MARIO',
    '1': 'FOX',
    '2': 'CAPTAIN_FALCON',
    '3': 'DONKEY_KONG',
    '4': 'KIRBY',
    '5': 'BOWSER',
    '6': 'LINK',
    '7': 'SHEIK',
    '8': 'NESS',
    '9': 'PEACH',
    '10': 'POPO',
    '11': 'NANA',
    '12': 'PIKACHU',
    '13': 'SAMUS',
    '14': 'YOSHI',
    '15': 'JIGGLYPUFF',
    '16': 'MEWTWO',
    '17': 'LUIGI',
    '18': 'MARTH',
    '19': 'ZELDA',
    '20': 'YOUNG_LINK',
    '21': 'DR_MARIO',
    '22': 'FALCO',
    '23': 'PICHU',
    '24': 'GAME_AND_WATCH',
    '25': 'GANONDORF',
    '26': 'ROY',
    '27': 'MASTER_HAND',
    '28': 'CRAZY_HAND',
    '29': 'WIREFRAME_MALE',
    '30': 'WIREFRAME_FEMALE',
    '31': 'GIGA_BOWSER',
    '32': 'SANDBAG'
}

def write_datafiles(files):
    '''
    Pulls metadata from files in list and writes metadata to .data file for each .slp.
    '''
    for file in files:
        data = pull_metadata(file)
        with open(file+'.data', 'w+') as data_file:
            data_file.write(str(data))

def pull_metadata(filename):
    '''
    Extracts date and characters from Slippi game metadata.
    '''
    metadata = {'date': None, 'mychar': None, 'oppchar': None}
    game = Game(filename, skip_frames=True)['metadata']
    metadata['date'] = re.findall(r'\d\d\d\d-\d\d-\d\d', game['startAt'])[0]
    if game['playedOn'] == 'dolphin':
        chars = ['']*4
        conn_codes = ['']*4
        mychar = ''
        oppchar = ''
        for i in range(len(game['players'].keys())):
            chars[i] = game['players'][str(i)]['characters']
            conn_codes[i] = game['players'][str(i)]['names']['code']
        for i in range(len(conn_codes)):
            if conn_codes[i] == MY_CODE:
                mychar = character_index[list(chars[i].keys())[0]]
            if conn_codes[i] != MY_CODE and conn_codes[i] != '':
                oppchar = character_index[list(chars[i].keys())[0]]
        if mychar != '':
            metadata['mychar'] = mychar
        if oppchar != '':
            metadata['oppchar'] = oppchar
    return metadata

def run():
    '''
    Main run of program.
    '''
    timestamp = time.time()
    slp_files = glob.glob(SLP_DIR+'**/*.slp', recursive=True)
    file_count = len(slp_files)
    group_size = int(file_count/(NUM_PROCESSES-1))
    subgroups = [slp_files[i:i+group_size] for i in range(0, len(slp_files), group_size)]

    # start writing .data files using int(NUM_PROCESSES) processes
    processes = []
    for i in range(len(subgroups)):
        processes.append(mp.Process(target=write_datafiles, args=(subgroups[i],)))
        processes[i].start()
    for process in processes:
        process.join()

    # pull metadata from all .data files into master dictionary
    master_dict = dict.fromkeys(slp_files)
    for i in range(len(slp_files)):
        with open(slp_files[i]+'.data', 'r') as curr_file:
            master_dict[slp_files[i]] = curr_file.readline()

    # remove .data files
    for file in glob.glob(SLP_DIR+'**/*.data', recursive=True):
        os.remove(file)

    # master_dict now contains metadata from every .slp file found in SLP_DIR
    print('\nall .slp replay data collected and ready to be accessed!'
            ,file_count,'files parsed in',round(time.time()-timestamp, 5),'seconds')

if __name__ == '__main__':
    run()
