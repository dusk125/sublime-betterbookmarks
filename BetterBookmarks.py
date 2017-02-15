import sublime, sublime_plugin, os
import collections
import json

# Add our BetterBookmarks cache folder if it doesn't exist
def plugin_loaded():
	directory = '{:s}/User/BetterBookmarks'.format(sublime.packages_path())
	if not os.path.exists(directory):
		os.makedirs(directory)

def Log(message):
	if Settings().get('verbose', False):
		print('[BetterBookmarks] ' + message)

def Settings():
    return sublime.load_settings('BetterBookmarks.sublime-settings')

def Variable(var, window=None):
	window = window if window else sublime.active_window()
	return sublime.expand_variables(var, window.extract_variables())

# Converts the marks-as-tuples back into sublime.Regions
def UnhashMarks(marks):
	newMarks = []
	for mark in marks:
		newMarks.append(sublime.Region(mark[0], mark[1]))

	return newMarks

# In order to use some list functions, python needs to be able to see a sublime.Region as something simpler;
# 	in this case a tuple.
def HashMarks(marks):
	newMarks = []
	for mark in marks:
		newMarks.append((mark.a, mark.b))

	return newMarks

# This class allows the conversion from a sublime.Region to a string (json)
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
		self.filename = Variable('${file_name}')
		self.layers = collections.deque(Settings().get('layer_icons'))
		self.layer = Settings().get('default_layer')
		while not self.layers[0] == self.layer:
			self.layers.rotate(1)
		self.marks = {}
		for layer in Settings().get('layer_icons'):
			self.marks[layer] = []

	def _is_empty(self):
		for layer in self.layers:
			if self.marks[layer]:
				return False

		return True

	# Get the path to the cache file.
	def _marks(self):
		return '{:s}/User/BetterBookmarks/{:s}.bb_cache'.format(sublime.packages_path(), self.filename.replace('.', '-'))

	# Renders the current layers marks to the view
	def _render(self):
		marks = UnhashMarks(self.marks[self.layer])
		icon = Settings().get('layer_icons')[self.layer]['icon']
		scope = Settings().get('layer_icons')[self.layer]['scope']

		self.view.add_regions('bookmarks', marks, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

	# Internal function for adding a list of marks to the existing ones.
	# 	Any marks that exist in both lists will be removed as this case is when the user is 
	# 		attempting to remove a mark.
	def _add_marks(self, newMarks, layer=None):
		layer = layer if layer else self.layer
		marks = []

		if newMarks:
			if not layer in self.marks:
				self.marks[layer] = []

			marks = self.marks[layer]

			for mark in newMarks:
				if mark in marks:
					marks.remove(mark)
				else:
					marks.append(mark)

		self.marks[layer] = marks

		if layer == self.layer:
			self._render()

	# Changes the layer to the given one and updates any and all of the status indicators.
	def _change_to_layer(self, layer):
		self.layer = layer
		status_name = 'bb_layer_status'

		status = Settings().get('layer_status_location', ['permanent'])

		if 'temporary' in status:
			sublime.status_message(self.layer)
		if 'permanent' in status:
			self.view.set_status(status_name, 'Bookmark Layer: {:s}'.format(self.layer))
		else:
			self.view.erase_status(status_name)
		if 'popup' in status:
			if self.view.is_popup_visible():
				self.view.update_popup(self.layer)
			else:
				self.view.show_popup(self.layer, 0, -1, 1000, 1000, None, None)

		self._render()

	def _save_marks(self):
		if not self._is_empty():
			Log('Saving BBFile for ' + self.filename)
			with open(self._marks(), 'w') as fp:
				json.dump(self.marks, fp, cls=RegionJSONCoder)

	def run(self, edit, **args):
		view = self.view
		subcommand = args['subcommand']

		if subcommand == 'mark_line':
			selection = view.sel()
			if Settings().get('mark_whole_line', False):
				selection = view.lines(selection[0])
			line = args['line'] if 'line' in args else HashMarks(selection)
			layer = args['layer'] if 'layer' in args else self.layer

			self._add_marks(line, layer)
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
				with open(self._marks(), 'r') as fp:
					marks = json.load(fp, object_hook=RegionJSONCoder.dict_to_object)
					for layer, regions in marks.items():
						self.marks[layer] = regions
			except Exception as e:
				pass
			self._change_to_layer(Settings().get('default_layer'))
		elif subcommand == 'on_save':
			self._save_marks()
		elif subcommand == 'on_close':
			if Settings().get('cache_marks_on_close', False):
				self._save_marks()
			if self._is_empty():
				Log('Removing BBFile for ' + self.filename)
				try:
					os.remove(self._marks())
				except FileNotFoundError as e:
					pass

class BetterBookmarksEventListener(sublime_plugin.EventListener):
	def __init__(self):
		sublime_plugin.EventListener.__init__(self)

	def _contact(self, view, subcommand):
		view.run_command('better_bookmarks', {'subcommand': subcommand})

	def on_load_async(self, view):
		if Settings().get('uncache_marks_on_load'):
			self._contact(view, 'on_load')

	def on_pre_save(self, view):
		if Settings().get('cache_marks_on_save'):
			self._contact(view, 'on_save')

	def on_close(self, view):
		if view.file_name() and Settings().get('cleanup_empty_cache_on_close'):
			self._contact(view, 'on_close')
