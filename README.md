# Sass Compile
**Sass Compile is a Sass compiler plugin for Sublime Text 3.**

## Features
-   Automatically compiles when Sass files are saved.
-   Only non-partial Sass files are compiled.  
    *A partial Sass file is named with a leading underscore, more information can be found on the [Sass Site](http://sass-lang.com/guide#topic-4)*
-   When compiling is attempted on a partial Sass file, the files that import it are located and compiled instead.
-   The following Sass options are configurable:
    -   css-location
    -   style
    -   syntax
    -   cache
    -   cache-location
    -   sourcemap
    -   line-numbers
    -   debug-info  
    *More options may be added later if needed or requested*
-   Sass compiling is disabled by default and requires a project with a `*.sublime-project` file to be enabled.
-   All Sass options are project specific and stored in the `*.sublime-project` file.
-   The default settings for new projects may be changed to match your needs and get you compiling faster.

## Installation

### From Source
1.  Quit Sublime Text 3
2.  If you already have **Sass Compile** installed, navigate to the packages directory and delete the `Sass Compile` directory.  
    *All user settings will be preserved*
3.  Either clone this GithHub repository into the packages directory or download a ZIP file and unzip it into the packages directory. Stable releases are tagged, it is recommended to use one of them for best results.
4.  Rename the cloned or unzipped directory to `Sass Compile`
5.  Open Sublime Text 3 and start using **Sass Compile**!

*Currently this is the only way to install*

Usage
-----
___Please note that this plugin may only be used in an open project with a saved `*.sublime-project` file.___  
___This functionality may change in the future depending on how users are utilizing the plugin and what their needs are.___

### Enabling *Sass Compile* On A Project
1.  Open the Command Palette and run the command `Sass Compile: (Project) Enable`.
2.  You will be prompted with three choices:
    -   `Use Default Settings` - All settings will be taken from the preset project defaults.
    -   `Customize Settings (Basic)` - You will be prompted to choose the values for the basic settings in the **Project Specific Settings** section below.
    -   `Specify All Settings (Advanced)` - You will be prompted to choose the values for all the settings in the **Project Specific Settings** section below.
3.  Choose the level of control you want to have over the settings and it will guide you through setting up the project settings.
4.  All the chosen settings will be inserted into the `*.sublime-project` file.

### Toggling Compile On Save
If **Sass Compile** has been enabled for the project, open the Command Palette and run either:  
`Sass Compile: Enable Compile On Save` - to enable the feature if it has been disabled.  
**or**  
`Sass Compile: Disable Compile On Save` to disable the feature if it is already enabled.

### Manually Compiling A Sass File
If **Sass Compile** has been enabled for the project and a Sass file is in the current window, open the Command Palette and run `Sass Compile: (File) Compile`.  
_The Sass file extension must match the `syntax` setting in the project settings. See the **Project Specific Settings** section below for more details._  
_The file will be compiled even if no changes have been made, using the `--force` option. This is helpful if any settings have been changed that affect the output format._

### Disabling *Sass Compile* On A Project
If **Sass Compile** has been enabled for the project, open the Command Palette and run `Sass Compile: (Project) Disable`.  
_This will remove the project settings from the ` *.sublime-project` file. If **Sass Compile** is re-enabled, the settings will return to their default values._  
*If you just want to stop Sass files from compiling when saved toggle the compile on save option as described above.*

### Editing Plugin Settings
1.  Navigate to `Preferences -> Package Settings -> Sass Compile` and choose `Settings - User`.
2.  The `SassCompile.sublime-settings` file will be opened.
3.  It will be blank if you have never edited it before. You may copy the default settings from the `Settings - Default` file that can be found under the same menu as in step 1.
4.  Make any changes, save and close the file.

**It is not recommended to make any changes in the default file since it overwritten when updates are installed. Please make all changes in the user file.**

A listing of all the settings and what they do can be found in the **Plugin Settings** section below.

### Editing Project Specific Settings
The project specific settings are stored in the `*.sublime-project` file. You can either find the project file in the project folders sidebar or navigate to `Project -> Edit Project`. You will find the project specific settings in the `sasscompile` section which is in the `settings` section. It will look similar to this:
```json
{
    "folders":
    [
        {
            "follow_symlinks": true,
            "path": "."
        }
    ],
    "settings":
    {
        "sasscompile":
        {
            "setting-name": "value",
            "other-setting-name": "other-value",
            "another-setting-name": "another-value"
        }
    }
}
```
Change any of the values under the `sasscompile` section, then save and close.  
***Do not change any setting names or edit anything outside of the `sasscompile` section.***

A listing of all settings and what they do can be found in the **Project Specific Settings** section below.

### Overriding Default Project Settings
Instead of always starting with the default project settings that come with the plugin and needing to change them manually to what you like to use in your projects, you may specify your own set of defaults.

1.  Navigate to `Preferences -> Package Settings -> Sass Compile` and choose `Default Project Settings - User`
2.  The `SassCompile.default-config` file will be opened and will look similar to this:

    ```json
    {
        "setting-name": "value",
        "other-setting-name": "other-value",
        "another-setting-name": "another-value"
    }
    ```
3.  Change the values to what you want new projects to default to.  
    **Do not change any setting names.**
4.  Save and close the file. The defaults you set will be used the next time you enable **Sass Compile** on a project.

A listing of all settings and what they do can be found in the **Project Specific Settings** section below.

## Plugin Settings
-   `sass_location`: `sass` - Where the Sass script is located on your machine.  
*All other settings are project specific and can be found in the next section.*

## Project Specific Settings
These settings are generated automatically and placed in the project file. Directions on how to edit the settings can be found in the **Usage** section above.

When enabling **Sass Compile** on a project for the first time, it will initialize the settings to the defaults specified below. You may override these defaults with your own set of defaults. Directions on how to do so can be found in the **Usage** section above.

*Settings are displayed in the format: `setting-name`:`default-value`*  

***Basic Settings***
-   `compile-on-save`:`true` - Whether Sass files will be compiled when they are saved.
-   `css-location`:`..` - Where the compiled CSS files should be stored. This can be an absolute or relative path. Relative paths are relative to the Sass file being compiled when started with `.` or `..`  
    *There are plans to add the ability to specify a path relative to the project directory.*
-   `style`:`compressed` - What formatting style should be used when compiling the CSS files.  
    Currently supported styles:
    `nested`, `compact`, `compressed`, and `expanded`  
    *For explanations of what these styles mean, please read the [Sass output style reference](http://sass-lang.com/documentation/file.SASS_REFERENCE.html#output_style)*  

***Advanced Settings***
-   `syntax`:`scss` - Which syntax to compile from. This also determines the file type that can be compiled either manually or automatically.  
    Currently supported syntaxes:
    `scss` and `sass`
-   `cache`:`true` - Whether to cache Sass files to speed up future compilations.
-   `cache-location`:`null` - Where the cache will be stored. Only applicable is `cache` is set to `true`. Relative paths function in the same way as `css-location`.
-   `sourcemap`:`false` - Whether CSS maps will be generated for use with development.
-   `line-numbers`:`false` - Whether line numbers will be generated for use with development.
-   `debug-info`:`false` - Whether debug information will be generated for use by external debuggers.

## Release Notes
- v0.1.0 - Initial launch
- v0.2.0 - User prompts added for enabling **Sass Compile** on a project
- v0.2.1 - Fixed [issue #1](https://github.com/willrowe/sublime-sass-compile/issues/1) that prevented source maps from being disabled.

## Compatibility
*May work in other contexts, but only tested on the following.*
- Mac OS X
- Sublime Text 3

## License
The **Sass Compile** plugin is open-sourced software licensed under the [MIT license](http://opensource.org/licenses/MIT)
