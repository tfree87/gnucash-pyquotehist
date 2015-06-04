#!/usr/bin/env/python

# 
# Copyright (C) 2015  Thomas Freeman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#Built-in modules
import argparse
from gnucash import Session, Account, Split
import gnucash
from fractions import Fraction
from pandas.io.data import DataReader
from datetime import datetime
from datetime import timedelta

def get_prices(security):
    """Gets a stock price DataFrame from Yahoo"""
    start_date = datetime(1900, 1, 1)
    end_date = datetime.today()
    result = DataReader(security, 'yahoo', start_date, end_date)
    return result

def main(filename, namespace, security):
    """The main function"""
    url = "xml://" + filename
    stock_price = get_prices(security)
    
    # Initialize Gnucash session
    session = Session(url, True, False, False)
    book = session.book
    commod_table = book.get_table()
    stock = commod_table.lookup(namespace, security)
    currency = commod_table.lookup('CURRENCY', 'USD')
    pricedb = book.get_price_db()
    price_list = pricedb.get_prices(stock,currency)

    if len(price_list)<1:
        print('Need at least one database entry to clone ...')

	# Delete all the old price entries except for the first
    pl0 = price_list[0]
    for i in range(0,len(price_list)):
        pricedb.remove_price(price_list[i])

    print(stock_price.index)
    for item in stock_price.index:
        p_new = pl0.clone(book)
        p_new = gnucash.GncPrice(instance=p_new)
        string = "Adding {} {}".format(item, stock_price["Close"][item.strftime("%Y-%m-%d")])
        print(string)
        # Add stock date formatted as year/month/day
        p_new.set_time(item)
        v = p_new.get_value()
        v.num = int(Fraction.from_float(stock_price["Close"][item.strftime("%Y-%m-%d")]).limit_denominator(100000).numerator)
        v.denom = int(Fraction.from_float(stock_price["Close"][item.strftime("%Y-%m-%d")]).limit_denominator(100000).denominator)
        p_new.set_value(v)
        pricedb.add_price(p_new)

    # Clean up
    session.save()
    session.end()
    session.destroy()


def parse_arguments():
    """Get arguments from command line and store them as a variable"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "filename",
        help="Name of the gnucash file"
    )
    parser.add_argument(
        "namespace",
        help="The namespace of the security"
    )
    parser.add_argument(
        "security",
        help="The name of the security to get price information for"
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_arguments()
    main(args.filename, args.namespace, args.security)
        
