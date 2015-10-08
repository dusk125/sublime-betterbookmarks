import sublime, sublime_plugin

global settings
settings = sublime.load_settings("BetterBookmarks.sublime-settings")

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)
		self.bookmarks = []
		self.refresh_bookmarks(self.view)

	def run(self, edit, **args):
		if args.get('bookmark_line'):
			self.bookmark_line(self.view, self.view.line(self.view.sel()[0]))

	def refresh_bookmarks(self, view):
		self.bookmarks = view.get_regions("bookmarks")

	def bookmark_line(self, view, line):
		newMarks = []
		
		if not self.bookmarks:
			newMarks.append(line)

		for bookmark in self.bookmarks:
			if not line.contains(bookmark):
				newMarks.append(bookmark)

		view.add_regions("bookmarks", newMarks, "bookmarks", 
			"bookmark", sublime.HIDDEN | sublime.PERSISTENT)

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
		print("Implement")

	def on_post_save(self, view):
		print("Implement")