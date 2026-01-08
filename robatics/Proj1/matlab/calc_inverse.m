
function theta_sol = calc_inverse(T, x, y, z, phi, initial_guess)
    syms theta1 theta2 theta3 theta4 real
    symbols = [theta1 theta2 theta3 theta4];

    Q = T(1:3, 1:3);
    a = T(1:3, 4);

    phi_p = trace(Q);

    eqs = [
        a(1) - x;
        a(2) - y;
        a(3) - z;
        phi_p - phi;
    ];

    eq_fun = matlabFunction(eqs, 'Vars', {symbols});
    options = optimoptions('fsolve', ...
        'Algorithm','trust-region-dogleg', ...
        'Display','off', ...
        'FunctionTolerance',1e-9, ...
        'StepTolerance',1e-9);
    theta_sol = fsolve(@(th) eq_fun(th), initial_guess, options);
    theta_sol = transpose(theta_sol);
    theta_sol = mod(theta_sol , 2 * pi);
end