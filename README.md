# Bark

Bark is a single file static site generator. I set out to make it primarily because I got tired of dealing with Jekyll and didn't want to put a bunch of effort into tweaking Pelican to look alright.

I hope to continually improve it so perhaps others might find it useful.

### Features

* Single file
* Jinja2 templating language
* Posts support markdown formatting thanks to Misaka with SmartyPants.

### Installation

    python setup.py install --user

or

    sudo python setup.py install
    
for system wide installation.

### Usage

    Usage:
        bark new <name>
        bark make [<settings>]

    Options:
        -h --help  Show this screen.
		--version  Show version.

### Contributing

If something is wrong or could be improved, let me know or submit a pull request.

### To Do

- [x] set it up with ~~argparse~~ docopt for basic command line options
- [ ] ability to set your own layouts per post, this will also allow you to create separate pages
- [ ] default templates are only loaded if they are not found within the template directory
- [ ] I feel like there should be a better way to render the posts without replicating settings over and over
