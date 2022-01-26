# Copyright (C) 2020 Modoolar <http://www.modoolar.com>
# @author Petar Najman <petar.najman@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import logging

import requests

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

URL = "https://www.modoolar.com/services/nbs/currency_exchange_rates"


class ResCompany(models.Model):
    _inherit = "res.company"

    currency_provider = fields.Selection(
        selection_add=[("nbs", "National Bank of Serbia")],
        ondelete={"nbs": "set default"},
    )

    @api.model
    def create(self, vals):
        """
        Change the default provider depending on the company data.
        """
        if vals.get("country_id") and "currency_provider" not in vals:
            cc = self.env["res.country"].browse(vals["country_id"])
            if cc.code.upper() == "RS":
                vals["currency_provider"] = "nbs"

        return super(ResCompany, self).create(vals)

    @api.model
    def set_special_defaults_on_install(self):
        """
        At module installation, set the default provider depending
        on the company country.
        """

        super(ResCompany, self).set_special_defaults_on_install()

        rs_companies = self.env["res.company"].search([("country_id.code", "=", "RS")])

        if rs_companies:
            rs_companies.write({"currency_provider": "nbs"})

    def _parse_nbs_data(self, available_currencies):
        """
        Parses the data returned in xml by FTA servers and returns it in a more
        Python-usable form.
        :param available_currencies:
        :return:
        """

        if self.env.company.currency_id.name != "RSD":
            return False

        try:
            rates = requests.request("GET", URL).json()
            if not rates.get("success", False):
                _logger.error(
                    "Modoolar NBS service responded with an error: %s",
                    rates.get("error"),
                )
                return False
        except Exception as ex:
            _logger.error(
                "Unexpected error occurred while contacting Modoolar NBS service: %s",
                str(ex),
            )
            return False

        rates_dict = {}
        today = fields.Date.today()
        available_currency_names = available_currencies.mapped("name")

        if "RSD" in available_currency_names:
            rates_dict["RSD"] = (1.0, today)

        for rate in rates["data"]:

            currency_code = rate["code"].upper()
            if currency_code not in available_currency_names:
                continue

            currency_amount = int(rate["unit"])
            currency_rate = float(rate["rate"])

            rates_dict[currency_code] = (currency_amount / currency_rate, today)

        return rates_dict
