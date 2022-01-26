# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_computed_account(self):
        self.ensure_one()
        if (
            self.move_id.move_type == "in_refund"
            and self.company_id.account_vendor_refund_expense_account_id
            and self.env.company.account_fiscal_country_id.code == "RS"
        ):
            return self.company_id.account_vendor_refund_expense_account_id
        else:
            return super(AccountMoveLine, self)._get_computed_account()

    def copy_data(self, default=None):
        result = super(AccountMoveLine, self).copy_data(default=default)
        expense_type = self.env.ref("account.data_account_type_expenses")
        for line in result:
            if (
                self.env.context.get("reverse_moves_wizard", False)
                and line.get("account_id", False)
                and self.company_id.account_vendor_refund_expense_account_id
                and self.env.company.account_fiscal_country_id.code == "RS"
            ):
                account = self.env["account.account"].browse(line["account_id"])
                if account.user_type_id == expense_type:
                    line[
                        "account_id"
                    ] = self.company_id.account_vendor_refund_expense_account_id.id
        return result
