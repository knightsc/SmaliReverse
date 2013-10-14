import collections
import os
import re
import sublime, sublime_plugin

HISTORY_SIZE = 64
jump_history_by_window = {}  # map of window id -> collections.deque([], HISTORY_SIZE)

# as we jump to files check here first so we don't
# have to scan all files
# Might be good to also see if we're jumping within the same file
method_calls = {}

def find_file(path, clazz, method):
    regObj = re.compile('\.class.*' + re.escape(clazz))
    regMeth = re.compile('\.method.* ' + re.escape(method))
    res = []
    name = ''
    number = ''
    for root, dirs, fnames in os.walk(path):
        for fname in fnames:
            filename = os.path.join(root, fname)
            if os.path.isfile(filename):
                with open(filename) as f:
                    i = 1
                    for line in f:
                        # If we've found that we're in the right file
                        if name:
                            if regMeth.search(line):
                                number = str(i)
                                break

                        if regObj.search(line):
                            name = filename

                        i += 1

                    # Don't check anymore files if we find the file
                    if name:
                        break

    if not number:
        number = '1'

    if name:
        encoded_position = '%s:%s' % (name, number)
    else:
        encoded_position = ''

    return encoded_position

class SmaliForwards(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        view = self.view
        window = sublime.active_window()
        file_name = view.file_name()
        encoded_position = ''

        if file_name.endswith('.smali'):
            pos = self.view.sel()[0].begin()
            line = self.view.substr(self.view.line(pos))

            # We only jump on method calls
            if re.match('.*invoke.*->', line):
                # Find file and position of method
                method_call = line[line.find('}')+3:]

                if method_call in method_calls:
                    encoded_position = method_calls[method_call]
                else:
                    clazz, method = method_call.split('->')
                    for folder in window.folders():
                        encoded_position = find_file(folder, clazz, method)
                        if encoded_position:
                            method_calls[method_call] = encoded_position

                if encoded_position:
                    # Save position
                    if window.id() not in jump_history_by_window:
                        jump_history_by_window[window.id()] = collections.deque([], HISTORY_SIZE)

                    jump_history = jump_history_by_window[window.id()]

                    row, col = view.rowcol(pos)
                    current_location = "%s:%d" % (file_name, row + 1)
                    jump_history.append(current_location)

                    # Open the new file
                    window.open_file(encoded_position, sublime.ENCODED_POSITION)

class SmaliBackwards(sublime_plugin.TextCommand):
    def run(self, edit, block=False):
        window = sublime.active_window()
        if window.id() in jump_history_by_window:
            jump_history = jump_history_by_window[window.id()]

            if len(jump_history) > 0:
                previous_location = jump_history.pop()
                window = sublime.active_window()
                window.open_file(previous_location, sublime.ENCODED_POSITION)

class SmaliComment(sublime_plugin.TextCommand):
    def run(self, edit):
        self.edit = edit
        view = self.view
        window = sublime.active_window()
        file_name = view.file_name()

        if file_name.endswith('.smali'):
            pos = self.view.sel()[0].begin()
            line = self.view.substr(self.view.line(pos))
            comment = ''
            parts = line.split('#')

            if len(parts) == 2:
                comment = parts[1].strip()

            window.show_input_panel("Enter Comment:", comment, self.on_done, None, None)

    def on_done(self, comment):
        pos = self.view.sel()[0].begin()
        line_reg = self.view.line(pos)
        line = self.view.substr(line_reg)

        # We might want to do something fancier here were if it's a really long comment we
        # add new lines so it basically word wraps, too complicated though for now

        if comment:
            line = line.ljust(79) + ' # ' + comment
        else:
            line = line.split('#')[0].rstrip()

        self.view.replace(self.edit, line_reg, line)


class SmaliLoad(sublime_plugin.EventListener):
    # We we open folder find public.xml and read the items
    def on_load(self, view):
        # When we open file look for public.xml values in file and replace with name
        # Maybe we just do this as a keybinding so if you see it you can click to follow what it is
        print 'SmaliLoad'

