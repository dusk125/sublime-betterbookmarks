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

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)
		Settings().add_on_change('layer_icons', self._on_settings_change)

		self.filename = Variable('${file_name}')
		self._on_settings_change()
		self.layer = Settings().get('default_layer')
		while not self.layers[0] == self.layer:
			self.layers.rotate(1)
		self.marks = {}
		for layer in Settings().get('layer_icons'):
			self.marks[layer] = []

	def _on_settings_change(self):
		self.layers = collections.deque(Settings().get('layer_icons'))

	def _should_bookmark(self, layer, line):
		for bookmark in self.marks[layer]:
			if line.contains(bookmark):
				return False

		return True

	def _is_empty(self):
		for layer in self.layers:
			if self.marks[layer]:
				return False

		return True

	def _render(self):
		marks = self._unhash_marks(self.marks[self.layer])
		icon = Settings().get('layer_icons')[self.layer]['icon']
		scope = Settings().get('layer_icons')[self.layer]['scope']

		self.view.add_regions('bookmarks', marks, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

	def _unhash_marks(self, marks):
		newMarks = []
		for mark in marks:
			newMarks.append(sublime.Region(mark[0], mark[1]))

		return newMarks

	def _hash_marks(self, marks):
		newMarks = []
		for mark in marks:
			newMarks.append((mark.a, mark.b))

		return newMarks

	def _add_marks(self, newMarks, layer=None):
		layer = layer if layer else self.layer
		marks = []

		if newMarks:
			newMarks = self._hash_marks(newMarks)

			if not layer in self.marks:
				self.marks[layer] = []

			marks = self.marks[layer]

			for mark in newMarks:
				if mark in marks:
					marks.remove(mark)
				else:
					marks.append(mark)

		self.marks[layer] = marks

		if layer is self.layer:
			self._render()

	def _change_to_layer(self, layer):
		self.layer = layer
		sublime.status_message(self.layer)
		self._render()

	def run(self, edit, **args):
		view = self.view
		subcommand = args['subcommand']
		
		if subcommand == 'mark_line':
			line = args['line'] if 'line' in args else view.sel()[0]
			layer = args['layer'] if 'layer' in args else self.layer

			self._add_marks([line], layer)
		elif subcommand == 'clear_marks':
			layer = args['layer'] if 'layer' in args else self.layer
			self._add_marks([], layer)
		elif subcommand == 'clear_all':
			for layer in self.layers:
				self._add_marks([], layer)
		elif subcommand == 'layer_swap':
			direction = args.get('direction')
			if direction == 'prev':
				self.layers.rotate(-1)
			elif direction == 'next':
				self.layers.rotate(1)
			else:
				sublime.error_message('Invalid layer swap direction.')

			self._change_to_layer(self.layers[0])
		elif subcommand == 'on_load':
			Log('Loading BBFile for ' + self.filename)
			try:
				with open(Marks(), 'r') as fp:
					marks = json.load(fp, object_hook=RegionJSONCoder.dict_to_object)
					for layer, regions in marks.items():
						self.marks[layer] = regions
			except Exception as e:
				pass
			self._change_to_layer(Settings().get('default_layer'))
		elif subcommand == 'on_save':
			if not self._is_empty():
				Log('Saving BBFile for ' + self.filename)
				with open(Marks(), 'w') as fp:
					json.dump(self.marks, fp, cls=RegionJSONCoder)
		elif subcommand == 'on_close':
			if self._is_empty():
				Log('Removing BBFile for ' + self.filename)
				try:
					os.remove(Marks())
				except FileNotFoundError as e:
					pass

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)

	def _contact(self, view, subcommand):
		view.run_command('better_bookmarks', {'subcommand': subcommand})

	def on_load_async(self, view):
		if Settings().get('load_marks_on_load'):
			self._contact(view, 'on_load')

	def on_pre_save_async(self, view):
		if Settings().get('auto_save_marks'):
			self._contact(view, 'on_save')

	def on_pre_close(self, view):
		if Settings().get('cleanup_empty_cache_on_close'):
			self._contact(view, 'on_close')
