#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Waiter.py
  A waiter who looks at a customers financial situation and suggests a
  menu
"""
from decimal import Decimal
import re
import collections

def _check_money(price):
    """Check that we don't have fractions of cent"""
    price = Decimal(str(price))
    return ((price * 100) % 1) == 0

def parse_text_menu(target_function):
    """Decorator:
       Parse a text input menu for the read_customer_request function.
       allows us to easily support more input types in the future
       by adding more decorators
    """
    def call_wrapper(self, text_input):
        if not isinstance(text_input, str):
            raise UserWarning("Menu data should be in String Format")
        price_re = re.compile(r"^(\$)*(\d*(\.\d+)*)$")
        price_target = None
        line_num = -1
        menu_items = []
        for line in text_input.splitlines():
            line_num += 1
            line = line.strip()
            if len(line) == 0:
                #we assume a blank line may be user error and continue
                #in case the rest of the data is correct
                continue

            if price_target is None:
                match = price_re.match(line)
                if (match is None or
                        _check_money(match.group(2)) == False):
                    raise UserWarning(
                        "Invalid target entered: %s, line %s" %
                        (line, line_num))
                price_target = Decimal(match.group(2))
                continue

            menu_item = [x.strip() for x in line.split(',')]
            if len(menu_item) != 2:
                raise UserWarning(
                    "Menu data seems incorrect: %s, line: %s" %
                    (line, line_num))
            match = price_re.match(menu_item[1])
            if match is None or _check_money(match.group(2)) == False:
                raise UserWarning(
                    "Invalid price entered: %s, line %s" %
                    (menu_item[1], line_num))
            menu_items.append(MenuItem(menu_item[0], match.group(2)))
        if price_target is None or len(menu_items) == 0:
            raise UserWarning("Either a price target was ommited or" +
                              " no menu items were listed!")

        return target_function(self, price_target, menu_items)

    return call_wrapper

class MenuItem(object):
    """Simple struct to define menuitems"""
    def __init__(self, name, price):
        self.name = str(name).strip()
        #we convert price to a string to drop any hidden floating point
        #if the argument happened to be a float
        self.price = Decimal(str(price))

    def __repr__(self):
        return "MenuItem(\"%s\",%.2f)" % (self.name, self.price)

    def __str__(self):
        return "%s: $%.2f" % (self.name, self.price)
    
    def __cmp__(self,other):
        if self.price < other.price:
            return -1
        elif self.price > other.price:
            return 1
        #basic string compare
        if self.name < other.name:
            return -1
        elif self.name > other.name:
            return 1
        return 0

class Waiter(object):
    """
    Waiter Class

    """
    def __init__(self):
        self._target_price = None
        self._menu_items = None

    @property
    def target_price(self):
        return self._target_price

    @target_price.setter
    def target_price(self, price):
        if _check_money(price) == False:
            raise UserWarning(
                "Prices with fractions of a penny are not accepted")
        self._target_price = Decimal(str(price))

    @property
    def menu_items(self):
        return self._menu_items

    @menu_items.setter
    def menu_items(self, menu_items):
        for item in menu_items:
            if hasattr(item, 'price') == False:
                raise UserWarning(
                    "All items must have a price to be considered!")
        self._menu_items = menu_items

    @parse_text_menu
    def read_customer_request(self, price_target, menu_item_list=[]):
        """
        this function sets our menu information so the waiter can make
        an order suggestion
        """
        self.target_price = price_target
        self.menu_items = list(menu_item_list)

    def make_suggestion(self, price_target=None):
        """
        This function will find a solution for the the customer based
        on a target price and the list of items previously set
        Intended to use self.target_price but this can be ovveridden
        """
        if price_target is None:
            price_target = self.target_price
        elif _check_money(price_target):
            price_target = Decimal(str(price_target))
        else:
            raise UserWarning("Bad price Target: %s!" % (price_target,))

        if price_target == 0:
            return []
        if len(self.menu_items) == 0:
            return []

        #in the rare case when the item prices are divisable by 1,
        #we dont have to convert them to integers. We spend time doing
        #this check becase it will greatly reduce our solution space
        multiply = 100
        if(price_target % 1 == 0) and (
                0 == len([x for x in self.menu_items if x.price % 1 != 0])):
            multiply = 1
        price_target *= multiply

        #we solve this problem like a standard knapsack problem using
        #dynamic programing and a bottem up traversal of the solution
        #space. Solve time is n*r where r is the price_target.
        #
        #If memory is a concern or we need every solution saved
        #the best we can do is probably a
        #bactrace tree with enumarting the multiple item duplicates
        #into individual items to reduce to a 0-1 knapsack.
        #This would be (n * r)(reduction time) -> (n * r) * r , or nr^2
        #This solution would often run faster becasue we are not
        #solving the entire space, like with DP. The worst case of
        #no solution would be much slower, however
        table = dict()
        table[0] = 0
        TableEntry = collections.namedtuple(
            'TableEntry', 'menu_item back_pointer')
        for item in self.menu_items:
            price = item.price * multiply
            if price_target not in table:
                for target in xrange(price, price_target+1):
                    if target not in table and (target-price) in table:
                        #save the item, and the location of the last
                        #"optimal" solution
                        table[target] = TableEntry(item, target - price)

        if price_target not in table:
            return []
        else:
            #here we walk back across the table to generate the return
            #list. Saving the full list each step above would be faster
            #but much more memory intensive
            solution_list = []
            current_location = price_target
            while current_location != 0:
                solution_list.append(table[current_location].menu_item)
                current_location = table[current_location].back_pointer
            return solution_list

if __name__ == '__main__':
    pass
