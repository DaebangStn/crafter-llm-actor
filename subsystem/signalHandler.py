from ruamel.yaml import YAML
import signal as sg
import sys


def sigint_handler(_signal, _frame):
    global token_usage_limit
    global configs
    global yaml1

    print('You pressed Ctrl+C!')

    with open("configs.yaml", "w") as f:
        yaml1.dump(configs, f)
        print("configs.yaml updated")

    sys.exit(0)


if __name__ == '__main__':
    sg.signal(sg.SIGINT, sigint_handler)
    print('Press Ctrl+C')

    # Change the value
    sg.pause()
