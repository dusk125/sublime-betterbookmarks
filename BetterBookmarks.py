import sublime, sublime_plugin, os
import collections
import json

# Add our BetterBookmarks cache folder if it doesn't exist
def plugin_loaded():
	Marks(True)

def Log(message):
	if Settings().get('verbose', False):
		print('[BetterBookmarks] ' + message)

def Settings():
    return sublime.load_settings('BetterBookmarks.sublime-settings')

def Variable(var, window=None):
	window = window if window else sublime.active_window()
	return sublime.expand_variables(var, window.extract_variables())

def Marks(create=False):
	directory = '{:s}/User/BetterBookmarks'.format(sublime.packages_path())
	if create and not os.path.exists(directory):
		os.makedirs(directory)

	return Variable(directory + '/${file_base_name}-${file_extension}.bb_cache')

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
		Settings().add_on_change('layer_icons', self.on_settings_change)

		self.view = view
		self.filename = Variable('${file_name}')
		self.on_settings_change()
		self.layer = Settings().get('default_layer')
		while not self.layers[0] == self.layer:
			self.layers.rotate(1)
		self.marks = dict([])
		for layer in Settings().get('layer_icons'):
			self.marks[layer] = []

	def on_settings_change(self):
		self.layers = collections.deque(Settings().get('layer_icons'))

	def should_bookmark(self, region):
		bookmarks = self.view.get_regions('bookmarks')
		line = self.view.line(region)

		for bookmark in bookmarks:
			if line.contains(bookmark):
				return False

		return True

	def is_empty(self):
		for layer in self.layers:
			if self.marks[layer]:
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
		Log('Loading BBFile for ' + self.filename)
		try:
			with open(Marks(), 'r') as fp:
				marks = json.load(fp, object_hook=RegionJSONCoder.dict_to_object)
				for layer, regions in marks.items():
					self.marks[layer] = regions
		except Exception as e:
			pass
		self.change_to_layer(Settings().get('default_layer'))
			
	def remove_save(self):
		if self.is_empty():
			Log('Removing BBFile for ' + self.filename)
			try:
				os.remove(Marks())
			except FileNotFoundError as e:
				pass

	def save_marks(self):
		if not self.is_empty():
			Log('Saving BBFile for ' + self.filename)
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
	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)

		self.bb = BBFile(self.view)
		self.bb.refresh_bookmarks()

	def run(self, edit, **args):
		view = self.view
		subcommand = args['subcommand']
		
		if subcommand == 'mark_line':
			self.bb.add_mark(view.line(view.sel()[0]))
		elif subcommand == 'clear_marks':
			self.bb.add_marks([])
		elif subcommand == 'clear_all':
			blayer = self.bb.layer
			for layer in self.bb.layers:
				self.bb.layer = layer
				self.bb.add_marks([])

			self.bb.layer = blayer
		elif subcommand == 'layer_swap':
			self.bb.swap_layer(args.get('direction'))
		elif subcommand == 'on_load':
			self.bb.load_marks()
		elif subcommand == 'on_save':
			self.bb.save_marks()
		elif subcommand == 'on_close':
			self.bb.remove_save()

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)

	def _contact(self, view, subcommand):
		view.run_command('better_bookmarks', {'subcommand': subcommand})

	def on_load(self, view):
		if Settings().get('load_marks_on_load'):
			self._contact(view, 'on_load')

	def on_pre_save(self, view):
		if Settings().get('auto_save_marks'):
			self._contact(view, 'on_save')

	def on_pre_close(self, view):
		if Settings().get('cleanup_empty_cache_on_close'):
			self._contact(view, 'on_close')
