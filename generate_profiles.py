from hackathon.energy.energy_math import gen_profile
from hackathon.utils.utils import *
import json

__author__ = "Dusan Majstorovic"
__copyright__ = "Typhoon HIL Inc."
__license__ = "MIT"


def generate_profiles():
    # Training profiles
    LOAD_SCALES = [1.0, 0.8, 0.9, 1.2, 0.8]
    SOLAR_SCALES = [1.0, 1.5, 1.2, 0.5, 0.6]
    BLACKOUTS = [[[17.75, 18]],
                 [[12.75, 13.50]],
                 [[2.75, 3]],
                 [[20, 20.50]],
                 [[19.50, 20.50]],
                 ]

    PROFILES = []

    # used to smoothen out the load PROFILES on day transitions
    LOAD_SCALING_PREV = 1.0

    for i in CFG.days:
        n = i-1
        to_write, profile = gen_profile(CFG.sampleRate,
                                        load_scaling=LOAD_SCALES[n],
                                        load_scaling_prev=LOAD_SCALING_PREV,
                                        solar_scaling=SOLAR_SCALES[n],
                                        blackouts=BLACKOUTS[n])
        PROFILES += profile
        LOAD_SCALING_PREV = LOAD_SCALES[n]

    with open(CFG.profile_file, 'w') as f:
        f.write(json.dumps(PROFILES))

    print('Profile is generated in {}'.format(CFG.profile_file))


if __name__ == '__main__':
    generate_profiles()
