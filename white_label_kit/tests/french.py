"""Shared helper: inherited templates must also apply on the translated (French) parent templates."""
from lxml import etree


def combined_arch_in_french(test, xmlids, modules):
    """Activate French, load the translations of ``modules`` and return the combined archs (French) of ``xmlids``."""
    env = test.env
    env['res.lang']._activate_lang('fr_FR')
    env['ir.module.module']._load_module_terms(modules, ['fr_FR'], overwrite=True)
    result = {}
    for xmlid in xmlids:
        view = env.ref(xmlid).with_context(lang='fr_FR')
        result[xmlid] = etree.tostring(view._get_combined_arch(), encoding='unicode')
    return result
