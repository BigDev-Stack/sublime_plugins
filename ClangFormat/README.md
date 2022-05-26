a format plugin use clang-format

system path is required to configure

input 'clang-format -v' to check if clang-format is available

support clang-format-settings.json and .clang-format

clang-format-settings.json is a json file to configure ClangFormat plugin,
support 'format_on_save' and 'ignored' options

format_on_save indicates when plugin detect a file is saved, format it
or just put it into the format queue. all request of format will be executed
when you press shortcut key

ignored indicates which folders or files you do not want to format

clang-format-settings.json can be multiple, folder's settings will inherite
settings from its parent(such as, clang-format-settings.json at /a/b/c will inherite
settings specified from clang-format-settings.json at /a or /a/b).when you modify
the clang-format-settings.json, all changes will take effect