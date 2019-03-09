from ranger.gui.colorscheme import ColorScheme
import ranger.gui.color as style
import ranger.gui.context
import ranger.gui.widgets.browsercolumn
from os import getenv
from subprocess import check_output, CalledProcessError


class ls_colors(ColorScheme):
    def __init__(self):
        super(ColorScheme, self).__init__()
        try:
            self.ls_colors = getenv('LS_COLORS',
                                    self.get_default_lscolors()).split(':')
        except (CalledProcessError, FileNotFoundError):
            self.ls_colors = []

        # Gets all the keys corresponding to extensions
        self.ls_colors_extensions = [
            k.split('=')[0] for k in self.ls_colors if k != ''
        ]
        self.ls_colors_extensions = [
            '.' + k.split('*.')[1] for k in self.ls_colors_extensions
            if '*.' in k
        ]

        # Add the key names to ranger context keys
        for key in self.ls_colors_extensions:
            ranger.gui.context.CONTEXT_KEYS.append(key)
            setattr(ranger.gui.context.Context, key, False)

        self.OLD_HOOK_BEFORE_DRAWING = ranger.gui.widgets.browsercolumn.hook_before_drawing

        ranger.gui.widgets.browsercolumn.hook_before_drawing = self.new_hook_before_drawing

        self.ls_colors_keys = [k.split('=') for k in self.ls_colors if k != '']
        self.tup_ls_colors = []

        # Not considering file extensions
        # The order of these two block matters, as extensions colouring should
        # take precedence over file type
        for key in [k for k in self.ls_colors_keys if '.*' not in k]:
            if key[0] == 'fi':
                self.tup_ls_colors += [('file', key[1])]

        # Considering files extensions
        self.tup_ls_colors += [('.' + k[0].split('*.')[1], k[1])
                               for k in self.ls_colors_keys if '*.' in k[0]]

        for key in [k for k in self.ls_colors_keys if '.*' not in k]:
            if key[0] == 'ex':
                self.tup_ls_colors += [('executable', key[1])]
            elif key[0] == 'pi':
                self.tup_ls_colors += [('fifo', key[1])]
            elif key[0] == 'ln':
                self.tup_ls_colors += [('link', key[1])]
            elif key[0] == 'bd' or key[0] == 'cd':
                self.tup_ls_colors += [('device', key[1])]
            elif key[0] == 'so':
                self.tup_ls_colors += [('socket', key[1])]
            elif key[0] == 'di':
                self.tup_ls_colors += [('directory', key[1])]

        self.progress_bar_color = 1

    def new_hook_before_drawing(self, fsobject, color_list):
        for key in self.ls_colors_extensions:
            if fsobject.basename.endswith(key):
                color_list.append(key)

        return self.OLD_HOOK_BEFORE_DRAWING(fsobject, color_list)

    def get_default_lscolors(self):
        """Returns the default value for LS_COLORS
        as parsed from the `dircolors` command
        """
        ls_colors = check_output('dircolors')
        ls_colors = ls_colors.splitlines()[0].decode('UTF-8').split("'")[1]
        return ls_colors

    def get_attr_from_lscolors(self, attribute_list):
        return_attr = 0
        to_del = []

        for i, attr in enumerate(attribute_list):
            attr = int(attr)
            to_del.append(i)
            if attr == 1:
                return_attr |= style.bold
            elif attr == 4:
                return_attr |= style.underline
            elif attr == 5:
                return_attr |= style.blink
            elif attr == 7:
                return_attr |= style.reverse
            elif attr == 8:
                return_attr |= style.invisible
            else:
                to_del.pop(-1)

            return return_attr

    def get_256_background_color_if_exists(self, attribute_list):
        colour256 = False
        for i, key in enumerate(attribute_list):
            if key == '48' and attribute_list[i + 1] == '5':
                colour256 = True
                break
        if colour256 and len(attribute_list) >= i + 3:
            return_colour = int(attribute_list[i + 2])
            del attribute_list[i:i + 3]
            return return_colour
        else:
            return None

    def get_256_foreground_color_if_exists(self, attribute_list):
        colour256 = False
        for i, key in enumerate(attribute_list):
            if key == '38' and attribute_list[i + 1] == '5':
                colour256 = True
                break
        if colour256 and len(attribute_list) >= i + 3:
            return_colour = int(attribute_list[i + 2])
            del attribute_list[i:i + 3]
            return return_colour
        else:
            return None

    def use(self, context):
        fg, bg, attr = style.default_colors

        # Values found from
        # http://www.bigsoft.co.uk/blog/2008/04/11/configuring-ls_colors
        for key, t_attributes in self.tup_ls_colors:
            if getattr(context, key):
                if key == 'executable' and (context.directory or context.link):
                    continue
                t_attributes = t_attributes.split(';')
                colour256_fg = self.get_256_foreground_color_if_exists(
                    t_attributes)
                colour256_bg = self.get_256_background_color_if_exists(
                    t_attributes)
                new_attr = self.get_attr_from_lscolors(t_attributes)
                if new_attr is not None:
                    attr |= new_attr

                # Now only the non-256 colours should be left.
                # Let's fetch them
                colour16_fg, colour16_bg = None, None
                for colour_val in t_attributes:
                    colour_val = int(colour_val)
                    # Basic colours for foreground
                    if (colour_val >= 30 and colour_val <= 37):
                        colour16_fg = colour_val - 30
                    # eight more basic colours
                    elif (colour_val >= 90 and colour_val <= 97):
                        colour16_fg = colour_val - 82

                    # Basic colours for background
                    elif (colour_val >= 40 and colour_val <= 47):
                        colour16_bg = colour_val
                    # eight more basic colours
                    elif (colour_val >= 90 and colour_val <= 97):
                        colour16_bg = colour_val

                if colour256_fg is not None:
                    fg = colour256_fg
                elif colour16_fg is not None:
                    fg = colour16_fg

                if colour256_bg is not None:
                    bg = colour256_bg
                elif colour16_bg is not None:
                    bg = colour16_bg

        if context.reset:
            return style.default_colors
        elif context.in_browser:
            if context.selected:
                attr = style.reverse
            if context.tag_marker and not context.selected:
                attr |= style.bold
                if fg in (style.red, style.magenta):
                    fg = style.white
                else:
                    fg = style.red
                fg += style.BRIGHT
            if not context.selected and (context.cut or context.copied):
                attr |= style.bold
                fg = style.black
                fg += style.BRIGHT
                # If the terminal doesn't support bright colors, use
                # dim white instead of black.
                if style.BRIGHT == 0:
                    attr |= style.dim
                    fg = style.white
            if context.main_column:
                # Doubling up with BRIGHT here causes issues because
                # it's additive not idempotent.
                if context.selected:
                    attr |= style.bold
                if context.marked:
                    attr |= style.bold
                    fg = style.yellow

        return fg, bg, attr
