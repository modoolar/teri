# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class ProductType(models.Model):
    _name = "product.type"

    @api.model
    def get_selection_product_type(self):
        return (
            self.env["product.product"]._fields["type"]._description_selection(self.env)
        )

    name = fields.Char()
    product_type = fields.Selection(
        string="Product type", selection="get_selection_product_type"
    )
