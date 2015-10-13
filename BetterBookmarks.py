import sublime, sublime_plugin
import collections

global settings
settings = sublime.load_settings("BetterBookmarks.sublime-settings")

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)

		self.bookmarks = []
		self.layers = collections.deque(settings.get("layer_icons"))
		self.layer = settings.get("default_layer")
		self.refresh_bookmarks()

	def add_marks(self, list):
		icon = settings.get("layer_icons")[self.layer]["icon"]
		scope = settings.get("layer_icons")[self.layer]["scope"]

		self.view.add_regions(self.layer, list, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

		self.refresh_bookmarks()

	def refresh_bookmarks(self):
		self.bookmarks = self.view.get_regions(self.layer)

	def bookmark_line(self, view, layer, line):
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

	def should_bookmark(self, view, region):
		bookmarks = view.get_regions("bookmarks")
		line = view.line(region)

		for bookmark in bookmarks:
			if line.contains(bookmark):
				return False

		return True

	def run(self, edit, **args):
		if args.get('bookmark_line'):
			self.bookmark_line(self.view, self.layer, self.view.line(self.view.sel()[0]))
		if args.get('swap_layers'):
			direction = args.get('direction')

			if direction == "prev":
				self.layers.rotate(-1)
			elif direction == "next":
				self.layers.rotate(1)

			self.layer = self.layers[0]
			self.refresh_bookmarks()
		if args.get('clear_marks'):
			self.add_marks([])

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def on_load(self, view):
		if settings.get("load_marks_on_load"):
			print("Implement - On load")

	def on_post_save(self, view):
		if settings.get("save_marks_on_save"):
			print("Implement - On save")