Bark
====

Bark is a single file static site generator. I set out to make it primarily because I got tired of dealing with Jekyll and didn't want to put a bunch of effort into tweaking Pelican to look alright.

I hope to continually improve it so perhaps others might find it useful.

Features
--------

* Single file
* Jinja2 templating language
* Posts support markdown formatting thanks to Hoedown with SmartyPants.

Installation
------------

You can install using the source by simply using::

    python setup.py install --user

or::

    sudo python setup.py install
    
for system wide installation.

Usage
-----

Usage: ``bark [options] (new NAME|make [SETTINGS])``

-h, --help       Show this message.
--version        Show version.


Contributing
------------

If something is wrong or could be improved, let me know or submit a pull request.

To do
-----

Over the past couple weeks I've noticed that I made this pretty bad, so here's my to do list.

* Need to ditch JSON settings for key=val or possibly just use ConfigParser
* Need to completely revamp how templates are loaded and used
    * Drop DictLoader with base templates and stop looking for templates by a specific name. Instead load templates from a specified folder. 
* Keep directory for posts, templates, etc, but hide anything that will not be parsed as Markdown for rendering that is prepended with '_' in the filename. Such as _content and _templates. Things like static, images, about will be rendered though. Naturally the configuration file will be ignored. Possibly create a separate directory for storing large sets of data? If so, what format? JSON, YAML, ?
* Pagination, straightforward to implement, include pagination object/dict.
* More descriptive console output when building; verbosity levels.
* Better and more numerous configuration options that override the settings for quick fixes, checks, etc. Possibly demo the site using SimpleHTTPServer.
