# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class AccountJournal(models.Model):

    _inherit = "account.journal"

    @api.model
    def create(self, vals):
        if (
            vals.get("type", False) == "cash"
            and self.env.company.account_fiscal_country_id.code == "RS"
        ):
            vals["currency_id"] = self.env.ref("base.RSD").id
        result = super(AccountJournal, self).create(vals)
        if (
            self.env.company.account_fiscal_country_id.code == "RS"
            and not self.env.context.get("skip_account_generation", False)
        ):
            result.generate_journal_account()
        return result

    @api.model
    def _fill_missing_values(self, vals):
        if self.env.company.account_fiscal_country_id.code == "RS":
            journal_type = vals.get("type", False)
            currency = vals.get("currency_id", False)
            company = self.env.company

            if journal_type == "cash":
                account_2430 = self.env["account.account"].search(
                    [
                        ("code", "=", "2430"),
                        ("company_id", "=", company.id),
                    ]
                )
                vals["default_account_id"] = account_2430.id
            elif (
                journal_type == "bank"
                and currency
                and currency != self.env.ref("base.RSD").id
            ):
                account_2440 = self.env["account.account"].search(
                    [
                        ("code", "=", "2440"),
                        ("company_id", "=", company.id),
                    ]
                )
                vals["default_account_id"] = account_2440.id
            elif journal_type == "bank":
                account_2410 = self.env["account.account"].search(
                    [
                        ("code", "=", "2410"),
                        ("company_id", "=", company.id),
                    ]
                )
                vals["default_account_id"] = account_2410.id

        result = super(AccountJournal, self)._fill_missing_values(vals)
        return result

    @api.onchange("type")
    def _onchange_type(self):
        result = super()._onchange_type()
        if (
            self.type == "cash"
            and self.env.company.account_fiscal_country_id.code == "RS"
        ):
            self.currency_id = self.env.ref("base.RSD")
        return result

    def generate_journal_account(self):
        rs_chart = self.env.ref("l10n_rs.l10n_rs_chart_template")
        rsd_currency = self.env.ref("base.RSD")
        for record in self:
            code = record.get_account_code_sequence(rs_chart, rsd_currency)
            if not code:
                continue
            account = self.env["account.account"].create(
                {
                    "code": code,
                    "name": record.name,
                    "user_type_id": self.env.ref(
                        "account.data_account_type_liquidity"
                    ).id,
                }
            )
            record.default_account_id = account

    def get_account_code_sequence(self, rs_chart, rsd_currency):
        self.ensure_one()
        code = False
        if self.type == "cash":
            code = "{}{}".format(
                rs_chart.cash_account_code_prefix,
                self.env["ir.sequence"].next_by_code("l10n_rs.account.cash"),
            )
        elif self.type == "bank" and self.currency_id == rsd_currency:
            code = "{}{}".format(
                rs_chart.bank_account_code_prefix,
                self.env["ir.sequence"].next_by_code("l10n_rs.account.bank"),
            )
        elif self.type == "bank" and self.currency_id != rsd_currency:
            code = "{}{}".format(
                rs_chart.bank_account_code_prefix_foreign,
                self.env["ir.sequence"].next_by_code("l10n_rs.account.bank.foreign"),
            )
        return code
