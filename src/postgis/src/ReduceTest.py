#!/usr/bin/env python3

import argparse
from Spatter.Log import *
from Spatter.Executor import *
from Spatter.QueriesReduce import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("trigger_case_path", type=str, help="the path of a single trigger case")
    args = parser.parse_args()
    
    trigger_path = args.trigger_case_path
    log = Log(0)
    executor = Executor(log)
    qr = QueriesReducor(executor)
    qr.GetAllQueriesByJson(trigger_path)

    insertErrorBox = InsertErrorBox()
    insertErrorBox.UseAll()
    queryError = ['GEOSOverlaps', 'GeoContains', 'TopologyException', 'This function only accepts LINESTRING as arguments.']        
    qr.SetErrors(insertErrorBox.errors + queryError)

    qr.ExecuteQueries(qr.t0_queries_list)
    qr.Reduce()
