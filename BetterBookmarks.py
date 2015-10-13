import sublime, sublime_plugin, os
import collections
import json

global settings
settings = sublime.load_settings("BetterBookmarks.sublime-settings")

def should_bookmark(view, region):
	bookmarks = view.get_regions("bookmarks")
	line = view.line(region)

	for bookmark in bookmarks:
		if line.contains(bookmark):
			return False

	return True

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)

		directory = "{:s}/User/BetterBookmarks".format(sublime.packages_path())
		if not os.path.exists(directory):
			os.makedirs(directory)
		
		bookmark_cache_name = sublime.expand_variables("${file_base_name}.sublime-settings", sublime.active_window().extract_variables())
		self.bookmark_cache = "BetterBookmarks/{:s}".format(bookmark_cache_name)
		self.cache = sublime.load_settings(self.bookmark_cache)

		self.layers = collections.deque(settings.get("layer_icons"))
		self.layer = settings.get("default_layer")
		self.bookmarks = self.cache.get("Bookmarks")
		if not self.bookmarks:
			self.bookmarks = dict([])
		self.refresh_bookmarks()

	def add_marks(self, list):
		icon = settings.get("layer_icons")[self.layer]["icon"]
		scope = settings.get("layer_icons")[self.layer]["scope"]

		self.view.add_regions("bookmarks", list, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

		self.refresh_bookmarks()

	def refresh_bookmarks(self):
		print(self.bookmarks)
		self.bookmarks[self.layer] = self.view.get_regions("bookmarks")
		print(self.bookmarks)

	def bookmark_line(self, layer, line):
		bookmarks = self.bookmarks
		newMarks = []
		bookmarkFound = False

		if not layer == self.layer:
			print("Cache current layer and load layer from file")

		for bookmark in bookmarks:
			if line.contains(bookmark):
				bookmarkFound = True
			else:
				newMarks.append(bookmark)

		if not bookmarkFound:
			newMarks.append(line)

		self.add_marks(newMarks)

	def swap_layers(self, direction):
		if direction == "prev":
			self.layers.rotate(-1)
		elif direction == "next":
			self.layers.rotate(1)

		if settings.get("auto_save_marks"):
#			layer_dict = dict([])
#			for layer in self.layers:
#				layer_dict[layer] = self.bookmarks
			print(self.bookmarks)
			self.cache.set("Bookmarks", {self.bookmarks})
			sublime.save_settings(self.bookmark_cache)

		self.layer = self.layers[0]
		sublime.status_message(self.layer)
		self.refresh_bookmarks()

	def run(self, edit, **args):
		if args.get('bookmark_line'):
			self.bookmark_line(self.layer, self.view.line(self.view.sel()[0]))
		elif args.get('swap_layers'):
			self.swap_layers(args.get('direction'))
		elif args.get('clear_marks'):
			self.add_marks([])

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)

	def on_load(self, view):
		if settings.get("load_marks_on_load"):
			print("Implement - On load")

	# def on_post_save(self, view):
	# 	if settings.get("save_marks_on_save"):
	# 		bookmarks = view.get_regions("bookmarks")
			# if not len(bookmarks):
			# 	filename = "BetterBookmarks/{:s}.sublime-settings".format(self.bookmark_cache)
			# 	marks = sublime.load_settings(filename)
			# 	print(self.bb.layers)
				# for layer in self.bb.layers:
				# 	print(layer)
				# marks.set()
