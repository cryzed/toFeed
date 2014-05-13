<div align="center">
<img src="http://i.imgur.com/UBKObTR.png"/>
<p>toFeed aims to provide syndication feeds for websites that don't.</p>
</div>


Introduction
============
What toFeed does at its core is scraping websites, converting the gathered data
into syndication feed formats, such as RSS or Atom, and exposing the generated
feeds to news aggregators through a web service. It grew out of my desire to be
able to immediately see news from sites I regularly visit and filter them
according to my own preferences.

toFeed relies on third-party modules such as [BeautifulSoup], [Jinja2] and
[Flask] to scrape the websites and generate as well as expose the feeds. Of
course that doesn't mean that you are limited to these modules, writing your
own adapters is easy and you are free to use whatever modules you want to do
so. The decision to use [BeautifulSoup] instead of [lxml.html] was primarily
made to avoid binary dependencies which would make the package less portable
and harder to install for end users. Another reason was that I'm simply more
familiar and comfortable working with [BeautifulSoup].

The documentation can be found here: http://tofeed.readthedocs.org/


[BeautifulSoup]: http://www.crummy.com/software/BeautifulSoup/
[Jinja2]: http://jinja.pocoo.org/
[Flask]: http://flask.pocoo.org/
[lxml.html]: http://lxml.de/lxmlhtml.html


Usage
=====
You can either run toFeed locally on your own PC or externally on a server. It
is recommended to use [virtualenv] in either case.

If you are planning on running toFeed locally, simply execute the main module
and the toFeed service should start running on your localhost and expose the
routes to your adapters from there.

Alternatively, if you are interested in setting up an external toFeed instance,
I recommend using [Heroku], which allows you to do so at no cost at all. Simply
follow their [Getting Started with Python on Heroku] guide from the [Declare
process types with Procfile] section onwards.


[Heroku]: http://heroku.com/
[Getting Started with Python on Heroku]: https://devcenter.heroku.com/articles/getting-started-with-python
[Declare process types with Procfile]: https://devcenter.heroku.com/articles/getting-started-with-python#declare-process-types-with-procfile


Adapters
========
(This will soon be moved into the documentation)

Parameters are passed via GET parameters and used to instantiate the "Adapter"
class instance. Parameters without a value are interpreted as positional
arguments, and parameters with a value as a keyword argument.

To write your own adapter you need to create a new module in "toFeed.packages"
which has a top-level "ROUTE" attribute. This attribute is the first part of
the route to your actual adapter class. All classes which inherit from the base
adapter class in this module are automatically recognized. Your class needs to
provide a static "ROUTE" attribute as well, which is the second part of the
route to your adapter: for example "twitter/timeline". If the static "PRIMARY"
attribute in your adapter class is set to true, it will also be accessible
simply via the module "ROUTE" attribute, i.e. only "twitter".

You need to add "\*\*kwargs" to the argument list and call this in your
constructor:

    Adapter.__init__(self, **kwargs)

All positional and keyword arguments you define before "\*\*kwargs" in your
constructor can be passed via the GET parameters. The "to_feed"-method needs to
be overriden and return a valid feed syndication format with your content. The
included Python packages in "toFeed.formats" can be used to do that.

To get a better idea, simply take a look at the already existing adapters. If
you create your own adapter I'd be happy to add it to this repository.

Listed below are the currently existing adapters, their routes and the
parameters they accept:


[Patreon]:

  - patreon?\<username\>
  - patreon/activities?\<username\>

    Turns the activity feed found on Patreon pages into an RSS feed. Currently
    posts visible to Patreons only are simply skipped due to me not having paid
    for any projects so far, and thus not being able to write a proper login
    mechanism.

    - max_title_length: Defines the maximum length of the title.


[Twitter]:

  - twitter?\<data_widget_id\>
  - twitter/timelineWidget?\<data_widget_id\>

    Turns the timeline widget data stream into an RSS feed. To retrieve the
    data widget id you need to access your Twitter settings, create a new
    widget and then grab the "data-widget-id" attribute from the JavaScript
    snippet you are provided.


[Picroma]:

  - picroma
  - picroma/blog

  Simply turns wollay's blog into an RSS feed.


[Patreon]: http://patreon.com/
[Twitter]: http://twitter.com/
[Picroma]: https://picroma.com/
