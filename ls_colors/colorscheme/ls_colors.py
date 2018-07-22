from ranger.gui.colorscheme import ColorScheme
import ranger.gui.color as style
from os import getenv


class base(ColorScheme):
    progress_bar_color = 1
    ls_colors = getenv('LS_COLORS').split(':')
    if ls_colors is None:
        ls_colors = []

    ls_colors_keys = [k.split('=') for k in ls_colors if k != '']
    tup_ls_colors = [(k[0].split('*.')[1], k[1]) for k in ls_colors_keys
                     if '*.' in k[0]] 

    # Not considering file extensions
    for key in [k for k in ls_colors_keys if '.*' not in k]:
        if key[0] == 'ex':
            tup_ls_colors += [('executable', key[1])]
        elif key[0] == 'pi':
            tup_ls_colors += [('fifo', key[1])]
        elif key[0] == 'ln':
            tup_ls_colors += [('link', key[1])]
        elif key[0] == 'di':
            tup_ls_colors += [('directory', key[1])]

    def get_attr_from_lscolors(self, attr):
        if attr == '00':
            return None
        elif attr == '01':
            return style.bold
        elif attr == '04':
            return style.underline
        elif attr == '05':
            return style.blink
        elif attr == '07':
            return style.reverse
        elif attr == '08':
            return style.invisible

    def use(self, context):
        fg, bg, attr = style.default_colors

        if context.reset:
            return style.default_colors

        elif context.in_browser:
            if context.selected:
                attr = style.reverse
            else:
                attr = style.normal
            if context.empty or context.error:
                fg = 37
                bg = 1
            if context.border:
                fg = 249
            if context.image:
                fg = 160
            if context.video:
                fg = 166
            if context.audio:
                fg = 166
            if context.document:
                fg = 196
            if context.container:
                attr |= style.bold
                fg = 206
            elif context.executable and not \
                    any((context.media, context.container,
                       context.fifo, context.socket)):
                attr |= style.bold
                fg = style.green
            if context.socket:
                fg = 3
                attr |= style.bold
            if context.fifo or context.device:
                fg = 10
                if context.device:
                    attr |= style.bold
            if context.link:
                fg = context.good and 7 or 8
                bg = style.cyan
            if context.bad:
                fg = 1
            if context.tag_marker and not context.selected:
                attr |= style.bold
                if fg in (7, 8):
                    fg = 1
                else:
                    fg = 1
            if not context.selected and (context.cut or context.copied):
                fg = 15
                bg = 8
            if context.main_column:
                if context.selected:
                    attr |= style.bold
                if context.marked:
                    attr |= style.bold
                    fg = 8
            if context.badinfo:
                if attr & style.reverse:
                    bg = 1
                else:
                    fg = 7

        elif context.in_titlebar:
            attr |= style.bold
            if context.hostname:
                fg = context.bad and 8 or 7
            elif context.directory:
                fg = 242
            elif context.tab:
                if context.good:
                    fg = 1
            elif context.link:
                fg = 8

        elif context.in_statusbar:
            if context.permissions:
                if context.good:
                    fg = 7
                elif context.bad:
                    fg = 8
            if context.marked:
                attr |= style.bold | style.reverse
                fg = 8
            if context.message:
                if context.bad:
                    attr |= style.bold
                    fg = 10
            if context.loaded:
                bg = self.progress_bar_color
            if context.vcsinfo:
                fg = 10
                attr &= ~style.bold
            if context.vcscommit:
                fg = 5
                attr &= ~style.bold

        if context.text:
            if context.highlight:
                attr |= style.reverse

        if context.in_taskview:
            if context.title:
                fg = 8

            if context.selected:
                attr |= style.reverse

            if context.loaded:
                if context.selected:
                    fg = self.progress_bar_color
                else:
                    bg = self.progress_bar_color

        if context.vcsfile and not context.selected:
            attr &= ~style.bold
            if context.vcsconflict:
                fg = 11
            elif context.vcschanged:
                fg = 12
            elif context.vcsunknown:
                fg = 210
            elif context.vcsstaged:
                fg = 216
            elif context.vcssync:
                fg = 113
            elif context.vcsignored:
                fg = 141

        elif context.vcsremote and not context.selected:
            attr &= ~style.bold
            if context.vcssync:
                fg = 12
            elif context.vcsbehind:
                fg = 13
            elif context.vcsahead:
                fg = 9
            elif context.vcsdiverged:
                fg = 10
            elif context.vcsunknown:
                fg = 11

        # Values found from 
        # http://www.bigsoft.co.uk/blog/2008/04/11/configuring-ls_colors
        for key, colour in self.tup_ls_colors:
            if getattr(context, key):
                colour = colour.split(';')
                for val in colour:
                    val = int(val)
                    # This is an attribute
                    if val <= 4:
                        k = self.get_attr_from_lscolors(val)
                        if k is not None:
                            attr |= k
                    elif ((val >= 31 and val <= 37)
                          or (val >= 90 and val <= 96)):
                        fg = val
                    elif ((val >= 40 and val <= 47)
                          or (val >= 100 and val <= 106)):
                        bg = val
                    else:
                        fg = val

        # For some reason, my directory background keeps appearing in green.
        if context.directory:
            attr |= style.bold
            fg = 242

        return fg, bg, attr
