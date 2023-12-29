import enum
from fractions import Fraction
import numpy as np
import random
import math

class Dimensions(enum.Enum):
    ThreeD = enum.auto()
    TwoD = enum.auto()

def random_fraction_matrix(d: Dimensions, max: int = 20):
# max is relatively prime numbers' max value
    def relatively_prime_numbers():
        n = random.randint(1, max)

        while True:
            m = random.randint(1, max)
            if math.gcd(n, m) == 1:
                break
        return m,n
    
    a1,b1 = relatively_prime_numbers(); x1 = abs(a1**2 - b1**2); y1 = 2*a1*b1; z1 = int(math.sqrt(x1**2 + y1**2))
    a2,b2 = relatively_prime_numbers(); x2 = abs(a2**2 - b2**2); y2 = 2*a2*b2; z2 = int(math.sqrt(x2**2 + y2**2))
    a3,b3 = relatively_prime_numbers(); x3 = abs(a3**2 - b3**2); y3 = 2*a3*b3; z3 = int(math.sqrt(x3**2 + y3**2))

    sinA = Fraction(x1, z1); cosA = Fraction(y1, z1)
    sinB = Fraction(x2, z2); cosB = Fraction(y2, z2)
    sinC = Fraction(x3, z3); cosC = Fraction(y3, z3)
    
    if d == Dimensions.ThreeD:
        m1 = np.array([[sinA, cosA, 0],
                    [cosA, -sinA, 0],
                    [0, 0, 1]])
        m2 = np.array([[1, 0, 0],
                    [0, sinB, cosB],
                    [0, cosB, -sinB]])
        m3 = np.array([[sinC, 0, cosC],
                    [0, 1, 0],
                    [cosC, 0, -sinC]])
        
        return np.dot(np.dot(m1,m2),m3), z1*z2*z3
    
    elif d == Dimensions.TwoD:
        m1 = np.array([[sinA, cosA],
                    [cosA, -sinA]])
        return m1, z1


def Q_2_Affine_param(Q) -> str:
    
    if len(Q) == 2:
        Q_txt = f'{Q[0][0]}, {Q[0][1]}, {Q[1][0]}, {Q[1][1]}, 0, 0'
    elif len(Q) == 3:
        Q_txt = f'{Q[0][0]}, {Q[0][1]}, {Q[0][2]}, {Q[1][0]}, {Q[1][1]}, {Q[1][2]}, {Q[2][0]}, {Q[2][1]}, {Q[2][2]}, 0, 0, 0'
    return Q_txt
