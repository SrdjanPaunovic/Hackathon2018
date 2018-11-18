#!/usr/bin/env python
import sys
import os
import subprocess
import shutil

# KoloTree https://github.com/gknezevic/solution.git
# Tim404 https://github.com/stevanmatovic/hakalaka.git
# AMiTeliHardware https://github.com/miloshunter/hackaton2017-AMiTeliHardware.git
# Cobra Team https://github.com/djordje2192/hackthon2017.git
# ~tilda~ https://github.com/tilda-center/hackathon2017.git
# Team TRV https://github.com/to92me/hackathon2017.git
# HilClimbers https://github.com/Djaps94/hackaton-2017.git
# SyntaxError https://github.com/fivkovic/TyphoonHIL_Hackathon2017.git
# Bit Please https://github.com/stek93/hackathon2017.git
# PyLiman https://github.com/AirmiX/typhoonhil-hackathon2017.git
# NoName https://github.com/bakaja021/typhoon_aip.git
# Code10 https://github.com/lukamaletin/typhoon-hil-hackathon2017.git


if __name__ == '__main__':
    theirs = 'hackathon2017.their'
    os.system('git reset --hard')
    subprocess.run(['git', 'clone', sys.argv[1], theirs])

    # Remove ours requirements file
    os.remove('requirements.txt')
    # Get theirs
    shutil.copyfile(os.path.join(theirs, 'requirements.txt'),
                    'requirements.txt')

    # Remove our hackathon/solution
    shutil.rmtree(os.path.join('hackathon', 'solution'))
    # Get their hackathon/solution
    shutil.copytree(os.path.join(theirs, 'hackathon', 'solution'),
                    os.path.join('hackathon', 'solution'))

    # Remove their repository completely
    if sys.platform.startswith('win'):
        os.system('rmdir /S /Q "{}"'.format(theirs))
    else:
        shutil.rmtree(theirs)

    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

    subprocess.run(['python', 'run.py'])
