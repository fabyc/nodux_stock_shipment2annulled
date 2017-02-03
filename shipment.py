# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

import collections
import logging
from decimal import Decimal
from trytond.pyson import Eval
from trytond.pyson import Eval, Not, Equal, If, Or, And, Bool, In, Get, Id
from trytond.model import ModelSQL, Workflow, fields, ModelView
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateAction, StateView, StateTransition, \
    Button
from trytond.pool import Pool, PoolMeta

__all__ = ['ShipmentInternal','AnullShipmentStart', 'AnullShipment']
__metaclass__ = PoolMeta

_STATE = [
    ('annulled','Annulled'),
]

class ShipmentInternal:
    'ShipmentInternal'
    __name__ = 'stock.shipment.internal'

    @classmethod
    def __setup__(cls):
        super(ShipmentInternal, cls).__setup__()
        new_sel = [
            ('annulled','Annulled'),
        ]
        if new_sel not in cls.state.selection:
            cls.state.selection.extend(new_sel)

        cls.effective_date.states['readonly'] |= Eval('state') == 'annulled'

        cls._buttons.update({
                'cancel': {
                    'invisible': Eval('state').in_(['cancel', 'done', 'annulled']),
                    },
                'draft': {
                    'invisible': ~Eval('state').in_(['cancel', 'waiting']),
                    'icon': If(Eval('state') == 'cancel',
                        'tryton-clear',
                        'tryton-go-previous'),
                    },
                'wait': {
                    'invisible': ~Eval('state').in_(['assigned', 'waiting',
                            'draft']),
                    'icon': If(Eval('state') == 'assigned',
                        'tryton-go-previous',
                        If(Eval('state') == 'waiting',
                            'tryton-clear',
                            'tryton-go-next')),
                    },
                'done': {
                    'invisible': Eval('state') != 'assigned',
                    },
                'assign_wizard': {
                    'invisible': Eval('state') != 'waiting',
                    'readonly': ~Eval('groups', []).contains(
                        Id('stock', 'group_stock')),
                    },
                'assign_try': {},
                'assign_force': {},
                })

class AnullShipmentStart(ModelView):
    'Anull Shipment Start'
    __name__ = 'stock.anull_shipment.start'


class AnullShipment(Wizard):
    'Anull Shipment'
    __name__ = 'stock.anull_shipment'
    start = StateView('stock.anull_shipment.start',
        'nodux_stock_shipment2annulled.anull_stock_start_view_form', [
            Button('Exit', 'end', 'tryton-cancel'),
            Button('Anull', 'anull_', 'tryton-ok', default=True),
            ])
    anull_ = StateAction('stock.act_shipment_internal_form')

    def do_anull_(self, action):
        pool = Pool()
        ShipmentInternal = pool.get('stock.shipment.internal')
        Move = pool.get('stock.move')
        shipments = ShipmentInternal.browse(Transaction().context['active_ids'])

        for shipment in shipments:
            shipment.state = 'annulled'
            shipment.save()
            move_new = Move()
            for move in shipment.moves:
                move_new.shipment = move.shipment
                move_new.from_location = move.to_location
                move_new.to_location = move.from_location
                move_new.planned_date = move.planned_date
                move_new.cost_price = move.cost_price
                move_new.unit_price = move.unit_price
                move_new.internal_quantity = move.internal_quantity
                move_new.quantity = move.quantity
                move_new.company = move.company
                move_new.currency = move.currency
                move_new.product = move.product
                move_new.origin = move.origin
                move_new.uom = move.uom
                move_new.save()
                print "Pasa aqui"
                Move.do([move_new])
