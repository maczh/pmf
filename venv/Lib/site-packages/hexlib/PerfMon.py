import time

from datetime import datetime

class PerfMon():
    def __init__(self, label="") -> None:
        self.label = label
        self.startTime = time.time()

    def printExecutionTime(self):
        end = time.time()
        print("----------")
        print("         Label: " + self.label)
        print("      Datetime: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")) 
        print("Execution Time: " + str(end-self.startTime)[0:8] + " sec")
        print("----------")      