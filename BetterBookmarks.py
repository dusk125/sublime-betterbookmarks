import sublime, sublime_plugin

global settings
settings = sublime.load_settings("BetterBookmarks.sublime-settings")

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	@staticmethod
	def should_bookmark(view, region):
		bookmarks = view.get_regions("bookmarks")
		line = view.line(region)

		for bookmark in bookmarks:
			if line.contains(bookmark):
				return False

		return True

	def run(self, edit):
		caretLine = self.view.line(self.view.sel()[0])
     	oldBookmarks = self.view.get_regions("bookmarks")

		newBookmarks = []
		bookmarkFoundOnCaretLine = False

		for thisbookmark in oldBookmarks:
			if caretLine.contains(thisbookmark):
		 		bookmarkFoundOnCaretLine = True
			else:
				newBookmarks.append(thisbookmark)

		if not bookmarkFoundOnCaretLine:
			newBookmarks.append(self.view.sel()[0])

		sublime.active_window().active_view().add_regions(
			"bookmarks", newBookmarks, "bookmarks", "bookmark", 
			sublime.HIDDEN | sublime.PERSISTENT)