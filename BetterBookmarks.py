import sublime, sublime_plugin

global settings
settings = sublime.load_settings("BetterBookmarks.sublime-settings")

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)
		self.bookmarks = []
		self.refresh_bookmarks(self.view)
		self.layer = "function"

	def run(self, edit, **args):
		if args.get('bookmark_line'):
			self.bookmark_line(self.view, self.layer, self.view.line(self.view.sel()[0]))
		elif args.get('bb_prev_group'):
			print("Implement - Prev Group")
		elif args.get('bb_next_group'):
			print("Implement - Next Group")

	def refresh_bookmarks(self, view):
		self.bookmarks = view.get_regions("bookmarks")

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

		icon = settings.get("layer_icons")[self.layer]["icon"]
		scope = settings.get("layer_icons")[self.layer]["scope"]

		view.add_regions("bookmarks", newMarks, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

		self.refresh_bookmarks(view)

	def should_bookmark(self, view, region):
		bookmarks = view.get_regions("bookmarks")
		line = view.line(region)

		for bookmark in bookmarks:
			if line.contains(bookmark):
				return False

		return True

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def on_load(self, view):
		if settings.get("load_marks_on_load"):
			print("Implement - On load")

	def on_post_save(self, view):
		if settings.get("save_marks_on_save"):
			print("Implement - On save")