
from ncplot import ncplot
import sys
import os


def main():
    if len(sys.argv) == 1:
        return "Please supply a file"

    for x in sys.argv[1:]:
        if os.path.exists(x):
            ff = x
            break

    if ff is None:
        return f"{ff} does not exist!"

    ff = sys.argv[1]

    return ncplot(ff)



if __name__ == '__main__':
    main()
