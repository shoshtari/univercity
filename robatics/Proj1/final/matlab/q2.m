
run("variables.m")

%% ------------------ Jacobian ------------------
p = T(1:3,4);         
J = simplify(jacobian(p, q));   % Jacobian in xyz coordinates (not phi)

%% ------------------ Welding Path ------------------
x = 1800;
z = 660;
phi = 0;

y_start = 40;
y_end   = -30;     % 7 cm weld length
N = 5;

y_points = linspace(y_start, y_end, N);

%% ------------------ Inverse Kinematics ------------------
theta = zeros(N,4);
theta0 = initial_guess;   % initial guess

for i = 1:N
    theta(i,:) = calc_inverse(T, x, y_points(i), z, phi, initial_guess); % using theta0 as initial guess didn't work well so against question I used initial_guess
    theta0 = theta(i,:)';
end

%% ------------------ Desired End-Effector Speed ------------------
vy = 0.01;        
V_mid = [0; vy; 0];

theta_dot = zeros(N,4);

for i = 1:N
    J_num = double(subs(J, q, theta(i,:)'));
    
    if i == 1 || i == N
        V = [0;0;0];    % zero speed at start/end
    else
        V = V_mid;
    end
    
    theta_dot(i,:) = pinv(J_num) * V;
end

%% ------------------ Polynomial Trajectory ------------------
T_total = 2;                     % total motion time
t_points = linspace(0,T_total,N);
tau_points = t_points / T_total; % normalized time

t = linspace(0,T_total,200);
tau = t / T_total;

theta_traj = zeros(length(t),4);

deg = 2*N - 1;

for joint = 1:4

    coeffs = sym('a', [1 deg+1]);     % a0 ... an
    s = 0;
    for k = 0:deg
        s = s + coeffs(k+1)*sym('tau')^k;
    end

    ds = diff(s, sym('tau'));

    eqs = sym([]);

    for i = 1:N


        s_pos = (theta(i,joint) - theta(1,joint)) / ...
                (theta(end,joint) - theta(1,joint));

        s_vel = theta_dot(i,joint) / ...
                (theta(end,joint) - theta(1,joint)) * T_total;

        % Position 
        eqs = [eqs;
               subs(s, sym('tau'), tau_points(i)) == s_pos];

        % Velocity 
        eqs = [eqs;
               subs(ds, sym('tau'), tau_points(i)) == s_vel];
    end

    sol = solve(eqs, coeffs);

    s_fun = matlabFunction(subs(s, coeffs, struct2array(sol)));

    for i = 1:length(t)
        theta_traj(i,joint) = ...
            theta(1,joint) + ...
            (theta(end,joint) - theta(1,joint)) * s_fun(tau(i));
    end
end

figure;
for j = 1:4
    subplot(4,1,j)
    plot(t, theta_traj(:,j), 'LineWidth',1.5)
    ylabel(['\theta_' num2str(j)])
    grid on
end
xlabel('Time (s)')

plot_joint_positions_with_trajectory(theta_traj)