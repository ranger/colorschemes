# Import the class
import ranger.gui.widgets.browsercolumn
import ranger.gui.context
from os import getenv

ls_colors = getenv('LS_COLORS').split(':')
if ls_colors is None:
    ls_colors = []
ls_colors_keys = [k.split('=')[0] for k in ls_colors if k != '']
ls_colors_keys = [k.split('*.')[1] for k in ls_colors_keys if '*.' in k]

# Add your key names
for key in ls_colors_keys:
    ranger.gui.context.CONTEXT_KEYS.append(key)
    setattr(ranger.gui.context.Context, key, False)
    # code = 'ranger.gui.context.Context.' + key + ' = False'
    # exec(code)

OLD_HOOK_BEFORE_DRAWING = ranger.gui.widgets.browsercolumn.hook_before_drawing


def new_hook_before_drawing(fsobject, color_list):
    for key in ls_colors_keys:
        if fsobject.basename.endswith(key):
            color_list.append(key)

    return OLD_HOOK_BEFORE_DRAWING(fsobject, color_list)


ranger.gui.widgets.browsercolumn.hook_before_drawing = new_hook_before_drawing
