Sass Compile
============
**Sass Compile is a Sass compiler plugin for Sublime Text 3.**

Available Features
------------------
-   Automatically compiles when Sass files are saved.
-   Only non-partial Sass files (file name does not begin with an underscore) are compiled.
-   A partial Sass file determines what files import it and compile those.
-   The following Sass options are configurable:
    -   css-location
    -   style
    -   syntax
    -   cache
    -   cache-location
    -   sourcemap
    -   line-numbers
    -   debug-info  
    _More options may be added later if needed or requested_
-   Sass compiling is disabled by default and requires a project with a `*.sublime-project` file to be enabled.
-   All Sass options are project specific and stored in the `*.sublime-project` file.
-   The default settings for new projects may be changed to match your needs and get you compiling faster.

Installing
----------

Plugin Settings
----------------
-   `sass_location`: `sass` - Where the Sass script is located on your machine.  
_All other settings are project specific and can be found in the next section._

Project Specific Settings
-------------------------
-   `compile-on-save`:`true` - Whether Sass files will be compiled when they are saved.
-   `css-location`:`..` - Where the compiled CSS files should be stored. This can be an absolute or relative path. Relative paths are relative to the Sass file being compiled when started with `.` or `..`  
    _There are plans to add the ability to specify a path relative to the project directory._
-   `style`:`compressed` - What formatting style should be used when compiling the CSS files.  
    Currently supported styles:
    `nested`, `compact`, `compressed`, and `expanded`  
    _For explanations of what these styles mean, please read the [Sass output style reference](http://sass-lang.com/documentation/file.SASS_REFERENCE.html#output_style)_
-   `syntax`:`scss` - Which syntax to compile from. This also determines the file type that will automatically compile.  
    Currently supported syntaxes:
    `scss` and `sass`
-   `cache`:`true` - Whether to cache Sass files to speed up future compilations.
-   `cache-location`:`null` - Where the cache will be stored. Only applicable is `cache` is set to `true`. Relative paths function in the same way as `css-location`.
-   `sourcemap`:`false` - Whether CSS maps will be generated for use with development.
-   `line-numbers`:`false` - Whether line numbers will be generated for use with development.
-   `debug-info`:`false` - Whether debug information will be generated for use by external debuggers.

Notes
------
-   At this point the plugin has only been tested on Mac OS X