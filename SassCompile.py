import sublime
import sublime_plugin
import json
import os
from threading import Thread
from subprocess import PIPE, Popen

dirtyFiles = []
pluginSettings = None
pluginProjectSettings = None
defaultPluginProjectSettings = None
pluginPath = None
userPath = None
upgradeCheckCompleted = False

def getPluginPath(appendPath = None):
	global pluginPath
	if not pluginPath:
		pluginPath = os.path.dirname(__file__);
	
	if appendPath:
		return os.sep.join([pluginPath, appendPath])
	return pluginPath

def getUserPath(appendPath = None):
	global userPath
	if not userPath:
		userPath = os.sep.join([os.path.dirname(getPluginPath()), 'User'])

	if appendPath:
		return os.sep.join([userPath, appendPath])

	return userPath

def logError(errorMessage):
	# outputPanel = sublime.active_window().create_output_panel('sasscompile')
	# outputPanelEdit = outputPanel.begin_edit()
	# outputPanel.insert(outputPanelEdit, outputPanel.size(), 'SassCompile Encountered an Error:\n')
	print('Sass Compile Encountered an Error:')
	# outputPanel.insert(outputPanelEdit, outputPanel.size(), err + '\n')
	# outputPanel.end_edit(outputPanelEdit)
	print(errorMessage)
	# outputPanel.
	# sublime.active_window().run_command('show_panel', {'panel': 'output.sasscompile'})

def wasDirty(filePath):
	return filePath in dirtyFiles

def getPluginSettings():
	global pluginSettings
	if not pluginSettings:
		pluginSettings = sublime.load_settings('SassCompile.sublime-settings')

	return pluginSettings

def getPluginProjectSettings():
	global pluginProjectSettings
	if not pluginProjectSettings:
		with open(getPluginPath('SassCompile.settings')) as pluginProjectSettingsFile:
			pluginProjectSettings = json.load(pluginProjectSettingsFile)
	return pluginProjectSettings.copy()

def getDefaultPluginProjectSettings():
	global defaultPluginProjectSettings
	if not defaultPluginProjectSettings:
		defaultPluginProjectSettings = {}
		for setting in getPluginProjectSettings():
			defaultPluginProjectSettings[setting['name']] = setting['default']

	return defaultPluginProjectSettings.copy()

def getDefaultProjectSettings():
	defaultProjectSettings = getDefaultPluginProjectSettings()
	
	userDefaultSettingsPath = getUserPath('SassCompile.default-config')
	userDefaultSettings = None
	if os.path.isfile(userDefaultSettingsPath):
		with open(userDefaultSettingsPath) as userDefaultSettingsFile:
			userDefaultSettings = json.load(userDefaultSettingsFile)

		for settingName, defaultValue in userDefaultSettings.items():
			if settingName in defaultProjectSettings:
				defaultProjectSettings[settingName] = defaultValue
	
	if not userDefaultSettings or set(userDefaultSettings) ^ set(defaultProjectSettings):
		with open(userDefaultSettingsPath, 'w') as userDefaultSettingsFile:
			json.dump(defaultProjectSettings, userDefaultSettingsFile, indent=4)

	return defaultProjectSettings

def initializeDefaultProjectSettings(promptForSettings = False):
	initialSettings = getDefaultProjectSettings()

	if promptForSettings:
		for setting in getPluginProjectSettings():
			if (promptForSettings == 1 and not setting['advanced']) or promptForSettings == 2:
				if setting['type'] == 'boolean' or type(setting['type']) is list:
					print(setting['title'])
				else:
					print(setting['title'])
		
	setProjectSetting(initialSettings)

def deinitializeProjectSettings():
	projectData = sublime.active_window().project_data()
	projectData['settings'].pop('sasscompile')
	if len(projectData['settings']) == 0:
		projectData.pop('settings')

	sublime.active_window().set_project_data(projectData)

def getProjectSetting(name = None):
	projectData = sublime.active_window().project_data()
	
	upgradeProjectSettings(projectData['settings']['sasscompile'])

	if name != None:
		return projectData['settings']['sasscompile'][name]

	return projectData['settings']['sasscompile'].copy()

def setProjectSetting(name, value = None):
	projectData = sublime.active_window().project_data()

	if 'settings' not in projectData:
		projectData['settings'] = {}
	if 'sasscompile' not in projectData['settings']:
		projectData['settings']['sasscompile'] = {}

	if value != None:
		projectData['settings']['sasscompile'][name] = value
	else:
		projectData['settings']['sasscompile'] = name

	sublime.active_window().set_project_data(projectData)

def upgradeProjectSettings(projectSettings):
	global upgradeCheckCompleted
	if not upgradeCheckCompleted:
		defaultProjectSettings = getDefaultProjectSettings()
		if set(projectSettings) ^ set(defaultProjectSettings):
			for setting in defaultProjectSettings:
				if setting in projectSettings:
					defaultProjectSettings[setting] = projectSettings[setting]
			setProjectSetting(defaultProjectSettings)
	upgradeCheckCompleted = True

def projectSettingsInitialized():
	if sublime.active_window().project_file_name():
		projectData = sublime.active_window().project_data()
		if 'settings' in projectData.keys():
			if 'sasscompile' in projectData['settings'].keys():
				return True

	return False

def isSassFile(filePath):
	if os.path.splitext(filePath)[1][1:] == getProjectSetting('syntax'):
		return True
	return False

def getFilesToCompile(filePath):
	if os.path.basename(filePath).startswith('_'):
		return getImportParents(filePath)
	return [filePath]

def getImportParents(filePath):
	importName = os.path.basename(filePath).split('.')[0][1:]
	cmd = "grep -E '@import.*{0}' * -l".format(importName)
	proc = Popen(cmd, shell=True, cwd=os.path.dirname(filePath), stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()
	if err:
		logError(err)
		return

	if not out:
		return

	files = []
	out = out.decode('utf8')
	for parentFileName in out.split():
		if isSassFile(parentFileName):
			files.extend(getFilesToCompile(os.sep.join([os.path.dirname(filePath), parentFileName])))
	
	return files

def compileOnThread(filesToCompile, originalFile):
	compileThread = Thread(target=compile, args=(filesToCompile, originalFile))
	compileThread.start()

def compile(filesToCompile, originalFile):
	compiled_files = []
	filesToCompile = list(set(filesToCompile))
	for filePath in filesToCompile:
		settings = getProjectSetting()
		compileName = os.path.basename(filePath).replace(os.path.splitext(filePath)[1], '.css')
		if os.path.isabs(settings['css-location']):
			compilePath = os.path.join(settings['css-location'], compileName)
		else:
			compilePath = os.path.normpath(os.sep.join([os.path.dirname(filePath), settings['css-location'], compileName]))

		rules = ['--trace', '--stop-on-error', '--style {0}'.format(settings['style'])]
		
		if originalFile not in dirtyFiles:
			rules.append('--force')
		if not settings['cache']:
			rules.append('--no-cache')
		if settings['debug-info']:
			rules.append('--debug-info')
		if settings['line-numbers']:
			rules.append('--line-numbers')
		if settings['cache-location']:
			rules.append('--cache-location \'{0}\''.format(settings['cache-location']))
		if settings['sourcemap']:
			rules.append('--sourcemap')

		cmd = '{0} {1} \'{2}\' \'{3}\''.format(getPluginSettings().get('sass_path'), ' '.join(rules), filePath, compilePath)
		proc = Popen(cmd, shell=True, cwd=os.path.dirname(filePath), stdout=PIPE, stderr=PIPE)
		out, err = proc.communicate()
		if err:
			logError(err)
			return
			
		compiled_files.append(filePath)

		
	sublime.status_message('{0} SASS file(s) compiled.'.format(len(compiled_files)))

	if originalFile in dirtyFiles:
		dirtyFiles.remove(originalFile)


class SassCompileEnableCommand(sublime_plugin.WindowCommand):
	def run(self):
		# self.window.show_quick_panel(['Use Default Settings', 'Customize Settings (Basic)', 'Specify All Settings (Advanced)'], self.on_select_initialize)
		self.on_select_initialize(0)

	def on_select_initialize(self, selectedIndex):
		if selectedIndex == 0:
			promptForSettings = False
		elif selectedIndex == 1 or selectedIndex == 2:
			promptForSettings = selectedIndex
		else:
			return
		initializeDefaultProjectSettings(promptForSettings)

	def is_visible(self):
		return not projectSettingsInitialized()

class SassCompileDisableCommand(sublime_plugin.WindowCommand):
	def run(self):
		deinitializeProjectSettings()

	def is_visible(self):
		return projectSettingsInitialized()

class SassCompileEnableCompileOnSaveCommand(sublime_plugin.WindowCommand):
	def run(self):
		setProjectSetting('compile-on-save', True)

	def is_visible(self):
		return projectSettingsInitialized() and not getProjectSetting('compile-on-save')

class SassCompileDisableCompileOnSaveCommand(sublime_plugin.WindowCommand):
	def run(self):
		setProjectSetting('compile-on-save', False)

	def is_visible(self):
		return projectSettingsInitialized() and getProjectSetting('compile-on-save')

class SassCompileCompileFileCommand(sublime_plugin.WindowCommand):
	def run(self):
		compileOnThread(getFilesToCompile(self.window.active_view().file_name()), self.window.active_view().file_name())

	def is_visible(self):
		return projectSettingsInitialized() and isSassFile(self.window.active_view().file_name())

class SassCompileCommand(sublime_plugin.EventListener):
	def on_pre_save(self, view):
		if projectSettingsInitialized() and isSassFile(view.file_name()) and view.is_dirty():
			dirtyFiles.append(view.file_name())

	def on_post_save(self, view):
		if projectSettingsInitialized() and getProjectSetting('compile-on-save') and isSassFile(view.file_name()) and wasDirty(view.file_name()):
			compileOnThread(getFilesToCompile(view.file_name()), view.file_name())

class SassCompileOpenDefaultConfig(sublime_plugin.WindowCommand):
	def run(self):
		getDefaultProjectSettings()
		self.window.open_file(getUserPath('SassCompile.default-config'))
