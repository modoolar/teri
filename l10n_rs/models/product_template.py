# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    preferred_type_check = fields.Boolean(
        string="Preferred Type OK", compute="_compute_preferred_type_check"
    )

    def _compute_preferred_type_check(self):
        for record in self:
            record.preferred_type_check = (
                record.type
                in record.categ_id.preferred_product_type.mapped("product_type")
            )

    def generate_automatic_sequence(self):
        sequence_code = (
            self.env.company.product_sequence_id.code
            if self.env.company.product_sequence_id
            else "product.product"
        )
        return self.env["ir.sequence"].next_by_code(sequence_code)
