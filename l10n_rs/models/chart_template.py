# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import _, api, fields, models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    bank_account_code_prefix_foreign = fields.Char(
        string="Prefix of the foreign bank accounts"
    )
    property_account_receivable_foreign_id = fields.Many2one(
        comodel_name="account.account.template", string="Foreign Receivable Account"
    )
    property_account_payable_foreign_id = fields.Many2one(
        comodel_name="account.account.template", string="Foreign Payable Account"
    )
    property_account_income_categ_foreign_id = fields.Many2one(
        comodel_name="account.account.template",
        string="Category of Foreign Income Account",
    )
    property_account_income_foreign_id = fields.Many2one(
        comodel_name="account.account.template", string="Foreign Income Account"
    )
    property_account_income_categ_storable_id = fields.Many2one(
        comodel_name="account.account.template", string="Product Income Account"
    )
    property_account_income_categ_storable_foreign_id = fields.Many2one(
        comodel_name="account.account.template", string="Product Foreign Income Account"
    )
    property_account_expense_group_id = fields.Many2one(
        comodel_name="account.group.template", string="Account expense group"
    )

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        result = super(AccountChartTemplate, self)._load(
            sale_tax_rate, purchase_tax_rate, company
        )
        if company.account_fiscal_country_id.code == "RS":
            account_foreign_payable_id = self.env["account.account"].search(
                [
                    ("code", "=", "4360"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.account_foreign_payable_id = account_foreign_payable_id
            account_foreign_receivable_id = self.env["account.account"].search(
                [
                    ("code", "=", "2050"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.account_foreign_receivable_id = account_foreign_receivable_id
            account_vendor_refund_expense_account_id = self.env[
                "account.account"
            ].search(
                [
                    ("code", "=", "6779"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.account_vendor_refund_expense_account_id = (
                account_vendor_refund_expense_account_id
            )
            account_expense_group_id = self.env["account.group"].search(
                [
                    ("code_prefix_start", "=", "5"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.expense_account_group_id = account_expense_group_id
            service_income_account_group_id = self.env["account.group"].search(
                [
                    ("code_prefix_start", "=", "614"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.service_product_income_account_group_id = (
                service_income_account_group_id
            )
            product_income_account_group_id = self.env["account.group"].search(
                [
                    ("code_prefix_start", "=", "604"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.product_product_income_account_group_id = (
                product_income_account_group_id
            )
            down_payment_income_account_group_id = self.env["account.group"].search(
                [
                    ("code_prefix_start", "=", "430"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.down_payment_product_income_account_group_id = (
                down_payment_income_account_group_id
            )
            account_currency_exchange_id = self.env["account.account"].search(
                [
                    ("code", "=", "5630"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            company.currency_exchange_journal_id.default_account_id = (
                account_currency_exchange_id
            )
            account_tax_pdv_20_advance = self.env["account.tax"].search(
                [
                    ("name", "=", "PDV 20% avans"),
                    ("type_tax_use", "=", "sale"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            account_income_down_payment = self.env["account.account"].search(
                [
                    ("code", "=", "4300"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            account_expense_down_payment = self.env["account.account"].search(
                [
                    ("code", "=", "1500"),
                    ("company_id", "=", self.env.user.company_id.id),
                ]
            )
            self.env.ref("l10n_rs.l10n_rs_advance_product").write(
                {
                    "taxes_id": [(6, 0, [account_tax_pdv_20_advance.id])],
                    "property_account_income_id": account_income_down_payment,
                    "property_account_expense_id": account_expense_down_payment,
                }
            )

        return result

    @api.model
    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(
            acc_template_ref, company, journals_dict
        )

        if company.account_fiscal_country_id.code == "RS":

            eur_currency = self.env.ref("base.EUR")

            account_5509 = self.env["account.account"].search(
                [
                    ("code", "=", "5509"),
                    ("company_id", "=", company.id),
                ]
            )
            account_2440 = self.env["account.account"].search(
                [
                    ("code", "=", "2440"),
                    ("company_id", "=", company.id),
                ]
            )
            account_241010 = self.env["account.account"].search(
                [
                    ("code", "=", "241010"),
                    ("company_id", "=", company.id),
                ]
            )
            account_6150 = self.env["account.account"].search(
                [
                    ("code", "=", "6150"),
                    ("company_id", "=", company.id),
                ]
            )

            for journal in journal_data:
                if journal["type"] == "purchase":
                    journal.update(
                        {
                            "default_account_id": account_5509.id,
                        }
                    )

            bank_journal_eur_vals = {
                "name": _("Bank journal EUR"),
                "type": "bank",
                "code": "BNKE",
                "company_id": company.id,
                "currency_id": eur_currency.id,
                "default_account_id": account_2440.id,
                "suspense_account_id": account_241010.id,
                "show_on_dashboard": True,
            }
            customer_invoice_foreign_vals = {
                "name": _("Customer invoice Foreign"),
                "type": "sale",
                "code": "INVF",
                "default_account_id": account_6150.id,
                "company_id": company.id,
                "show_on_dashboard": True,
            }
            vendor_bill_foreign_vals = {
                "name": "Vendor Bill Foreign",
                "type": "purchase",
                "code": "BILF",
                "default_account_id": account_5509.id,
                "company_id": company.id,
                "show_on_dashboard": True,
            }

            journal_data.append(bank_journal_eur_vals)
            journal_data.append(customer_invoice_foreign_vals)
            journal_data.append(vendor_bill_foreign_vals)

        return journal_data

    @api.model
    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        result = super(
            AccountChartTemplate, self.with_context(skip_account_generation=True)
        ).generate_journals(acc_template_ref, company, journals_dict)
        return result

    def _create_bank_journals(self, company, acc_template_ref):
        result = super(
            AccountChartTemplate, self.with_context(skip_account_generation=True)
        )._create_bank_journals(company, acc_template_ref)
        return result
