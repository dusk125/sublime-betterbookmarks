# BetterBookmarks
BetterBookmarks extends the built-in Sublime Text 3 bookmarking system to allow for persistent bookmarks and bookmark layers.
## Installation
#### Git Clone
First, find out where the packages directory is by going to (Preferences->Browse Packages), use that location in the git clone command.
#### Package Control
Install from Package Control [here](https://packagecontrol.io/packages/Better%20Bookmarks).
## Usage
The easiest way to use this plugin is with the default keymap (see the [KeyBinding][KeyBinding] section).
#### Available Commands
All listed commands are subcommands of the `better_bookmarks` command.

* To mark a given selection, add `"args": {"subcommand": "mark_line"}`
* To cycle between bookmarks run the native `prev_bookmark` and `next_bookmark` Sublime commands.
* To remove all bookmarks on the selected layer, add `"args": {"subcommand": "clear_marks"}`. To remove ALL bookmarks from EVERY layer, add `"args": {"subcommand": "clear_all"}`.
* To cycle between the declared layers, add `"args": {"subcommand": "layer_swap", "direction": "<direction>"}` and replace `<direction>` with either `prev` or `next`.

## KeyBinding
```
The following are the bindings from the default keymap.

Swap layers backwards

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
		"keys": ["f9"], "command": "prev_bookmark",
		"args": {"name": "better_bookmarks"}
	},
	{
		"description": "Moves the viewport to the next bookmark in the current visible layer.",
		"keys": ["f10"], "command": "next_bookmark",
		"args": {"name": "better_bookmarks"}
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
	}
]
```
## Settings
```
// Should BetterBookmarks print out things to the console (usually unseen by the user) when it's doing caching operations.
"verbose": false,

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

/*
 * How should marking behave.
 *
 * Possible values:
 *    selection:  Adds one bookmark for an entire selection.
 *                Overlapping selections will combine to form a larger mark.
 *    line: Toggles a mark on each line of the selection.
 */
"marking_mode": "selection",

// If true, ignore the order of the selection; this causes the bookmark to always be min->max.
"ignore_cursor": false
```
