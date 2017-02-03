#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .shipment import *

def register():
    Pool.register(
        ShipmentInternal,
        AnullShipmentStart,
        module='nodux_stock_shipment2annulled', type_='model')
    Pool.register(
        AnullShipment,
        module='nodux_stock_shipment2annulled', type_='wizard')
