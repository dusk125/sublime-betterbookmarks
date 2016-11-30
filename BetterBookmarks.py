import sublime, sublime_plugin, os
import collections
import json

global bbFiles
bbFiles = dict([])

def Settings():
    return sublime.load_settings('BetterBookmarks.sublime-settings')

def Variable(var, window=None):
	window = window if window else sublime.active_window()
	return sublime.expand_variables(var, window.extract_variables())

def Filename(window=None):
	return Variable('${file}', window)

def Marks():
	directory = '{:s}/User/BetterBookmarks'.format(sublime.packages_path())
	if not os.path.exists(directory):
		os.makedirs(directory)

	return Variable(directory + '/${file_base_name}-${file_extension}.bb_cache')

def GetBB(view=None):
	bb = None
	filename = Filename()

	if filename in bbFiles:
		bb = bbFiles[filename]
	else:
		bb = BBFile(view if view else sublime.active_window().active_view())
		bbFiles[filename] = bb
		bb.refresh_bookmarks()

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
		self.filename = Filename()
		self.layers = collections.deque(Settings().get('layer_icons'))
		self.layer = Settings().get('default_layer')
		while not self.layers[0] == self.layer:
			self.layers.rotate(1)
		self.marks = dict([])
		for layer in Settings().get('layer_icons'):
			self.marks[layer] = []

	def should_bookmark(self, region):
		bookmarks = self.view.get_regions('bookmarks')
		line = self.view.line(region)

		for bookmark in bookmarks:
			if line.contains(bookmark):
				return False

		return True

	def refresh_bookmarks(self):
		self.marks[self.layer] = self.view.get_regions('bookmarks')

	def add_marks(self, list, layer=None):
		usedLayer = layer if layer else self.layer
		icon = Settings().get('layer_icons')[usedLayer]['icon']
		scope = Settings().get('layer_icons')[usedLayer]['scope']

		self.view.add_regions('bookmarks', list, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

		self.refresh_bookmarks()

	def load_marks(self):
		try:
			with open(Marks(), 'r') as fp:
				self.marks = json.load(fp, object_hook=RegionJSONCoder.dict_to_object)
				for tup in self.marks.items():
					self.layer = tup[0]
					self.add_marks(tup[1])
				self.layer = Settings().get('default_layer')
		except Exception as e:
			pass

	def save_marks(self):
		with open(Marks(), 'w') as fp:
			json.dump(self.marks, fp, cls=RegionJSONCoder)

	def add_mark(self, line, layer=None):
		newMarks = []
		markFound = False

		if not layer:
			layer = self.layer
		elif not layer == self.layer:
			print('Cache current layer and load layer from file')

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

		self.add_marks(newMarks, layer)

	def change_to_layer(self, layer):
		self.layer = layer
		sublime.status_message(self.layer)

		if self.layer in self.marks:
			self.add_marks(self.marks[self.layer])
		else:
			self.marks[self.layer] = []

	def swap_layer(self, direction):
		if direction == 'prev':
			self.layers.rotate(-1)
		elif direction == 'next':
			self.layers.rotate(1)
		else:
			sublime.error_message('Invalid layer swap direction.')

		self.change_to_layer(self.layers[0])

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		view = self.view
		subcommand = args['subcommand']
		bb = GetBB()
		
		if subcommand == 'mark_line':
			bb.add_mark(view.line(view.sel()[0]))
		elif subcommand == 'clear_marks':
			bb.add_marks([])
		elif subcommand == 'clear_all':
			blayer = bb.layer
			for layer in bb.layers:
				bb.layer = layer
				bb.add_marks([])

			bb.layer = blayer
		elif subcommand == 'layer_swap':
			bb.swap_layer(args.get('direction'))

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)
		Settings().add_on_change('layer_icons', self.on_layer_icon_change)

	def on_layer_icon_change(self):
		for bb in bbFiles.items():
			bb[1].layers.clear()
			bb[1].layers.extend(Settings().get('layer_icons'))

	def on_load(self, view):
		if Settings().get('load_marks_on_load'):
			filename = Filename()
			if not filename in bbFiles:
				print('[BetterBookmarksEventListener] Creating BBFile for ' + filename)
				bb = BBFile(view)
				bb.load_marks()
				bbFiles[filename] = bb

	def on_pre_save(self, view):
		if Settings().get('auto_save_marks'):
			bb = GetBB()

			if bb.marks.keys():
				print(bb.marks.keys())
				bb.save_marks()

	def on_pre_close(self, view):
		if Settings().get('cleanup_empty_cache_on_close'):
			filename = Filename()
			bb = GetBB()
			empty = True
			for item in bb.marks.items():
				empty = empty and not item[1]
			if bb.marks.items() and empty:
				try:
					os.remove(Marks())
				except FileNotFoundError as e:
					pass
			if filename in bbFiles:
				del bbFiles[filename]
