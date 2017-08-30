import sublime
import sublime_plugin
import sys
import os
import json
import codecs
import sys

pkg_path = os.path.dirname(__file__)
if pkg_path not in sys.path:
    sys.path.append(pkg_path)

# if sublime.version().startswith('3'):
#     from .core import LuaFormat
# else:
#     from core import LuaFormat


class LuaFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # check whether the lua files
        suffix_setting = self.view.settings().get('syntax')
        file_suffix = suffix_setting.split('.')[0]
        if file_suffix[-3:].lower() != 'lua': return

        # get content of replacement
        region = sublime.Region(0, self.view.size())
        content = self.view.substr(region)

        # get cursor position before the replacement
        selection = self.view.sel()[0].b
        row, col = self.view.rowcol(selection)

        # replace the content after format
        luaFormatExePath = pkg_path + "/LuaFormat.exe"
        tmpLuaPath = pkg_path + "/tmp.lua"
        orgLuaPath = pkg_path + "/org.lua"
        if os.path.exists(tmpLuaPath):
            os.remove(tmpLuaPath)
        if os.path.exists(orgLuaPath):
            os.remove(orgLuaPath)
        with codecs.open(orgLuaPath,"w","utf-8") as f:
        	f.write(content)
        cmd = '"%s" -i "%s" > "%s"'  % (luaFormatExePath,orgLuaPath,tmpLuaPath)
        data = os.popen(cmd).read()
        with codecs.open(tmpLuaPath,"r","utf-8") as f:
            data = f.read()
            newdata = json.loads(data)
        if not "Text" in newdata:
        	return 
        self.view.replace(edit, region, newdata["Text"])

        # deal cursor position
        selection = self.view.full_line(self.view.text_point(row - 1, 0)).b
        cursor_pos = sublime.Region(selection, selection)
        regions = self.view.sel()
        regions.clear()
        regions.add(cursor_pos)
        sublime.set_timeout_async(lambda: self.view.show_at_center(cursor_pos),
                                  0)

class LuaFormatOnPreSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        view.run_command("lua_format")
