from odoo import api, SUPERUSER_ID, _
from . import models
from . import wizard


def _setup_product_sequence(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    default_product_sequence = env.ref(
        "l10n_rs.sequence_product_product", raise_if_not_found=False
    )
    env["res.company"].search([]).write(
        {
            "product_sequence_id": default_product_sequence.id,
        }
    )
