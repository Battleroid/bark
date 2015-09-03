"""Bark

Usage:
    bark new <name>
    bark make [<settings>]

Options:
    -h --help  Show this screen.
    --version  Show version.
"""
__author__ = 'Casey Weed'
__version__ = '1.3.1'

from docopt import docopt
import json
import errno
import shutil
from hoedown import Markdown, HtmlRenderer, SmartyPants
from datetime import datetime
import sys
import os
from slugify import slugify
from dateutil import parser
import frontmatter as ft
from jinja2 import Environment, FileSystemLoader, Template, DictLoader


def walk_files(start):
    for root, dirs, files in os.walk(start):
        for f in files:
            yield os.path.join(root, f)


def walk_directories(start):
    for root, dirs, files in os.walk(start):
        for d in dirs:
            yield os.path.join(root, d)


def mkdirp(path):
    """
    Replicate mkdir -p functionality.
    """
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


BASE_BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
        <meta charset="UTF-8">
        <title>{{ settings.site_name }}</title>
        <style type="text/css">
            body {
                font: 14px/1.5em sans-serif;
            }
        </style>
</head>
<body>
        <h1>{% if settings.site_url %}<a href="{{ settings.site_url }}">{{ settings.site_name }}</a>{% else %}{{ settings.site_name }}{% endif %}</h1>
        <small>by {{ settings.site_author }}</small>
        <article>
                {% block content %}
                {% endblock %}
        </article>
</body>
</html>"""

BASE_INDEX = """
{% extends "base.html" %}

{% block content %}
<ul>
        {% for post in posts -%}
        <li><a href="{% if settings.site_url %}{{ settings.site_url }}/{% endif %}{{ post.url }}">{{ post.title }}</a></li>
        {% endfor %}
</ul>
{% endblock %}"""

BASE_POST = """
{% extends "base.html" %}

{% block content %}
<h3>{{ post.title }}</h3>
<small>By {{ post.author }} at {{ post.date }}</small>

{{ post.rendered }}
{% endblock %}"""

BASE_TEMPLATES = {
    'base.html': BASE_BASE,
    'index.html': BASE_INDEX,
    'post.html': BASE_POST
}

class HtmlRenderer(HtmlRenderer, SmartyPants):
    pass

class Post(object):
    def __init__(self, filename, settings):
        self.filename = filename
        self.matter = ft.load(self.filename).to_dict()
        self.title = self.matter.get('title', 'Unremarkable Post')
        self.author = self.matter.get('author', 'Anonymous')
        self.category = self.matter.get('category', None)
        self.slug = self.matter.get('slug', slugify(self.title))
        self.url = '.'.join([self.slug, 'html'])
        if self.category:
            self.url = '/'.join([self.category, self.url])
        if 'date' in self.matter:
            d = parser.parse(self.matter['date'])
            self.date = d.strftime('%Y-%m-%d %H:%M')
        else:
            self.date = self.get_create_time(filename)
        self.raw = self.matter.get('content', '')
        self.html = Markdown(HtmlRenderer()).render(self.raw)
        self.rendered = Template(self.html).render(post=self, settings=settings)

    def get_create_time(self, filename):
        created = datetime.fromtimestamp(os.stat(filename).st_ctime)
        return created.strftime('%Y-%m-%d %H:%M')


class Settings(object):
    def __init__(self, settings):
        self.templates = settings.get('templates', None)
        self.static = settings.get('static', 'static')
        self.content = settings.get('content', 'content')
        self.output = settings.get('output', 'output')
        self.site_name = settings.get('site_name', 'My Blog')
        self.site_author = settings.get('site_author', 'Anonymous')
        self.site_url = settings.get('site_url', None)
        self.misc = settings.get('misc', {})


class Engine(object):
    def __init__(self, settings):
        self.settings = Settings(settings)
        self.files = []
        self.posts = []
        self.categories = set()
        self.jinja = Environment()
        if self.settings.templates:
            self.jinja.loader = FileSystemLoader(self.settings.templates)
        else:
            self.jinja.loader = DictLoader(BASE_TEMPLATES)
        self.jinja.globals = dict(settings=self.settings, posts=self.posts)

    def load_posts(self):
        """
        Load markdown (.md) posts from our content directory.
        """
        print 'Looking for content in "{}":'.format(self.settings.content)
        for f in walk_files(self.settings.content):
            if f.endswith(('.md', '.MD')):
                self.files.append(f)
                print '+ Loaded "{}"'.format(os.path.basename(f))

    def order_posts(self):
        """
        Order the posts according to date.
        """
        for f in self.files:
            post = Post(f, self.settings)
            if post.category:
                self.categories.add(post.category)
            self.posts.append(post)
        self.posts = sorted(self.posts, key=lambda p: p.date, reverse=True)

    def prepare_output(self):
        """
        Prep output directories, move static files, and copy post category
        directory tree.
        """
        if not os.path.exists(self.settings.output):
            os.mkdir(self.settings.output)
        try:
            shutil.copytree(self.settings.static,
                            os.path.join(self.settings.output,
                                         self.settings.static))
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(self.settings.static):
                pass
            else:
                raise
        for f in walk_files(self.settings.static):
            dest = os.path.join(self.settings.output, f)
            try:
                shutil.copy(f, dest)
            except OSError as e:
                if e.errno == errno.EEXIST and os.path.isfile(dest):
                    pass
                else:
                    raise
        category_dirs = [os.path.join(self.settings.output, category)
                         for category in self.categories]
        for c in category_dirs:
            mkdirp(c)

    def build_index(self):
        """
        Create the index, save in output.
        """
        print '+ Building index'
        index_tmpl = self.jinja.get_template('index.html')
        with open(os.path.join(self.settings.output, 'index.html'), 'w') as f:
            f.write(index_tmpl.render())

    def build_posts(self):
        """
        Render posts, save output in appropriate category or default output
        directory.
        """
        post_tmpl = self.jinja.get_template('post.html')
        for post in self.posts:
            with open(os.path.join(self.settings.output, post.url), 'w') as f:
                print '+ Building {}'.format(post.url)
                f.write(post_tmpl.render(post=post, settings=self.settings))

    def build(self):
        self.load_posts()
        self.order_posts()
        self.prepare_output()
        self.build_index()
        self.build_posts()
        print 'Finished'


def create_new_site(location):
    """
    Create new blank site at location. Includes basic settings file, templates,
    and content directory.
    """
    if not os.path.exists(location):
        os.mkdir(location)
    defaults = Settings({})
    if not defaults.templates:
        defaults.templates = 'templates'
    if not os.path.exists(os.path.join(location, defaults.templates)):
        os.mkdir(os.path.join(location, defaults.templates))
    if not os.path.exists(os.path.join(location, defaults.content)):
        os.mkdir(os.path.join(location, defaults.content))
    if not os.path.exists(os.path.join(location, defaults.static)):
        os.mkdir(os.path.join(location, defaults.static))
    for name, content in BASE_TEMPLATES.iteritems():
        with open(os.path.join(location, defaults.templates, name), 'w') as f:
            f.write(content)
    with open(os.path.join(location, 'settings.json'), 'w') as f:
        f.write(json.dumps(defaults.__dict__))


def parse_args():
    arguments = docopt(__doc__, version='Bark {}'.format(__version__))
    if arguments['new']:
        if arguments['<name>']:
            create_new_site(arguments['<name>'])
            sys.exit(0)
        create_new_site('myblog')
    if arguments['make']:
        if arguments['<settings>']:
            config = open(arguments['<settings>'], 'r').read()
            settings = json.loads(config)
            engine = Engine(settings)
            engine.build()
            sys.exit(0)
        config = open('settings.json', 'r').read()
        settings = json.loads(config)
        engine = Engine(settings)
        engine.build()
        sys.exit(0)


def main():
    parse_args()
