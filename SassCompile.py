import sublime
import sublime_plugin
import json
import os
import traceback
from threading import Thread
from subprocess import PIPE, Popen

dirtyFiles = []
pluginSettings = None
pluginProjectSettings = None
basicPluginProjectSettings = None
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
		userPath = os.sep.join([os.path.dirname(getPluginPath()), "User"])

	if appendPath:
		return os.sep.join([userPath, appendPath])

	return userPath

def logError(errorMessage):
	# outputPanel = sublime.active_window().create_output_panel("sasscompile")
	# outputPanelEdit = outputPanel.begin_edit()
	# outputPanel.insert(outputPanelEdit, outputPanel.size(), "SassCompile Encountered an Error:\n")
	print("Sass Compile Encountered an Error:")
	# outputPanel.insert(outputPanelEdit, outputPanel.size(), err + "\n")
	# outputPanel.end_edit(outputPanelEdit)
	print(errorMessage)
	# outputPanel.
	# sublime.active_window().run_command("show_panel", {"panel": "output.sasscompile"})

def wasDirty(filePath):
	return filePath in dirtyFiles

def getPluginSettings():
	global pluginSettings
	if not pluginSettings:
		pluginSettings = sublime.load_settings("SassCompile.sublime-settings")

	return pluginSettings

def getPluginProjectSettings(useUserDefaults = False):
	global pluginProjectSettings
	if not pluginProjectSettings:
		with open(getPluginPath("SassCompile.settings")) as pluginProjectSettingsFile:
			pluginProjectSettings = json.load(pluginProjectSettingsFile)

	if useUserDefaults:
		defaultProjectSettings = getDefaultProjectSettings()
		for setting in pluginProjectSettings:
			setting["default"] = defaultProjectSettings[setting["name"]]
	return pluginProjectSettings.copy()

def getBasicPluginProjectSettings(useUserDefaults = False):
	global basicPluginProjectSettings
	if not basicPluginProjectSettings:
		basicPluginProjectSettings = []
		for setting in getPluginProjectSettings(useUserDefaults):
			if not setting["advanced"]:
				basicPluginProjectSettings.append(setting)

	return basicPluginProjectSettings.copy()

def getDefaultPluginProjectSettings():
	global defaultPluginProjectSettings
	if not defaultPluginProjectSettings:
		defaultPluginProjectSettings = {}
		for setting in getPluginProjectSettings():
			defaultPluginProjectSettings[setting["name"]] = setting["default"]

	return defaultPluginProjectSettings.copy()

def getDefaultProjectSettings():
	defaultProjectSettings = getDefaultPluginProjectSettings()

	userDefaultSettingsPath = getUserPath("SassCompile.default-config")
	userDefaultSettings = None
	if os.path.isfile(userDefaultSettingsPath):
		with open(userDefaultSettingsPath) as userDefaultSettingsFile:
			userDefaultSettings = json.load(userDefaultSettingsFile)

		for settingName, defaultValue in userDefaultSettings.items():
			if settingName in defaultProjectSettings:
				defaultProjectSettings[settingName] = defaultValue

	if not userDefaultSettings or set(userDefaultSettings) ^ set(defaultProjectSettings):
		with open(userDefaultSettingsPath, "w") as userDefaultSettingsFile:
			json.dump(defaultProjectSettings, userDefaultSettingsFile, indent=4)

	return defaultProjectSettings

def initializeDefaultProjectSettings(promptLevel = 0):
	if promptLevel == 0:
		initializationInputDone()
	elif promptLevel > 0:
		if promptLevel == 1:
			promptSettings = getBasicPluginProjectSettings(True)
		elif promptLevel == 2:
			promptSettings = getPluginProjectSettings(True)

		UserInputList(promptSettings, initializationInputDone, formatQuestionCallback)

def initializationInputDone(answers = None):
	initialSettings = getDefaultProjectSettings()
	if answers:
		for name, answer in answers.items():
			initialSettings[name] = answer
	setProjectSetting(initialSettings)
	sublime.status_message("Sass Compile is now enabled for this project.")

def formatQuestionCallback(question, type):
	if type == UserInputList.QUICK_PANEL:
		return [question["title"] + " (" + question["name"] + ")", question["question"]]
	elif type == UserInputList.INPUT_PANEL:
		return question["title"] + " (" + question["name"] + ") - " + question["question"]

def deinitializeProjectSettings():
	projectData = sublime.active_window().project_data()
	projectData["settings"].pop("sasscompile")
	if len(projectData["settings"]) == 0:
		projectData.pop("settings")

	sublime.active_window().set_project_data(projectData)
	sublime.status_message("Sass Compile has been disabled for this project.")

def getProjectSetting(name = None):
	projectData = sublime.active_window().project_data()

	upgradeProjectSettings(projectData["settings"]["sasscompile"])

	if name != None:
		return projectData["settings"]["sasscompile"][name]

	return projectData["settings"]["sasscompile"].copy()

def setProjectSetting(name, value = None):
	projectData = sublime.active_window().project_data()

	if "settings" not in projectData:
		projectData["settings"] = {}
	if "sasscompile" not in projectData["settings"]:
		projectData["settings"]["sasscompile"] = {}

	if value != None:
		projectData["settings"]["sasscompile"][name] = value
	else:
		projectData["settings"]["sasscompile"] = name

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
		if "settings" in projectData.keys():
			if "sasscompile" in projectData["settings"].keys():
				return True

	return False

def isSassFile(filePath):
	if os.path.splitext(filePath)[1][1:] == getProjectSetting("syntax"):
		return True
	return False

def getFilesToCompile(filePath):
	if os.path.basename(filePath).startswith("_"):
		return getImportParents(filePath)
	return [filePath]

def getImportParents(filePath):
	importName = os.path.basename(filePath).split(".")[0][1:]
	cmd = "grep -E '@import.*{0}' * -l".format(importName)
	proc = Popen(cmd, shell=True, cwd=os.path.dirname(filePath), stdout=PIPE, stderr=PIPE)
	out, err = proc.communicate()
	if err:
		logError(err)
		return

	if not out:
		return

	files = []
	out = out.decode("utf8")
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
		compileName = os.path.basename(filePath).replace(os.path.splitext(filePath)[1], ".css")
		if os.path.isabs(settings["css-location"]):
			compilePath = os.path.join(settings["css-location"], compileName)
		else:
			compilePath = os.path.normpath(os.sep.join([os.path.dirname(filePath), settings["css-location"], compileName]))

		rules = ["--trace", "--stop-on-error", "--style {0}".format(settings["style"])]

		if originalFile not in dirtyFiles:
			rules.append("--force")
		if not settings["cache"]:
			rules.append("--no-cache")
		if settings["debug-info"]:
			rules.append("--debug-info")
		if settings["line-numbers"]:
			rules.append("--line-numbers")
		if settings["cache-location"]:
			rules.append("--cache-location \'{0}\'".format(settings["cache-location"]))
		if not settings["sourcemap"]:
			rules.append("--sourcemap=none")

		cmd = "{0} {1} \'{2}\' \'{3}\'".format(getPluginSettings().get("sass_path"), " ".join(rules), filePath, compilePath)
		proc = Popen(cmd, shell=True, cwd=os.path.dirname(filePath), stdout=PIPE, stderr=PIPE)
		out, err = proc.communicate()
		if err:
			logError(err)
			return

		compiled_files.append(filePath)


	sublime.status_message("{0} SASS file(s) compiled.".format(len(compiled_files)))

	if originalFile in dirtyFiles:
		dirtyFiles.remove(originalFile)


class SassCompileEnableCommand(sublime_plugin.WindowCommand):
	def run(self):
		self.window.show_quick_panel([["Use Default Settings", "All settings will be initialized using the current defaults."], ["Customize Settings (Basic)", "Choose custom values for the most common settings."], ["Specify All Settings (Advanced)", "Choose custom values for all of the available settings."]], initializeDefaultProjectSettings)
		# initializeDefaultProjectSettings()

	def is_visible(self):
		return not projectSettingsInitialized()

class SassCompileDisableCommand(sublime_plugin.WindowCommand):
	def run(self):
		deinitializeProjectSettings()

	def is_visible(self):
		return projectSettingsInitialized()

class SassCompileEnableCompileOnSaveCommand(sublime_plugin.WindowCommand):
	def run(self):
		setProjectSetting("compile-on-save", True)

	def is_visible(self):
		return projectSettingsInitialized() and not getProjectSetting("compile-on-save")

class SassCompileDisableCompileOnSaveCommand(sublime_plugin.WindowCommand):
	def run(self):
		setProjectSetting("compile-on-save", False)

	def is_visible(self):
		return projectSettingsInitialized() and getProjectSetting("compile-on-save")

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
		if projectSettingsInitialized() and getProjectSetting("compile-on-save") and isSassFile(view.file_name()) and wasDirty(view.file_name()):
			compileOnThread(getFilesToCompile(view.file_name()), view.file_name())

class SassCompileOpenDefaultConfig(sublime_plugin.WindowCommand):
	def run(self):
		getDefaultProjectSettings()
		self.window.open_file(getUserPath("SassCompile.default-config"))

class UserInputList():
	QUICK_PANEL = 0
	INPUT_PANEL = 1

	questions = None
	questionIndex = 0
	completeCallback = None
	questionFormatCallback = None
	cancelCallback = None
	answers = {}
	resetIndex = False

	def __init__(self, questions, completeCallback, questionFormatCallback = None, cancelCallback = None):
		self.questions = questions
		self.completeCallback = completeCallback
		self.questionFormatCallback = questionFormatCallback
		self.promptQuestion(False)

	def promptQuestion(self, delayed = True, resetIndex = False):
		currentQuestion = self.questions[self.questionIndex]

		if currentQuestion["type"] == "boolean" or type(currentQuestion["type"]) is list:
			if delayed:
				if self.questionFormatCallback:
					choices = [self.questionFormatCallback(currentQuestion, self.QUICK_PANEL)]
				else:
					choices = [currentQuestion["question"]]
				if currentQuestion["type"] == "boolean":
					choices.extend(["Yes", "No"])
					if currentQuestion["default"] == True:
						defaultIndex = 1
					else:
						defaultIndex = 2
				elif type(currentQuestion["type"]) is list:
					choices.extend(currentQuestion["type"])
					defaultIndex = currentQuestion["type"].index(currentQuestion["default"]) + 1

				if self.resetIndex:
					self.resetIndex = False
					defaultIndex = 1

				sublime.active_window().show_quick_panel(choices, self.recordAnswer, 0, defaultIndex)
			else:
				if resetIndex:
					self.resetIndex = True
				sublime.set_timeout(self.promptQuestion, 100)

		elif currentQuestion["type"] == "text":
			if self.questionFormatCallback:
				caption = self.questionFormatCallback(currentQuestion, self.INPUT_PANEL)
			else:
				caption = currentQuestion["question"]
			default = currentQuestion["default"] if currentQuestion["default"] else ""
			sublime.active_window().show_input_panel(caption, default, self.recordAnswer, None, self.cancelCallback)

	def recordAnswer(self, answer):
		currentQuestion = self.questions[self.questionIndex]

		if currentQuestion["type"] == "boolean" or type(currentQuestion["type"]) is list:
			if answer == -1:
				if self.cancelCallback:
					self.cancelCallback()
				return
			elif answer == 0:
				self.promptQuestion(False, True)
				return
			else:
				if currentQuestion["type"] == "boolean":
					if answer == 1:
						currentAnswer = True
					elif answer == 2:
						currentAnswer = False
				elif type(currentQuestion["type"]) is list:
					currentAnswer = currentQuestion["type"][answer - 1]
		elif currentQuestion["type"] == "text":
			if answer == -1:
				return
			else:
				currentAnswer = answer

		self.answers[currentQuestion["name"]] = currentAnswer
		self.questionIndex += 1

		if self.questionIndex == len(self.questions):
			self.completeCallback(self.answers)
		else:
			self.promptQuestion(False)
