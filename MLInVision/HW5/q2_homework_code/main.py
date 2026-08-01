from utils.functions import rosenbrock, rosenbrock_grad_x, rosenbrock_grad_y


def main():
    print("f(1, 1) =", rosenbrock(1, 1))
    print("grad_x(1, 1) =", rosenbrock_grad_x(1, 1))
    print("grad_y(1, 1) =", rosenbrock_grad_y(1, 1))


if __name__ == "__main__":
    main()
