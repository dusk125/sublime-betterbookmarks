import sublime, sublime_plugin, os
import collections
import json

global settings
settings = sublime.load_settings("BetterBookmarks.sublime-settings")

global bbFiles
bbFiles = dict([])

class BBFunctions():
	@staticmethod
	def get_variable(var_string):
		return sublime.expand_variables("{:s}".format(var_string), sublime.active_window().extract_variables())

	@staticmethod
	def get_current_file_name():
		return BBFunctions.get_variable("${file}")

	@staticmethod
	def get_marks_filename():
		directory = "{:s}\\User\\BetterBookmarks".format(sublime.packages_path())
		if not os.path.exists(directory):
			os.makedirs(directory)

		return "{:s}\\{:s}-{:s}.bb_cache".format(directory, BBFunctions.get_variable("${file_base_name}"), BBFunctions.get_variable("${file_extension}"))

	@staticmethod
	def get_bb_file():
		bb = None
		filename = BBFunctions.get_current_file_name()

		if filename in bbFiles:
			bb = bbFiles[filename]
		else:
			bb = BBFile(sublime.active_window().active_view())
			bbFiles[filename] = bb

		return bb

class RegionJSONCoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, sublime.Region):
			return {
				'__type__': 'sublime.Region',
				'a': obj.a,
				'b': obj.b,
			}
		return json.JSONEncoder.default(self, obj)

	@staticmethod
	def dict_to_object(d):
		if '__type__' not in d:
			return d

		type = d.pop('__type__')
		if type == 'sublime.Region':
			return sublime.Region(d.pop('a'), d.pop('b'))
		else:
			d['__type__'] = type
			return d

class BBFile():
	def __init__(self, view):
		self.view = view
		self.filename = BBFunctions.get_current_file_name()
		self.layers = collections.deque(settings.get("layer_icons"))
		self.layer = settings.get("default_layer")
		while not self.layers[0] == self.layer:
			self.layers.rotate(1)
		self.marks = dict([])
		for layer in settings.get("layer_icons"):
			self.marks[layer] = []

	def should_bookmark(self, region):
		bookmarks = self.view.get_regions("bookmarks")
		line = self.view.line(region)

		for bookmark in bookmarks:
			if line.contains(bookmark):
				return False

		return True

	def refresh_bookmarks(self):
		self.marks[self.layer] = self.view.get_regions("bookmarks")

	def add_marks(self, list):
		icon = settings.get("layer_icons")[self.layer]["icon"]
		scope = settings.get("layer_icons")[self.layer]["scope"]

		self.view.add_regions("bookmarks", list, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

		self.refresh_bookmarks()

	def load_marks(self):
		try:
			with open(BBFunctions.get_marks_filename(), 'r') as fp:
				self.marks = json.load(fp, object_hook=RegionJSONCoder.dict_to_object)
				for tup in self.marks.items():
					self.layer = tup[0]
					self.add_marks(tup[1])
				self.layer = settings.get("default_layer")
		except Exception as e:
			pass

	def save_marks(self):
		with open(BBFunctions.get_marks_filename(), 'w') as fp:
			json.dump(self.marks, fp, cls=RegionJSONCoder)

	def add_mark(self, line, layer=None):
		newMarks = []
		markFound = False

		if not layer:
			layer = self.layer
		elif not layer == self.layer:
			print("Cache current layer and load layer from file")

		if not layer in self.marks:
			self.marks[layer] = []

		marks = self.marks[layer]

		for mark in marks:
			if line.contains(mark):
				markFound = True
			else:
				newMarks.append(mark)

		if not markFound:
			newMarks.append(line)

		self.add_marks(newMarks)

	def change_to_layer(self, layer):
		self.layer = layer
		sublime.status_message(self.layer)

		if self.layer in self.marks:
			self.add_marks(self.marks[self.layer])
		else:
			self.marks[self.layer] = []

	def swap_layer(self, direction):
		if direction == "prev":
			self.layers.rotate(-1)
		elif direction == "next":
			self.layers.rotate(1)
		else:
			sublime.error_message("Invalid layer swap direction.")

		self.change_to_layer(self.layers[0])

class BetterBookmarksMarkLineCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		bb = BBFunctions.get_bb_file()
		bb.add_mark(self.view.line(self.view.sel()[0]))

class BetterBookmarksClearMarksCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		bb = BBFunctions.get_bb_file()
		bb.add_marks([])

class BetterBookmarksClearAllMarksCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		bb = BBFunctions.get_bb_file()
		blayer = bb.layer
		for layer in bb.layers:
			bb.layer = layer
			bb.add_marks([])

		bb.layer = blayer

class BetterBookmarksSwapLayerCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		bb = BBFunctions.get_bb_file()
		bb.swap_layer(args.get("direction"))

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)

	def on_load(self, view):
		if settings.get("load_marks_on_load"):
			filename = BBFunctions.get_current_file_name()
			if not filename in bbFiles:
				print("[BetterBookmarksEventListener] Creating BBFile for " + filename)
				bb = BBFile(view)
				bb.load_marks()
				bbFiles[filename] = bb

	def on_pre_save(self, view):
		if settings.get("auto_save_marks"):
			filename = BBFunctions.get_current_file_name()

			bb = BBFunctions.get_bb_file()

			if bb.marks.keys():
				bb.save_marks()

	def on_pre_close(self, view):
		if settings.get("cleanup_empty_cache_on_close"):
			filename = BBFunctions.get_current_file_name()
			bb = BBFunctions.get_bb_file()
			empty = True
			for item in bb.marks.items():
				empty = empty and not item[1]
			if bb.marks.items() and empty:
				try:
					os.remove(BBFunctions.get_marks_filename())
				except FileNotFoundError as e:
					pass
			if filename in bbFiles:
				del bbFiles[filename]
