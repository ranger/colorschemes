'''
    SCRIPT: install.py
    VERSION: v1.0
    DESCRIPTION: Install colorschemes in Ranger's colorscheme module
    AUTHOR: S. Numerius <parvus.mortalis@gmail.com>
    LICENSE: GPL-3.0 (found in `LICENSE`)

    Copr. 2018 S. Numerius. Some rights reserved.
'''

from __future__ import print_function
import argparse
import os
from subprocess import call

parser = argparse.ArgumentParser(
    description='Install colorschemes for the file manager Ranger')
parser.add_argument('scheme', type=str, help='the name of the desired scheme')
parser.add_argument('-c', dest='copy', action='store_true', help='copy files')
parser.add_argument(
    '--ranger-config', dest='config', action='store', default=None,
    help='set ranger\'s config directory')
args = parser.parse_args()

if args.copy:
    cmd = ['cp']
else:
    cmd = ['ln', '-s']

if args.config is not None:
    confDir = args.config
else:
    confDir = os.environ['HOME'] + '/.config/ranger'


def getFolders(choice=None, path=os.path.dirname(os.path.realpath(__file__)), fullPath=True):
    listing = os.listdir(path)
    res = []

    if choice == 'all':
        choice = None

    for name in listing:
        #  full_path = os.path.join(path, name)
        full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path, name)
        if os.path.isdir(full_path) and name != '.git':
            if choice is not None and name != choice:
                continue

            if fullPath:
                res.append(full_path)
            else:
                res.append(name)

    return res


schemes = getFolders(choice=args.scheme)
colors = []
plugins = []

for scheme in schemes:
    for folder in getFolders(path=scheme, choice='colorschemes'):
        colors += [os.path.join(folder, File) for File in os.listdir(folder)]
    if 'plugins' in os.listdir(scheme):
        for folder in getFolders(path=scheme, choice='plugins'):
            plugins += [os.path.join(folder, File) for File in os.listdir(folder)]

for File in colors:
    schemeDir = confDir + '/colorschemes'

    command = cmd.copy()
    command.append(File)
    command.append(schemeDir)

    verb = 'Copying' if args.copy else 'Linking'
    print(verb, 'colorscheme:', File)
    call(command)

for File in plugins:
    schemeDir = confDir + '/plugins'

    command = cmd.copy()
    command.append(File)
    command.append(schemeDir)

    verb = 'Copying' if args.copy else 'Linking'
    print(verb, 'plugin:', File)
    call(command)
