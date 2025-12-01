import math


def trace(Q):
    trace = 0
    for i in range(3):
        trace += Q[i][i]
    return trace


def vect(Q):
    return [
        Q[2][1] - Q[1][2],
        Q[0][2] - Q[2][0],
        Q[1][0] - Q[0][1]
    ]


def calculate_e_and_phi(Q):
    tr = trace(Q)
    vct = vect(Q)

    phi = math.acos((tr - 1) / 2)

    coef = 1 / (2 * math.sin(phi))
    e = [coef * v for v in vct]
    return trim_numbers(e), phi * 100 // 1 / 100


def calculate_euler_parameter(Q):
    tr = trace(Q)
    q0 = (tr - 1) / 2
    vct = vect(Q)
    q = [i/2 for i in vct]
    return trim_numbers([q0] + q)


def calculate_euler_rodriguez(Q):
    e, phi = calculate_e_and_phi(Q)
    r0 = math.cos(phi / 2)
    coef = math.sin(phi / 2)
    r = [coef * ei for ei in e]
    return trim_numbers([r0] + r)

def trim_numbers(arr):
    ans = []
    for i in arr:
        ans.append(i * 100 // 1 / 100)
    return ans
A = [
    [0.354, -0.612,  0.707],
    [0.927,  0.127, -0.354],
    [0.127,  0.780,  0.612]
]

print("E and phi", calculate_e_and_phi(A))
print("Euler parameter", calculate_euler_parameter(A))
print("Euler-Rodriguez", calculate_euler_rodriguez(A))

