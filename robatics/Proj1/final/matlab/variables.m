syms theta1 theta2 theta3 theta4 real
q = [theta1; theta2; theta3; theta4];


T1 = get_T(sym(pi)/2,     theta1,  786.71, 260);
T2 = get_T(sym(pi),       theta2,  945,     0);
T3 = get_T(3*sym(pi)/2,   theta3, 1270.15, 251.5);
T4 = get_T(0,        theta4,    0,     0);

T = simplify(T1 * T2 * T3 * T4);

initial_guess = [0.1 0.1 0.1 0.1];
