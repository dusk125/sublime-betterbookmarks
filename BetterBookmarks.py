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

# class BBRegion():
# 	def __init__(self, a, b):
# 		self.a = a
# 		self.b = b

# 	def __hash__(self):
# 		print("hello")
# 		return hash((self.a, self.b))

# 	def __eq__(self, other):
# 		return isinstance(other, BBRegion) and self.a == other.a and self.b == other.b

# 	@staticmethod
# 	def cast_to_this(region):
# 		return BBRegion(region.a, region.b)

# class BetterBookmarksCommand(sublime_plugin.TextCommand):
# 	def __init__(self, edit):
# 		sublime_plugin.TextCommand.__init__(self, edit)

# 		directory = "{:s}/User/BetterBookmarks".format(sublime.packages_path())
# 		if not os.path.exists(directory):
# 			os.makedirs(directory)
		
# 		bookmark_cache_name = sublime.expand_variables("${file_base_name}.sublime-settings", sublime.active_window().extract_variables())
# 		self.bookmark_cache = "BetterBookmarks/{:s}".format(bookmark_cache_name)

# 	def add_marks(self, list):
# 		icon = settings.get("layer_icons")[self.layer]["icon"]
# 		scope = settings.get("layer_icons")[self.layer]["scope"]

# 		self.view.add_regions("bookmarks", list, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

# 		self.refresh_bookmarks()

# 	def refresh_bookmarks(self):
# 		self.bookmarks[self.layer] = self.view.get_regions("bookmarks")

# 	def bookmark_line(self, layer, line):
# 		newMarks = []
# 		bookmarkFound = False

# 		if not layer == self.layer:
# 			print("Cache current layer and load layer from file")

# 		bookmarks = self.bookmarks[layer]

# 		for bookmark in bookmarks:
# 			if line.contains(bookmark):
# 				bookmarkFound = True
# 			else:
# 				# bm = BBRegion.cast_to_this(bookmark)
# 				newMarks.append(bookmark)

# 		if not bookmarkFound:
# 			# ln = BBRegion.cast_to_this(line)
# 			newMarks.append(line)

# 		self.add_marks(newMarks)

# 	def swap_layers(self, direction):
# 		if direction == "prev":
# 			self.layers.rotate(-1)
# 		elif direction == "next":
# 			self.layers.rotate(1)

# 		if settings.get("auto_save_marks"):
# 			# print(self.bookmarks)
# 			def freeze(d):
# 			    if isinstance(d, dict):
# 			        return frozenset((key, freeze(value)) for key, value in d.items())
# 			    elif isinstance(d, list):
# 			        return tuple(freeze(value) for value in d)
# 			    return d
# 			# self.cache.set(key="Marks", value=freeze(self.bookmarks))
# 			self.cache.set("Marks", self.bookmarks[self.layer])
# 			sublime.save_settings(self.bookmark_cache)

# 		self.layer = self.layers[0]
# 		sublime.status_message(self.layer)
# 		self.refresh_bookmarks()

# 	def run(self, edit, **args):
# 		if args.get('bookmark_line'):
# 			self.bookmark_line(self.layer, self.view.line(self.view.sel()[0]))
# 		elif args.get('swap_layers'):
# 			self.swap_layers(args.get('direction'))
# 		elif args.get('clear_marks'):
# 			self.add_marks([])

global bbFiles
bbFiles = dict([])

def get_variable(var_string):
	return sublime.expand_variables(var_string, sublime.active_window().extract_variables())

def get_current_file_name():
	return get_variable("${file}")

def get_marks_filename():
	directory = "{:s}\\User\\BetterBookmarks".format(sublime.packages_path())
	if not os.path.exists(directory):
		os.makedirs(directory)

	return "{:s}\\{:s}.bb_cache".format(directory, get_variable("${file_base_name}"))

# class BBRegion(sublime.Region):
# 	def __init__(self, a, b):
# 		sublime.Region.__init__(self, a, b)

# 	@staticmethod
# 	def cast_to_this(region):
# 		return BBRegion(region.a, region.b)

class RegionEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, sublime.Region):
			return {
				'__type__': "sublime.Region",
				'a': obj.a,
				'b': obj.b,
			}
		return json.JSONEncoder.default(self, obj)

def dict_to_object(self, d):
	if '__type__' not in d:
		return d

	type = d.pop('__type__')
	if type == 'sublime.Region':
		return sublime.Region(**d)
	else:
		d['__type__'] = type
		return d

class BBFile():
	def __init__(self, view):
		self.view = view
		self.filename = get_current_file_name()
		self.layers = settings.get("layer_icons")
		self.layer = settings.get("default_layer")
		self.marks = dict([])
		self.load_marks()

	def refresh_bookmarks(self):
		self.marks[self.layer] = self.view.get_regions("bookmarks")

	def add_marks(self, list):
		icon = settings.get("layer_icons")[self.layer]["icon"]
		scope = settings.get("layer_icons")[self.layer]["scope"]

		self.view.add_regions("bookmarks", list, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

		self.refresh_bookmarks()

	def load_marks(self):
		try:
			with open(get_marks_filename(), 'r') as fp:
				self.marks = json.load(fp, object_hook=dict_to_object)
				print(self.marks)
				self.refresh_bookmarks()
		except Exception as e:
			print("Couldn't read file")
			pass

	def save_marks(self):
		with open(get_marks_filename(), 'w') as fp:
			json.dump(self.marks, fp, cls=RegionEncoder)

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
				# m = BBRegion.cast_to_this(mark)
				# newMarks.append(m)

		if not markFound:
			# ln = BBRegion.cast_to_this(line)
			# newMarks.append(ln)
			newMarks.append(line)

		self.add_marks(newMarks)

class BetterBookmarksMarkLineCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		bb = bbFiles[get_current_file_name()]
		bb.add_mark(self.view.line(self.view.sel()[0]))

class BetterBookmarksClearMarksCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		bb = bbFiles[get_current_file_name()]
		# bb.add_marks([])
		bb.save_marks()

class BetterBookmarksSwapLayerCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		bb = bbFiles[get_current_file_name()]
		bb.load_marks()
		# print("Implement")

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)

	def on_load(self, view):
		if settings.get("load_marks_on_load"):
			filename = get_current_file_name()
			if not filename in bbFiles:
				print("[BetterBookmarksEventListener] Creating BBFile for " + filename)
				bbFiles[filename] = BBFile(view)
			# self.cache = sublime.load_settings(self.bookmark_cache)

			# self.layers = collections.deque(settings.get("layer_icons"))
			# self.layer = settings.get("default_layer")
			# self.bookmarks = self.cache.get("Bookmarks")
			# if self.bookmarks == None:
			# 	self.bookmarks = dict([])
			# self.refresh_bookmarks()
