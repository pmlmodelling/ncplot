
from ncplot import ncplot
import sys
import os


def main():
    if len(sys.argv) == 1:
        return "Please supply a file"
    ff = sys.argv[1]

    if os.path.exists(ff) == False:
        return f"{ff} does not exist!"

    return ncplot(ff)
    print(ascii_snek)

if __name__ == '__main__':
    main()
