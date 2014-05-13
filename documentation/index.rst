.. image:: _static/logo.png
toFeed aims to provide syndication feeds for websites that don't.


Introduction
============
What toFeed does at its core is scraping websites, converting the gathered data into
syndication feed formats, such as RSS or Atom, and exposing the generated feeds
to news aggregators through a web service. It grew out of my desire to be able
to immediately see news from sites I regularly visit and filter them according
to my own preferences.

toFeed relies on third-party modules such as `BeautifulSoup`_, `Jinja2`_ and `Flask`_ to
scrape the websites and generate as well as expose the feeds. Of course that doesn't mean
that you are limited to these modules, writing your own
:doc:`adapter <adapters>` is easy and you are free to use whatever modules you
want to do so. The decision to use `BeautifulSoup`_ instead of `lxml.html`_ was
primarily made to avoid binary dependencies which would make the package less portable and harder to
install for end users. Another reason was that I'm simply more familiar and
comfortable working with `BeautifulSoup`_.


Usage
=====
You can either run toFeed locally on your own PC or externally on a server. It
is recommended to use `virtualenv`_ in either case.

If you are planning on running toFeed locally, simply execute the main module
and the toFeed service should start running on your localhost and expose the
routes to your adapters from there.

Alternatively, if you are interested in setting up an external toFeed instance,
I recommend using `Heroku`_, which allows you to do so at no cost at all. Simply
follow their `Getting Started with Python on Heroku`_ guide from the `Declare
process types with Procfile`_ section onwards.


.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
.. _Jinja2: http://jinja.pocoo.org/
.. _Flask: http://flask.pocoo.org/
.. _lxml.html: http://lxml.de/lxmlhtml.html
.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _Getting Started with Python on Heroku: https://devcenter.heroku.com/articles/getting-started-with-python
.. _Declare process types with Procfile: https://devcenter.heroku.com/articles/getting-started-with-python#declare-process-types-with-procfile

.. _Heroku: https://www.heroku.com/



Modules
=======
.. toctree::
   :maxdepth: 2

   adapters
   formats
   utilities


Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
