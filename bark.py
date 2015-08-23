import json
from slugify import slugify
from dateutil import parser
import misaka as ms
import frontmatter as ft
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, Markup, Template
from datetime import datetime
import sys
import os

def walk_folder(start):
    for root, dirs, files in os.walk(start):
        for f in files:
            yield os.path.join(root, f)

class Post(object):

    def __init__(self, filename):
        self.filename = filename
        self.matter = ft.load(self.filename).to_dict()
        self.title = self.matter.get('title', 'Unremarkable Post')
        self.author = self.matter.get('author', 'Anonymous')
        self.slug = self.matter.get('slug', slugify(self.title))
        self.url = '.'.join([self.slug, 'html'])
        if 'date' in self.matter:
            d = parser.parse(self.matter['date'])
            self.date = d.strftime('%Y-%m-%d %H:%M')
        else:
            self.date = self.get_create_time(filename)
        self.content = self.matter.get('content', 'No content.')
        # self.html = ms.html(self.content)
        # TODO: Use template to create a template from string, store the result as html
        t = Template(self.content)
        self.html = ms.html(t.render(post=self))

    @classmethod
    def get_create_time(cls, filename):
        created = datetime.fromtimestamp(os.stat(filename).st_ctime)
        return created.strftime('%Y-%m-%d %H:%M')

class Settings(object):

    def __init__(self, settings):
        self.templates = settings.get('templates', 'templates')
        self.static = settings.get('static', 'static')
        self.content = settings.get('content', 'content')
        self.output = settings.get('output', 'output')
        self.site_name = settings.get('site_name', 'My Blog')
        self.site_author = settings.get('site_author', 'Anonymous')
        self.site_url = settings.get('site_url', '/')
        self.misc = settings.get('misc', {})

class Engine(object):

    def __init__(self, settings):
        self.settings = Settings(settings)
        self.files = []
        self.posts = []
        self.jinja = Environment()
        self.jinja.loader = FileSystemLoader(self.settings.templates)
        self.jinja.globals = dict(settings=self.settings, posts=self.posts)

    def load_files(self):
        print 'Looking for content in "{}":'.format(self.settings.content)
        for f in walk_folder(self.settings.content):
            if f.endswith(('.md', '.MD')):
                self.files.append(f)
                print '+ Loaded "{}"'.format(os.path.basename(f))

    def grab_template(self, name):
        try:
            return self.jinja.get_template(name, globals=self.settings)
        except TemplateNotFound, e:
            print e.message

    def prepare_output(self):
        # TODO: prepare output by genning dirs, copying static files, etc
        pass

    def build_index(self):
        # TODO: save index to output
        index = self.jinja.get_or_select_template('index.html')
        print index.render()

    def build_posts(self):
        post = self.jinja.get_template('post.html')
        for p in self.posts:
            # TODO: save render to file in output directory
            t = Template(p.content)
            html = ms.html(t.render(post=p, settings=self.settings))
            print post.render(html)

    def assess_posts(self):
        for f in self.files:
            self.posts.append(Post(f))
        self.posts = sorted(self.posts, key=lambda p: p.date)

    def build(self):
        self.load_files()
        self.assess_posts()
        self.build_index()
        self.build_posts()


if __name__ == '__main__':
    config = open(sys.argv[1], 'r').read()
    settings = json.loads(config)
    engine = Engine(settings)
    engine.build()
