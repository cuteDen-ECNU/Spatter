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
        
        self.collect_postgis = f"lcov -c -d /postgis -o /log/coverage/postgis-{name}.info"
        self.collect_geos = f"lcov -c -d /geos -o /log/coverage/geos-{name}.info"
        self.summary_postgis = f"lcov --summary /log/coverage/postgis-{name}.info"
        self.summary_geos = f"lcov --summary /log/coverage/geos-{name}.info"
        self.clear_coverage = f"lcov -d ./ -z"
        self.execute_unit = f"cd /postgis; make check"

        self.postgis_sec_to_coverage_list = []
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


    def RecordPostGIS(self):
        process = subprocess.Popen(self.collect_postgis, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode != 0:
            print("Error:", error.decode())
            print("what happened in lcov again?")
            exit(0)
        
        process = subprocess.Popen(self.summary_postgis, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
            self.postgis_sec_to_coverage_list.append(sec_to_coverage)
        else:
            print("Error:", error.decode())
            print("what happened in lcov again?")
            exit(0)

    def RecordGeos(self):
        process = subprocess.Popen(self.collect_geos, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode != 0:
            print("Error:", error.decode())
            print("what happened in lcov again?")
            exit(0)
        
        process = subprocess.Popen(self.summary_geos, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
            self.geos_sec_to_coverage_list.append(sec_to_coverage)
        else:
            print("Error:", error.decode())
            print("what happened in lcov again?")
            exit(0)


    def Writefile(self):
        name = time.strftime("%Y-%m-%d-%H:%M:%S", self.init_time) 

        with open(f"log/coverage/postgis-{name}.txt", "w") as of:
            for e in self.postgis_sec_to_coverage_list:
                of.write(str(e) + "\n")
    
        with open(f"log/coverage/geos-{name}.txt", "w") as of:
            for e in self.geos_sec_to_coverage_list:
                of.write(str(e) + "\n")