import json
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools.misc import format_date


class AccountPrintTaxRS(models.TransientModel):
    _name = "account.print.tax.l10n.rs"
    _description = "Account Print TAX RS"

    @api.model
    def get_first_open_period(self):
        locked_date = self.env.company._get_user_fiscal_lock_date()
        if locked_date and locked_date != date.min:
            return locked_date + relativedelta(days=1)
        else:
            first_invoice = self.env["account.move"].search(
                [], order="invoice_date asc, id asc", limit=1
            )
            return first_invoice.invoice_date if first_invoice else False

    @api.model
    def _default_date_start(self):
        return self.get_first_open_period()

    @api.model
    def _default_date_end(self):
        first_period = self.get_first_open_period()
        return (
            self.get_first_open_period() + relativedelta(months=1)
            if first_period
            else False
        )

    date_start = fields.Date(
        string="Date from", required=True, default=_default_date_start
    )
    date_end = fields.Date(string="Date to", required=True, default=_default_date_end)

    def print_report(self):
        [data] = self.read()
        data["data"] = self._prepare_report_data()
        return self.env.ref(
            "l10n_rs_reports.action_report_l10n_rs_tax_report"
        ).report_action(None, data=data)

    def calculate_balance(self, lines):
        return round(abs(sum(invoice_line.balance for invoice_line in lines)))

    def _prepare_report_data(self):
        invoices = self.env["account.move"].search(
            [
                ("invoice_date", ">=", self.date_start),
                ("invoice_date", "<", self.date_end),
                ("state", "=", "posted"),
            ]
        )
        company = self.env.company
        result = {
            "date_start": format_date(
                self.env, self.date_start, date_format="dd MM yyyy"
            ),
            "date_end": format_date(self.env, self.date_end, date_format="dd MM yyyy"),
            "vat": company.vat,
            "company_info": "{} {} {} {}".format(
                company.name,
                company.street,
                company.city,
                company.country_id.name,
            ),
            "email": company.email,
        }

        tax_20 = self.env["account.tax"].search(
            [("amount", "=", 20), ("amount_type", "=", "percent")]
        )
        tax_10 = self.env["account.tax"].search(
            [("amount", "=", 10), ("amount_type", "=", "percent")]
        )

        indices = [
            "001",
            "002",
            "003",
            "103",
            "004",
            "104",
            "005",
            "105",
            "006",
            "106",
            "007",
            "107",
            "008",
            "108",
            "009",
            "109",
            "110",
        ]
        for index in indices:
            result[index] = 0.0

        self._prepare_report_data_sales(invoices, result, company, tax_20, tax_10)
        self._prepare_report_data_purchase(invoices, result, company, tax_20, tax_10)

        # 009
        result["009"] = result["006"] + result["007"] + result["008"]

        # 109
        result["109"] = result["106"] + result["107"] + result["108"]

        # 110
        result["110"] = result["105"] - result["109"]

        for index in indices:
            result[index] = round(result[index])

        return result

    def _prepare_report_data_sales(self, invoices, result, company, tax_20, tax_10):
        sale_journals = self.env["account.journal"].search(
            [
                ("type", "=", "sale"),
                "|",
                ("currency_id", "=", company.currency_id.id),
                ("currency_id", "=", False),
            ]
        )
        sale_journals_foreign = self.env["account.journal"].search(
            [
                ("type", "=", "sale"),
                ("currency_id", "!=", company.currency_id.id),
                ("currency_id", "!=", False),
            ]
        )
        down_payment_product = self.env.ref("l10n_rs.l10n_rs_advance_product")

        # 001
        sale_foreign_invoices = invoices.filtered(
            lambda i: i.journal_id in sale_journals_foreign
        )
        for invoice in sale_foreign_invoices:
            result["001"] += invoice.company_currency_total

        # 003
        invoice_line_sale_20 = self.env["account.move.line"].search(
            [
                ("tax_ids", "in", tax_20.ids),
                ("journal_id", "in", sale_journals.ids),
                ("exclude_from_invoice_tab", "=", False),
                ("move_id", "in", invoices.ids),
                ("product_id", "!=", down_payment_product.id),
            ]
        )
        result["003"] = self.calculate_balance(invoice_line_sale_20)

        # 103
        account_103 = self.env["account.account"].search(
            [("code", "in", ("4700", "4720"))]
        )
        invoice_line_103 = self.env["account.move.line"].search(
            [("account_id", "in", account_103.ids), ("move_id", "in", invoices.ids)]
        )
        result["103"] = self.calculate_balance(invoice_line_103)

        # 004
        invoice_line_sale_10 = self.env["account.move.line"].search(
            [
                ("tax_ids", "in", tax_10.ids),
                ("journal_id", "in", sale_journals.ids),
                ("exclude_from_invoice_tab", "=", False),
                ("move_id", "in", invoices.ids),
            ]
        )
        result["004"] = self.calculate_balance(invoice_line_sale_10)

        # 104
        for invoice in invoices.filtered(lambda i: i.journal_id in sale_journals):
            invoice_totals = json.loads(invoice.tax_totals_json)
            for amount_by_group_list in invoice_totals["groups_by_subtotal"].values():
                for amount_by_group in amount_by_group_list:
                    if (
                        amount_by_group["tax_group_id"]
                        in tax_10.mapped("tax_group_id").ids
                    ):
                        result["104"] += amount_by_group["tax_group_amount"]
        result["104"] = round(result["104"])

        # 005
        result["005"] = result["001"] + result["002"] + result["003"] + result["004"]

        # 105
        result["105"] = result["103"] + result["104"]

    def _prepare_report_data_purchase(self, invoices, result, company, tax_20, tax_10):
        purchase_journals = self.env["account.journal"].search(
            [
                ("type", "=", "purchase"),
                "|",
                ("currency_id", "=", company.currency_id.id),
                ("currency_id", "=", False),
            ]
        )

        # 006
        account_2740 = self.env["account.account"].search([("code", "=", "2740")])
        invoice_line_006 = self.env["account.move.line"].search(
            [("account_id", "in", account_2740.ids), ("move_id", "in", invoices.ids)]
        )
        result["006"] = round((self.calculate_balance(invoice_line_006) / 20) * 100)

        # 106
        invoice_line_2740 = self.env["account.move.line"].search(
            [("account_id", "=", account_2740.id), ("move_id", "in", invoices.ids)]
        )
        result["106"] = self.calculate_balance(invoice_line_2740)

        # 008
        invoice_line_purchase_10_20 = self.env["account.move.line"].search(
            [
                "|",
                ("tax_ids", "in", tax_20.ids),
                ("tax_ids", "in", tax_10.ids),
                ("journal_id", "in", purchase_journals.ids),
                ("exclude_from_invoice_tab", "=", False),
                ("move_id", "in", invoices.ids),
            ]
        )
        account_4360 = self.env["account.account"].search([("code", "=", "4360")])
        invoice_line_4360 = self.env["account.move.line"].search(
            [("account_id", "=", account_4360.id), ("move_id", "in", invoices.ids)]
        )
        result["008"] = self.calculate_balance(invoice_line_purchase_10_20)
        result["008"] += abs(self.calculate_balance(invoice_line_4360))

        # 108
        account_108 = self.env["account.account"].search(
            [("code", "in", ("2700", "2710", "2720", "2730"))]
        )
        invoice_line_108 = self.env["account.move.line"].search(
            [("account_id", "in", account_108.ids), ("move_id", "in", invoices.ids)]
        )
        result["108"] = self.calculate_balance(invoice_line_108)
