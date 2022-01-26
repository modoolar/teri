# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class ResCompany(models.Model):
    """ Added fields for serbian accounting """

    _inherit = "res.company"

    account_foreign_payable_id = fields.Many2one(
        comodel_name="account.account", string="Foreign Payable Account"
    )
    account_foreign_receivable_id = fields.Many2one(
        comodel_name="account.account", string="Foreign Receivable Account"
    )
    account_vendor_refund_expense_account_id = fields.Many2one(
        comodel_name="account.account", string="Vendor Refund Expense Account"
    )
    service_product_income_account_group_id = fields.Many2one(
        comodel_name="account.group",
        string="Default income account group for service products",
    )
    product_product_income_account_group_id = fields.Many2one(
        comodel_name="account.group",
        string="Default income account group for storable and consumable products",
    )
    down_payment_product_income_account_group_id = fields.Many2one(
        comodel_name="account.group",
        string="Default income account group for down payment products",
    )
    expense_account_group_id = fields.Many2one(
        comodel_name="account.group", string="Default expense account group"
    )
    generate_product_reference = fields.Boolean(
        string="Automatically generate product reference"
    )
    product_sequence_id = fields.Many2one(
        comodel_name="ir.sequence",
        string="Product Sequence",
        default=lambda self: self.env.ref(
            "l10n_rs.sequence_product_product", raise_if_not_found=False
        ),
    )
