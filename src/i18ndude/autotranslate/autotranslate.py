# encoding: utf-8
from handler import find_untranslated

import argparse


def main():
    parser = argparse.ArgumentParser(description='Auto translate')
    parser.add_argument('path', type=str,
                        help='Path. Example: /Users/Francois/templates')
    args = parser.parse_args()
    find_untranslated([args.path])
