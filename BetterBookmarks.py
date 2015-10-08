import sublime, sublime_plugin

global settings
settings = sublime.load_settings("BetterBookmarks.sublime-settings")

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		if args.get('bookmark_line'):
			self.bookmark_line(self.view, self.view.line(self.view.sel()[0]))

	@staticmethod
	def bookmark_line(view, line):
		oldMarks = view.get_regions("bookmarks")

		newMarks = []
		bookmarkFound = False

		for bookmark in oldMarks:
			if line.contains(bookmark):
				bookmarkFound = True
			else:
				newMarks.append(bookmark)

		if  not bookmarkFound:
			newMarks.append(line)

		view.add_regions("bookmarks", newMarks, "bookmarks", 
			"bookmark", sublime.HIDDEN | sublime.PERSISTENT)

	@staticmethod
	def should_bookmark(view, region):
		bookmarks = view.get_regions("bookmarks")
		line = view.line(region)

		for bookmark in bookmarks:
			if line.contains(bookmark):
				return False

		return True

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def on_load(view):
		print("Implement")

	def on_pre_save_async(view):
		print("Implement")