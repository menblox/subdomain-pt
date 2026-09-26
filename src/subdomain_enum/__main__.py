"""Точка входа: python -m subdomain_enum <команда> <домен>"""

import sys

from subdomain_enum.cli import main

if __name__ == "__main__":
    sys.exit(main())
