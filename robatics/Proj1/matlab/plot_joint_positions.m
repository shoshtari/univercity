function plot_joint_positions(start_joint, end_joint)
    run("variables.m")

    N = 100;       % number of steps
    t = linspace(0, 1, N);

    % Cubic trajectory (zero velocity at start/end)
    theta_traj = zeros(N, 4);
    for i = 1:4
        theta0 = start_joint(i);
        thetaf = end_joint(i);
        theta_traj(:,i) = theta0 + (thetaf - theta0).*(t);
    end

    joint_positions = zeros(N, 4, 3);

    for k = 1:N
        th = theta_traj(k,:);

        % Individual transforms
        T1_num = double(subs(T1, theta1, th(1)));
        T2_num = double(subs(T2, theta2, th(2)));
        T3_num = double(subs(T3, theta3, th(3)));
        T4_num = double(subs(T4, theta4, th(4)));

        % Cumulative transforms
        T12   = T1_num * T2_num;
        T123  = T12 * T3_num;
        T1234 = T123 * T4_num;

        % Joint positions
        joint_positions(k,1,:) = T1_num(1:3,4)';
        joint_positions(k,2,:) = T12(1:3,4)';
        joint_positions(k,3,:) = T123(1:3,4)';
        joint_positions(k,4,:) = T1234(1:3,4)';
    end

    % 3D plot
    figure; hold on;
    colors = ['r','g','b','k'];
    for j = 1:4
        plot3(squeeze(joint_positions(:,j,1)), ...
              squeeze(joint_positions(:,j,2)), ...
              squeeze(joint_positions(:,j,3)), ...
              'Color', colors(j), 'LineWidth', 2);
    end

    xlabel('X');
    ylabel('Y');
    zlabel('Z');
    title('3D Trajectories of All Joints');
    legend('Joint 1','Joint 2','Joint 3','Joint 4');


    axis equal;
    grid on;
end