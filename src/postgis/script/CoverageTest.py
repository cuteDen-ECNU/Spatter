import argparse
import threading
from Spatter.Tester import *

main_complete = False
main_begin = False
d = {
    "name": "coverage-1-hour",
    "geometry_number": 10,
    "smart_generator_on": 0,
    "transformation_on": 1,
    "unit_coverage_on": 0, 
    }

parser = argparse.ArgumentParser(description="")
parser.add_argument("--seed", type=int, default=2, help="set seed for Spatter, default 2")
parser.add_argument("--geometry_number", type=int, default=10, help="geometry number in a single run, default 10")
parser.add_argument("--smart_generator_on", type=int,default=d["smart_generator_on"], help="random-shape strategy if 0. geometry-aware generator if 1. default 1")
parser.add_argument("--transformation_on", type=int, default=d["transformation_on"], help="swith transformation off if 0, default 1")
parser.add_argument("--unit_coverage_on", type=int, default=d["unit_coverage_on"], help="collect coverage of unit test first if 1, default 0")
args = parser.parse_args()

d["geometry_number"] = args.geometry_number
d["smart_generator_on"] = bool(args.smart_generator_on)
d["transformation_on"] = bool(args.transformation_on)
d["unit_coverage_on"] = bool(args.unit_coverage_on)

c = Configure()
c.ReadDict(d)
print(c.GetSmartGeneratorOn())

cr = CoverageRecordor(c)
cr.ClearBefore()
if c.GetUnit() == True:
    cr.ExecuteUnit()

def mainFunc():
    global main_complete
    for i in range(0, 1000000):
        random.seed(i)
        spatter = Spatter(i)
        spatter.Spatter(c)
    main_complete = True

def coverageFunc():
    global cr
    while not main_complete:
        cr.RecordPostGIS()
        cr.RecordGeos()
        cr.Writefile()

if __name__ == '__main__':

    gcov_thread = threading.Thread(target=coverageFunc)
    main_thread = threading.Thread(target=mainFunc)

    gcov_thread.start()
    main_thread.start()

    main_thread.join()
    gcov_thread.join()