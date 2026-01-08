%% ------------------ FKP ------------------
run("variables.m")
disp("Forward kinematic problem")
disp(T(1:3), (1:3))
disp(T(1:3, 4))

%% ------------------ IKP ------------------
inv = calc_inverse(T, 1500, 15, 1450, 0, initial_guess);
forward = subs(T, q, inv);
Q = forward(1:3, 1:3);
a = forward(1:3, 4);
disp("Inverse problem for start position")
disp(double(a))
disp(double((trace(Q))))


inv = calc_inverse(T, 1800, 40, 660, 0, initial_guess);
forward = subs(T, q, inv);
Q = forward(1:3, 1:3);
a = forward(1:3, 4);
disp("Inverse problem for end position")
disp(double(a))
disp(double(trace(Q)))

%% ------------------ Plot trajectory ------------------


start_joint = calc_inverse(T, 1500, 15, 1450, 0, initial_guess);
end_joint   = calc_inverse(T, 1800, 40, 660, 0, initial_guess);
plot_joint_positions(start_joint, end_joint)