import sublime, sublime_plugin, os, collections, json, hashlib

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

# Takes a region and converts it to a list taking into consideration if
#	the user wants us to care about the order of the selection.
def FixRegion(mark):
	if Settings().get("ignore_cursor", True):
		return [mark.begin(), mark.end()]
	return [mark.a, mark.b]

def fix(item):
	if item[0] > item[1]:
		item[0], item[1] = item[1], item[0]
	return item

def mark_in(one, two):
	one = one[0]
	two = fix(two)

	return one >= two[0] and one <= two[1]

class BetterBookmarksCommand(sublime_plugin.TextCommand):
	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)
		self.filename = Variable('${file_name}')
		self.layers = collections.deque(Settings().get('layer_icons'))
		self.layer = Settings().get('default_layer')
		while not self.layers[0] == self.layer:
			self.layers.rotate(1)

	def _is_empty(self):
		for layer in self.layers:
			if self.view.get_regions(self._get_region_name(layer)):
				return False

		return True

	# Get the path to the cache file.
	def _get_cache_filename(self):
		h = hashlib.md5()
		h.update(self.view.file_name().encode())
		filename = str(h.hexdigest())
		return '{:s}/User/BetterBookmarks/{:s}.bb_cache'.format(sublime.packages_path(), filename)

	def _get_region_name(self, layer=None):
		return 'better_bookmarks_{}'.format(layer if layer else self.layer)

	# Renders the current layers marks to the view
	def _render(self):
		marks = self.view.get_regions(self._get_region_name())
		icon = Settings().get('layer_icons')[self.layer]['icon']
		scope = Settings().get('layer_icons')[self.layer]['scope']

		self.view.add_regions('better_bookmarks', marks, scope, icon, sublime.PERSISTENT | sublime.HIDDEN)

	# Internal function for adding a list of marks to the existing ones.
	# 	Any marks that exist in both lists will be removed as this case is when the user is 
	# 		attempting to remove a mark.
	def _add_marks(self, newMarks, layer=None):
		region = self._get_region_name(layer)
		marks = self.view.get_regions(region)
		
		for mark in newMarks:
			if mark in marks:
				marks.remove(mark)
			else:
				marks.append(mark)

		self.view.add_regions(region, marks, '', '', 0)

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

	def run(self, edit, **args):
		view = self.view
		subcommand = args['subcommand']

		if subcommand == 'mark_line':
			mode = Settings().get('marking_mode', 'selection')

			if mode == 'line':
				selection = view.lines(view.sel()[0])
			elif mode == 'selection':
				selection = view.sel()
			else:
				sublime.error_message('Invalid BetterBookmarks setting: \'{}\' is invalid for \'marking_mode\''.format(mode))

			line = args['line'] if 'line' in args else selection
			layer = args['layer'] if 'layer' in args else self.layer

			self._add_marks(line, layer)
		elif subcommand == 'clear_marks':
			layer = args['layer'] if 'layer' in args else self.layer
			self.view.erase_regions('better_bookmarks')
			self.view.erase_regions(self._get_region_name(layer))
		elif subcommand == 'clear_all':
			self.view.erase_regions('better_bookmarks')
			for layer in self.layers:
				self.view.erase_regions(self._get_region_name(layer))
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
				with open(self._get_cache_filename(), 'r') as fp:
					data = json.load(fp)

					for name, marks in data['bookmarks'].items():
						self._add_marks([sublime.Region(mark[0], mark[1]) for mark in marks], name)
			except Exception as e:
				pass
			self._change_to_layer(Settings().get('default_layer'))
		elif subcommand == 'on_save':
			if not self._is_empty():
				Log('Saving BBFile for ' + self.filename)
				with open(self._get_cache_filename(), 'w') as fp:
					marks = {'filename': self.view.file_name(), 'bookmarks': {}}
					for layer in self.layers:
						marks['bookmarks'][layer] = [FixRegion(mark) for mark in self.view.get_regions(self._get_region_name())]
					json.dump(marks, fp)
		elif subcommand == 'on_close':
			if Settings().get('cache_marks_on_close', False):
				self._save_marks()
			if Settings().get('cleanup_empty_cache_on_close', False) and self._is_empty():
				Log('Removing BBFile for ' + self.filename)
				try:
					os.remove(self._get_cache_filename())
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
		if view.file_name():
			self._contact(view, 'on_close')
