import json

from odoo import _, api, models


class ReportAccountPDVReport(models.AbstractModel):
    _name = "account.pdv.report"
    _description = "PDV Report"
    _inherit = "account.report"

    filter_multi_company = None
    filter_date = {"mode": "range", "filter": "last_month"}
    filter_all_entries = False
    filter_journals = False
    filter_unfold_all = False

    def _get_report_name(self):
        return _("PDV Report")

    def _get_columns_name(self, options):
        columns = [
            {"name": "", "class": "whitespace_print o_account_report_line_ellipsis"},
            {"name": ""},
            {"name": _("Iznos naknade bez PDV"), "class": "number"},
            {"name": ""},
            {"name": _("PDV (u dinarima bez decimala"), "class": "number"},
        ]
        return columns

    def _get_item_line(self, options, name, code1, col1, code2, col2):
        columns = [
            {"name": code1},
            {"name": col1, "class": "number"},
            {"name": code2},
            {"name": col2, "class": "number"},
        ]
        return {
            "id": "pdv_%s" % name,
            "name": "%s" % name,
            "level": 2,
            "columns": columns,
            "unfoldable": False,
        }

    def calculate_balance(self, lines):
        return round(abs(sum(invoice_line.balance for invoice_line in lines)))

    def _get_line_data_001(self, invoices, sale_journals_foreign):
        sale_foreign_invoices = invoices.filtered(
            lambda i: i.journal_id in sale_journals_foreign
        )
        return round(
            sum(invoice.company_currency_total for invoice in sale_foreign_invoices)
        )

    def _get_line_data_003(self, invoices, sale_journals, tax_20, down_payment_product):
        invoice_line_sale_20 = self.env["account.move.line"].search(
            [
                ("tax_ids", "in", tax_20.ids),
                ("journal_id", "in", sale_journals.ids),
                ("exclude_from_invoice_tab", "=", False),
                ("move_id", "in", invoices.ids),
                ("product_id", "!=", down_payment_product.id),
            ]
        )
        return self.calculate_balance(invoice_line_sale_20)

    def _get_line_data_103(self, invoices):
        account_103 = self.env["account.account"].search(
            [("code", "in", ("4700", "4720"))]
        )
        invoice_line_103 = self.env["account.move.line"].search(
            [("account_id", "in", account_103.ids), ("move_id", "in", invoices.ids)]
        )
        return self.calculate_balance(invoice_line_103)

    def _get_line_data_004(self, invoices, sale_journals, tax_10):
        invoice_line_sale_10 = self.env["account.move.line"].search(
            [
                ("tax_ids", "in", tax_10.ids),
                ("journal_id", "in", sale_journals.ids),
                ("exclude_from_invoice_tab", "=", False),
                ("move_id", "in", invoices.ids),
            ]
        )
        return self.calculate_balance(invoice_line_sale_10)

    def _get_line_data_104(self, invoices, sale_journals, tax_10):
        result = 0.0
        for invoice in invoices.filtered(lambda i: i.journal_id in sale_journals):
            invoice_totals = json.loads(invoice.tax_totals_json)
            for amount_by_group_list in invoice_totals["groups_by_subtotal"].values():
                for amount_by_group in amount_by_group_list:
                    if (
                        amount_by_group["tax_group_id"]
                        in tax_10.mapped("tax_group_id").ids
                    ):
                        sign = (
                            1
                            if invoice.move_type in ("out_invoice", "in_refund")
                            else -1
                        )
                        result += amount_by_group["tax_group_amount"] * sign
        result = round(result)
        return result

    def _get_line_data_006(self, invoices):
        account_2740 = self.env["account.account"].search([("code", "=", "2740")])
        invoice_line_006 = self.env["account.move.line"].search(
            [("account_id", "in", account_2740.ids), ("move_id", "in", invoices.ids)]
        )
        result = self.calculate_balance(invoice_line_006)
        result = (result / 20) * 100
        return round(result)

    def _get_line_data_106(self, invoices):
        account_2740 = self.env["account.account"].search([("code", "=", "2740")])
        invoice_line_2740 = self.env["account.move.line"].search(
            [("account_id", "=", account_2740.id), ("move_id", "in", invoices.ids)]
        )
        return self.calculate_balance(invoice_line_2740)

    def _get_line_data_008(self, invoices, purchase_journals, tax_10, tax_20):
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
        result = self.calculate_balance(invoice_line_purchase_10_20)
        return result + abs(self.calculate_balance(invoice_line_4360))

    def _get_line_data_108(self, invoices):
        account_108 = self.env["account.account"].search(
            [("code", "in", ("2700", "2710", "2720", "2730"))]
        )
        invoice_line_108 = self.env["account.move.line"].search(
            [("account_id", "in", account_108.ids), ("move_id", "in", invoices.ids)]
        )
        return self.calculate_balance(invoice_line_108)

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []
        company = self.env.company

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
        purchase_journals = self.env["account.journal"].search(
            [
                ("type", "=", "purchase"),
                "|",
                ("currency_id", "=", company.currency_id.id),
                ("currency_id", "=", False),
            ]
        )
        tax_20 = self.env["account.tax"].search(
            [("amount", "=", 20), ("amount_type", "=", "percent")]
        )
        tax_10 = self.env["account.tax"].search(
            [("amount", "=", 10), ("amount_type", "=", "percent")]
        )

        invoices = self.env["account.move"].search(
            [
                ("invoice_date", ">=", options["date"]["date_from"]),
                ("invoice_date", "<", options["date"]["date_to"]),
                ("state", "=", "posted"),
            ]
        )

        down_payment_product = self.env.ref("l10n_rs.l10n_rs_advance_product")

        lines.append(
            self._get_item_line(options, "PROMET DOBARA I USLUGA", "", "", "", "")
        )
        f001 = self._get_line_data_001(invoices, sale_journals_foreign)
        lines.append(
            self._get_item_line(
                options,
                "Promet dobara i usluga koji je oslobođen PDV"
                " sa pravom na odbitak prethodnog poreza",
                "001",
                f001,
                "",
                "",
            )
        )
        f002 = 0
        lines.append(
            self._get_item_line(
                options,
                "Promet dobara i usluga koji je oslobođen PDV"
                " bez prava na odbitak prethodnog poreza",
                "002",
                f002,
                "",
                "",
            )
        )
        f003 = self._get_line_data_003(
            invoices, sale_journals, tax_20, down_payment_product
        )
        f103 = self._get_line_data_103(invoices)
        lines.append(
            self._get_item_line(
                options,
                "Promet dobara i usluga po opštoj stopi",
                "003",
                f003,
                "103",
                f103,
            )
        )
        f004 = self._get_line_data_004(invoices, sale_journals, tax_10)
        f104 = self._get_line_data_104(invoices, sale_journals, tax_10)
        lines.append(
            self._get_item_line(
                options,
                "Promet dobara i usluga po posebnoj stopi",
                "004",
                f004,
                "104",
                f104,
            )
        )
        f005 = round(f001 + f002 + f003 + f004)
        f105 = round(f103 + f104)
        lines.append(
            self._get_item_line(options, "ZBIR (1+2+3+4)", "005", f005, "105", f105)
        )
        lines.append(self._get_item_line(options, "PRETHODNI POREZ", "", "", "", ""))
        f006 = self._get_line_data_006(invoices)
        f106 = self._get_line_data_106(invoices)
        lines.append(
            self._get_item_line(
                options,
                "Prethodni porez plaćen prilikom uvoza",
                "006",
                f006,
                "106",
                f106,
            )
        )
        f007 = 0
        f107 = 0
        lines.append(
            self._get_item_line(
                options,
                "PDV nadoknada plaćena poljoprivredniku",
                "007",
                f007,
                "107",
                f107,
            )
        )
        f008 = self._get_line_data_008(invoices, purchase_journals, tax_10, tax_20)
        f108 = self._get_line_data_108(invoices)
        lines.append(
            self._get_item_line(
                options,
                "Prethodni porez, osim prethodnog poreza sa red. br. 6. i 7.",
                "008",
                f008,
                "108",
                f108,
            )
        )
        f009 = round(f006 + f007 + f008)
        f109 = round(f106 + f107 + f108)
        lines.append(
            self._get_item_line(options, "ZBIR (6+7+8)", "009", f009, "109", f109)
        )
        lines.append(self._get_item_line(options, "PORESKA OBAVEZA", "", "", "", ""))
        f110 = round(f105 - f109)
        lines.append(
            self._get_item_line(
                options, "Iznos PDV u poreskom periodu (5 - 9)", "", "", "110", f110
            )
        )

        return lines
