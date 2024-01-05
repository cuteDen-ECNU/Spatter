#!/usr/bin/env python3

import argparse
import random

from Spatter.Configure import *
from Spatter.Tester import *

if __name__ == '__main__':
       
    d = {
        "name": "single-run",
        "geometry_number": 10,
        "smart_generator_on": 1,
        "transformation_on": 1,
        "unit_coverage_on": 0, 
        "seed": 2
        }

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--seed", type=int, default=2, help="set seed for Spatter, default 2")
    parser.add_argument("--geometry_number", type=int, default=10, help="geometry number in a single run, default 10")
    parser.add_argument("--smart_generator_on", type=int,default=d["smart_generator_on"], help="generator is completely random if 0, default 1")
    parser.add_argument("--transformation_on", type=int, default=d["transformation_on"], help="swith transformation off if 0, default 1")
    parser.add_argument("--unit_coverage_on", type=int, default=d["unit_coverage_on"], help="collect coverage of unit test first if 1, default 0")
    args = parser.parse_args()
    
    d["geometry_number"] = args.geometry_number
    d["smart_generator_on"] = bool(args.smart_generator_on)
    d["transformation_on"] = bool(args.transformation_on)
    d["unit_coverage_on"] = bool(args.unit_coverage_on)
    d["seed"] = args.seed

    c = Configure()
    c.ReadDict(d)
    

    random.seed(c.GetSeed())
    spatter = Spatter(c.GetSeed())
    spatter.Spatter(c)
