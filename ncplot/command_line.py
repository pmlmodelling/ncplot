
from ncplot import view
import sys
import re
import os

def is_url(x):
    regex = re.compile(
        r"^(?:http|ftp)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return re.match(regex, x) is not None


def main():
    if len(sys.argv) == 1:
        return "Please supply a file"

    for x in sys.argv[1:]:
        if os.path.exists(x):
            ff = x
            break
        if is_url(x):
            ff = x

    if ff is None:
        return f"{ff} does not exist!"

    ff = sys.argv[1]

    return view(ff)



if __name__ == '__main__':
    main()
