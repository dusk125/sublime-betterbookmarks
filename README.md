# BetterBookmarks
BetterBookmarks changes the way the native bookmarks in Sublime Text 3 work. In addition to only allowing one bookmark per line, you can customize different layers for your bookmarks.
## Installation
#### Git Clone
First, find out where the packages directory is by going to (Preferences->Browse Packages), use that location in the git clone command.
#### Package Control
Install from Package Control [here](https://packagecontrol.io/packages/Better%20Bookmarks).
## Usage
Usage is simple because, basically, BetterBookmarks functions just like the native Sublime Text bookmarks. All available commands are called using the Text Command `better_bookmarks`.
#### Available Commands
* To mark a given selection, add `"args": {"subcommand": "mark_line"}`
* To cycle between bookmarks run the native `prev_bookmark` and `next_bookmark` Sublime commands.
* To remove all bookmarks on the selected layer, add `"args": {"subcommand": "clear_marks"}`. To remove ALL bookmarks from EVERY layer, add `"args": {"subcommand": "clear_all"}`.
* To cycle between the declared layers, add `"args": {"subcommand": "layer_swap", "direction": "<direction>"}` and replace `<direction>` with either `prev` or `next`.

## KeyBinding
```
[
	{
		"description": "Swaps the layers backwards.",
		"keys": ["f7"], "command": "better_bookmarks",
		"args": {"direction": "prev", "subcommand": "layer_swap"}
	},
	{
		"description": "Swaps the layers forwards.",
		"keys": ["f8"], "command": "better_bookmarks",
		"args": {"direction": "next", "subcommand": "layer_swap"}
	},
	{   
		"description": "Moves the viewport to the previous bookmark in the current visible layer.",
		"keys": ["f9"], "command": "prev_bookmark"
	},
	{
		"description": "Moves the viewport to the next bookmark in the current visible layer.",
		"keys": ["f10"], "command": "next_bookmark"
	},
	{
		"description": "Adds a single bookmark to the current visible layer.",
		"keys": ["f11"], "command": "better_bookmarks",
		"args": {"subcommand": "mark_line"}
	},
	{
		"description": "Removes all marks in the current visible layer.",
		"keys": ["f12"], "command": "better_bookmarks",
		"args": {"subcommand": "clear_marks"}
	},
	{
		"description": "Removes all marks from ALL layers.",
		"keys": ["shift+f12"], "command": "better_bookmarks",
		"args": {"subcommand": "clear_all"}
	},
]
```
## Settings
```
{
	// Should BetterBookmarks print out things to the console (usually unseen by the user) when it's doing caching operations.
	"verbose": true,
	// Should BetterBookmarks save marks on when the current file is saved.
	"cache_marks_on_save": true,
	// Should BetterBookmarks save marks on when the current file is closed.
	"cache_marks_on_close": true,
	// Should BetterBookmarks load saved marks automatically when a file is opened.
	"uncache_marks_on_load": true,
	// If the cache is empty, should BetterBookmarks delete the cached file (for the file being closed).
	"cleanup_empty_cache_on_close": true,
	// What layers should be available in editor. Icon is the path to the icon file. Scope controls the shading of the icon.
	// NOTE: All of those listed in the example can be edited/removed.
	"layer_icons": {
		// This one is the default Sublime bookmark
		"bookmarks": {"icon": "bookmark", "scope": "string"},
		// "functions": {"icon": "Packages/Better Bookmarks/icons/function.png", "scope": "comment"},
		// "todos": {"icon": "Packages/Better Bookmarks/icons/todo.png", "scope": "comment"},
	},
	// What layer should be selected on start.
	"default_layer": "bookmarks",
	/*
	 * Where, if anywhere, should BetterBookmarks show the user what layer they're on when they switch layers. This value can be any combination of the following possible values; you don't have to pick just one!
	 *
	 * Possible values:
	 *    popup: Shows a popup with the name of the currently selected layer at the cursor location.
	 *    temporary: Shows the layer name in the status bar for a brief amount of time.
	 *    permanent: Shows the layer name in the status bar permanently (unless "permanent" is removed from the settings).
	 */
	"layer_status_location": ["permanent"],
	// If true, BetterBookmarks will mark the entire line, or each line in a multi-line selection, instead of marking the exact selection (like Sublime Text does by default).
	"mark_whole_line": false,
	// If true, ignore the order of the selection; this causes the bookmark to always be min->max.
	"ignore_cursor": false
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
