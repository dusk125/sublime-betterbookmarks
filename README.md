# BetterBookmarks
BetterBookmarks changes the way the native bookmarks in Sublime Text 3 work. In addition to only allowing one bookmark per line, you can customize different layers for your bookmarks.
## Installation
#### Git Clone
First, find out where the packages directory is by going to (Preferences->Browse Packages), use that location in the git clone command.
#### Package Control
Coming soon!
## Usage
Usage is simple because, basically, BetterBookmarks functions just like the native Sublime Text bookmarks.
* To mark a given selection, run the `better_bookmarks_mark_line` command; even though this command is called bookmark line, it does retain the selection you are bookmarking.
* To cycle between bookmarks run the native `prev_bookmark` and `next_bookmark` Sublime commands.
* To remove all bookmarks on the selected layer, run the `better_bookmarks_clear_marks` command. To remove ALL bookmarks from EVERY layer, run the `better_bookmarks_clear_all_marks` command.
* To cycle between the declared layers, run the `better_bookmarks_swap_layer` command with the direction argument set to which way you want to cycle. A message will be shown at the bottom of the screen, next to the line and column number, as to which layer you are currently on.

## KeyBinding
```
[
  {
    "keys": ["f7"], "command": "better_bookmarks_swap_layer",
    "args": {"direction": "prev"}
  },
  {
    "keys": ["f8"], "command": "better_bookmarks_swap_layer",
    "args": {"direction": "next"}
  },
  { "keys": ["f9"], "command": "prev_bookmark" },
  { "keys": ["f10"], "command": "next_bookmark" },
  {
    "keys": ["f11"], "command": "better_bookmarks_mark_line",
  },
  {
    "keys": ["f12"], "command": "better_bookmarks_clear_marks",
  },
  {
    "keys": ["shift+f12"], "command": "better_bookmarks_clear_all_marks",
  },
]
```
## Settings
automark_functions (true/false): Currently unused.

auto_save_marks (true/false): Should BetterBookmarks save marks on the on_save event.

load_marks_on_load (true/false): Should BetterBookmarks load saved marks on the on_load event.

cleanup_empty_cache_on_close (true/false): Should BetterBookmarks delete mark-files if they are empty when the file is closed.

layer_icons (name : {icon, scope}): What layers should be available in editor. Icon is the path to the icon file. Scope controls the shading of the icon.

default_layer (string): What layer should be selected on start.
#### Example
```
{
	"automark_functions": false,
	"auto_save_marks": true,
	"load_marks_on_load": true,
	"cleanup_empty_cache_on_close": true,
	"layer_icons": {
		"bookmarks": {"icon": "bookmark", "scope": "string"},
		"functions": {"icon": "Packages/BetterBookmarks/icons/function.png", "scope": "comment"},
		"todos": {"icon": "Packages/BetterBookmarks/icons/todo.png", "scope": "comment"},
	},
	"default_layer": "bookmarks",
}
```
## License
Copyright (c) 2015 Allen Ray

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
