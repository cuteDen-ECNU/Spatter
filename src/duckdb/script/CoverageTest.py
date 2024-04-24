import threading
from Spatter.Tester import *
from Spatter.CoverageRecord import *

main_complete = False
main_begin = False
c = Configure()
d = {
    "name": "coverage-1-hour",
    "geometry_number": 10,
    "smart_generator_on": 0,
    "transformation_on": 1,
    "unit_coverage_on": 0, 
    }
c.ReadDict(d)

cr = CoverageRecordor(c)
# cr.ClearBefore()
if c.GetUnit() == True:
    cr.ExecuteUnit()

def mainFunc():
    global main_complete
    global main_begin
    for i in range(0, 1000000):
        random.seed(i)
        spatter = Spatter(i)
        spatter.Spatter(c)
        main_begin = True
    main_complete = True

def coverageFunc():
    global cr

    while not main_complete:
        cr.Record()
        cr.Writefile()

if __name__ == '__main__':

    gcov_thread = threading.Thread(target=coverageFunc)
    main_thread = threading.Thread(target=mainFunc)

    gcov_thread.start()
    main_thread.start()

    main_thread.join()
    gcov_thread.join()