import os
import re
import subprocess
import time
from Spatter.Configure import *

class CoverageRecordor:
    class SecToCoverage:
        def __init__(self, sec, line_coverage, function_coverage) -> None:
            self.sec = sec
            self.line_coverage = line_coverage
            self.function_coverage = function_coverage
        def __str__(self) -> str:
            return f"{self.sec}, {self.line_coverage}, {self.function_coverage}"
    

    def __init__(self, configure: Configure) -> None:
        self.type = configure.GetName()
        self.init_time = time.localtime()
        name = time.strftime("%Y-%m-%d-%H:%M:%S", self.init_time) 
        coverage_directory = "/log/coverage"
        if not os.path.exists(coverage_directory):
            os.makedirs(coverage_directory)
        
        self.collect = f"lcov -c -d /duckdb_spatial/build/debug -o /log/coverage/spatial-{name}.info"
        self.summary = f"lcov --summary /log/coverage/spatial-{name}.info"
        self.clear_coverage = f"lcov -d ./ -z"
        # self.execute_unit = f"cd /postgis; make check"

        self.sec_to_coverage_list = []
        self.geos_sec_to_coverage_list = []
    

    def ClearBefore(self):
        process = subprocess.Popen(self.clear_coverage, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            print("Error:", error.decode())
            print("what happened in lcov again?")
            exit(0)
    

    def ExecuteUnit(self):
        # export PATH=/usr/local/pgsql/bin:$PATH
        # export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/pgsql/lib/:$LD_LIBRARY_PATH
        current_path = os.environ.get('PATH', '')
        new_path = '/usr/local/pgsql/bin'
        if new_path not in current_path:
            os.environ['PATH'] = f"{new_path}:{current_path}"

        current_ld_path = os.environ.get('LD_LIBRARY_PATH', '')
        new_paths = '/usr/local/pgsql/lib/'
        if new_paths not in current_ld_path:
            os.environ['LD_LIBRARY_PATH'] = f"{new_paths}:{current_ld_path}"
        
        process = subprocess.Popen("find /postgis -name *.gcda", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print(output)

        process = subprocess.Popen(self.execute_unit, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        if process.returncode != 0:
            print("Error:", error.decode())
            print("execute unit error.")
            exit(0)


    def Record(self):
        process = subprocess.Popen(self.collect, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        print(self.collect)
        if process.returncode != 0:
            print("CollectError:", error.decode())
            print("what happened in lcov again?")
            exit(0)
        
        process = subprocess.Popen(self.summary, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 0:
            result_lines = output.decode().split('\n')
            for line in result_lines:
                if "lines" in line:
                    line_coverage = re.findall(r': ([0-9.]+)%', line)[0]
                elif "functions" in line:
                    function_coverage = re.findall(r': ([0-9.]+)%', line)[0]
            t = time.mktime(time.localtime()) - time.mktime(self.init_time)
            sec_to_coverage = self.SecToCoverage(t, line_coverage, function_coverage)
            self.sec_to_coverage_list.append(sec_to_coverage)
        else:
            print("SummaryError:", error.decode())
            print("what happened in lcov again?")
            exit(0)

    def Writefile(self):
        name = time.strftime("%Y-%m-%d-%H:%M:%S", self.init_time) 

        with open(f"log/coverage/postgis-{name}.txt", "w") as of:
            for e in self.sec_to_coverage_list:
                of.write(str(e) + "\n")
    