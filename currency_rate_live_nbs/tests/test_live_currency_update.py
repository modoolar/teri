# Copyright (C) 2020 Modoolar <http://www.modoolar.com>
# @author Petar Najman <petar.najman@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.addons.currency_rate_live.tests import test_live_currency_update


class NBSCurrencyTestCase(test_live_currency_update.CurrencyTestCase):
    def test_live_currency_update_nbs(self):
        self.test_company.currency_provider = "nbs"
        # Testing National Bank of Serbia requires that serbian dinar
        # can be found which is not the case in runbot/demo data
        self.env.ref("base.RSD").write({"active": True})
        rates_count = len(self.currency_usd.rate_ids)
        res = self.test_company.update_currency_rates()
        self.assertTrue(res)
        self.assertEqual(len(self.currency_usd.rate_ids), rates_count + 1)
