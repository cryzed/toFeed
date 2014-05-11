<div align="center">
<img src="http://i.imgur.com/0kbZEwI.png"/>
<p>toFeed aims to provide syndication feeds for websites that don't.</p>
</div>


Adapters
--------
Parameters are passed via GET parameters and used to instantiate the "Adapter"
class instance. Parameters without a value are interpreted as positional
arguments, and parameters with a value as a keyword argument.

To write your own adapter you need to create a new module in "toFeed.packages"
which has a top-level "ROUTE" attribute. This attribute is the first part
of the route to your actual adapter class. All classes which inherit from the
base adapter class in this module are automatically recognized. Your class
needs to provide a static "ROUTE" attribute as well, which is the second part
of the route to your adapter: for example "twitter/timeline". If the static
"PRIMARY" attribute in your adapter class is set to true, it will also be
accessible simply via the module "ROUTE" attribute, i.e. only "twitter".

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


[Patreon](http://patreon.com/):

  - patreon?\<username\>
  - patreon/activities?\<username\>

    Turns the activity feed found on Patreon pages into an RSS feed.
    Currently posts visible to Patreons only are simply skipped due to me
    not having paid for any projects so far, and thus not being able to write
    a proper login mechanism.

    - max_title_length: Defines the maximum length of the title, after which
      it is cropped with "...".


[Twitter](http://twitter.com/):

  - twitter?\<data_widget_id\>
  - twitter/timelineWidget?\<data_widget_id\>

    Turns the timeline widget data stream into an RSS feed. To retrieve the
    data widget id you need to access your Twitter settings, create a new
    widget and then grab the "data-widget-id" attribute from the JavaScript
    snippet you are provided.

  - twitter/primitive?\<username\>

    Turns the regular twitter feed into an RSS feed. Simply use the username
    as an argument. Apparently there are different kind of Twitter pages, so
    don't expect this to work for all users. Using the timeline widget adapter
    is a way better option.


[Picroma](https://picroma.com/)

  - picroma

  Simply turns wollay's blog into an RSS feed.


Usage
-----
toFeed is designed to be run either locally on your own PC or on your own
web server. Simply execute "main.py" and the toFeed service should start
running on http://127.0.0.1:5000/ and expose the routes to your adapters
from there.

If you want to run toFeed on a web server, but don't own one, check out the
awesome service [Heroku](http://heroku.com/) where you can get one for free.
