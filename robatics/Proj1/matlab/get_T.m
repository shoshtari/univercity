function T = get_T(alpha, theta, a_len, b)
    Q = get_Q(alpha, theta);
    a = get_a(a_len, b, theta);
    T = [
        Q, a;
        0 0 0 1
    ];
end

function a = get_a(a_len, b, theta)
    a = [
        a_len*cos(theta);
        a_len*sin(theta);
        b
    ];
end
function Q = get_Q(alpha, theta)
    Q = [
        cos(theta), -sin(theta)*cos(alpha),  sin(theta)*sin(alpha);
        sin(theta),  cos(theta)*cos(alpha), -cos(theta)*sin(alpha);
        0,           sin(alpha),             cos(alpha)
    ];
end
