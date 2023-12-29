#!/usr/bin/env python3

import argparse
import random
from Spatter.Configure import *
from Spatter.Tester import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--completely_random_gen", type=bool, default=False, help="generator is completely random if True, default False")
    parser.add_argument("--transformation_off", type=bool, default=False, help="swith transformation off, default False")
    parser.add_argument("--seed", type=int, default=2, help="set seed for Spatter, default 2")
    args = parser.parse_args()

    # default
    t_off = False 
    seed = 3
    
    d = json.loads('{"coordinates_trans": true, "syntax_trans": true, "name": "pure", "unit": false, "completely_random_gen": false}')
    # from args
    t_off = args.transformation_off
    if t_off == True:
        d["coordinates_trans"] = False
        d["syntax_trans"] = False
    
    d["completely_random_gen"] = args.completely_random_gen
    spatter_seed = args.seed

    c = Configure()
    c.ReadDict(d)
    random.seed(spatter_seed)
    spatter = Spatter(spatter_seed)
    spatter.Spatter(c)
