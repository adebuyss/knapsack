#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Cafe
# Soulution to xkcd #287 where a waiter is given a
# price, and needs to provide a menu exactly equal
# to that price
#

from argparse import ArgumentParser as AP
import os.path
from Waiter import Waiter

def is_valid_file(parser, arg):
    """Check to make sure the location is valid"""
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return open(arg, 'r')  # return an open file handle

def main():
    parser = AP(description=
                "Look at a menu and price and suggest options")
    parser.add_argument('-f', dest="filename", required=True,
                        help="Input file including the target price and menu",
                        metavar="FILE",
                        type=lambda x: is_valid_file(parser, x))
    args = parser.parse_args()

    menu_string = "".join(args.filename.readlines())
    try:
        waiter = Waiter()
        waiter.read_customer_request(menu_string)
        suggestion = waiter.make_suggestion()
    except UserWarning as e:
        print e
        return -1

    print "Our Menu:"
    print "---------"
    for item in waiter.menu_items:
        print item
    print "---------"
    print "\nYour target price is: $%.2f\n" % waiter.target_price

    if len(suggestion) == 0:
        print "There is no selection that would meet the target price"
    else:
        print "Our suggested meal:"
        suggestion.sort()
        last_item = None
        number = 0
        for menu_item in suggestion:
            if last_item is None:
                last_item = menu_item
                number += 1
            elif last_item == menu_item:
                number += 1
            else:
                print "%dx %sea" % (number, last_item)
                number = 1
                last_item = menu_item
        print "%dx %sea" % (number, last_item)

    return 0

if __name__ == '__main__':
    main()

