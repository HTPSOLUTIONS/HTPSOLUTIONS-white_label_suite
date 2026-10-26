import logging

from odoo import models
from odoo.tools.template_inheritance import locate_node

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    def apply_inheritance_specs(self, source, specs_tree, *args, **kwargs):
        """White Label views only: when another module already removed what a White Label view changes
        (another debranding module, for instance), skip that change instead of breaking the whole page."""
        if len(self) != 1 or not (self.key or '').startswith('htp_white_label'):
            return super().apply_inheritance_specs(source, specs_tree, *args, **kwargs)
        specs = list(specs_tree) if specs_tree.tag == 'data' else [specs_tree]
        for spec in specs:
            if not isinstance(spec.tag, str):  # comments
                continue
            if spec.tag != 'data' and locate_node(source, spec) is None:
                _logger.info("%s: %s not found (removed by another module), skipped",
                             self.key, spec.get('expr') or spec.tag)
                continue
            source = super().apply_inheritance_specs(source, spec, *args, **kwargs)
        return source
