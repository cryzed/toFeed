toFeed
======
toFeed aims to provide syndication feeds for websites that don't.


Adapters
--------
Below the currently supported adapters and their routes are listed.

- Patreon
    - patreon/activities?<username>

- Twitter
    - twitter/timeline?<data_widget_id>[&max_title_length=<max_title_length>]


Usage
-----
Simply run main.py locally or via a WSGI-server and enter the correct routes
as the feed URLs into your feed reader of choice. To use the Twitter timeline
route you currently need to create a new widget in your twitter settings for
the person you want to follow, and then copy the "data-widget-id" attribute
from the JavaScript snippet they provide you.
