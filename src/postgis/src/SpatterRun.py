import random
from Spatter.Configure import *
from Spatter.Tester import *

if __name__ == '__main__':
    c = Configure('/log/coverage.conf')
    random.seed(42989)
    spatter = Spatter(42989)
    spatter.Spatter(c)
