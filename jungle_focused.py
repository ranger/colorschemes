from ranger.colorschemes.default import Default
from ranger.gui.color import blue, green, red


class Scheme(Default):
    def use(self, context):
        fg, bg, attr = Default.use(self, context)

        if context.main_column:
            fg = green

        # Copied from ranger.colorschemes.jungle
        if context.in_titlebar and context.hostname:
            fg = red if context.bad else blue

        return fg, bg, attr
