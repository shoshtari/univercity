function plot_joint_positions_with_trajectory(theta_traj)

    run("variables.m")

    Nt = size(theta_traj,1);
    joint_positions = zeros(Nt,4,3);

    for k = 1:Nt
        th = theta_traj(k,:);

        T1_num = double(subs(T1, theta1, th(1)));
        T2_num = double(subs(T2, theta2, th(2)));
        T3_num = double(subs(T3, theta3, th(3)));
        T4_num = double(subs(T4, theta4, th(4)));

        T12 = T1_num * T2_num;
        T123 = T12 * T3_num;
        T1234 = T123 * T4_num;

        joint_positions(k,1,:) = T1_num(1:3,4)';
        joint_positions(k,2,:) = T12(1:3,4)';
        joint_positions(k,3,:) = T123(1:3,4)';
        joint_positions(k,4,:) = T1234(1:3,4)';
    end

    % Plot joint trajectories in 3D
    figure; hold on;
    colors = {'r','g','b','k'};

    for j = 1:4
        plot3( ...
            joint_positions(:,j,1), ...
            joint_positions(:,j,2), ...
            joint_positions(:,j,3), ...
            'Color',colors{j}, 'LineWidth',2 );
    end

    xlabel('X'); ylabel('Y'); zlabel('Z');
    legend('Joint 1','Joint 2','Joint 3','Joint 4');
    grid on; axis equal;
    view(0,0);   % X–Z plane
end