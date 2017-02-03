===================
JSON Cut By Example
===================
.. figure:: docs/source/_static/logger.jpg
   :scale: 15 %
   :align: left

   a JSON pruning tool

**Python 3 support only**; *jsoncut is not currently supported under Python 2*.

.. code-block:: console

  $ jsoncut --help
  Usage: cli.py [OPTIONS] [JSONFILE]

    Quickly select or filter out properties in a JSON document.

  Options:
    -r, --root TEXT                 Set the root of the JSON document.
    -g, --get TEXT                  Get JSON object members and/or array
                                    elements.
    -G, --getdefault <TEXT TEXT>... 
                                    Same as --get, except provides a default
                                    value to be used when a key/index is not
                                    found (key, default-value)
    -p, --fullpath                  Works with --get; uses the full key
                                    path for the destination key name.
    -d, --del TEXT                  Deletes JSON object members and/or array
                                    elements.
    -a, --any                       Works with --get & --del; instructs
                                    jsoncut to ignore any key not found
                                    errors.
    -l, --list                      Generates a numbered list of JSON keys;
                                    crawls through all keys in the 1st
                                    JSON object found; list doesn't crawl
                                    through JSON arrays.
    -f, --fullscan                  Works with --list; searches for keys
                                    in all JSON objects, not just the 1st
                                    one.
    -i, --inspect                   Inspect JSON document; crawls through
                                    all keys & indexes in the entire
                                    document; displays keys found, array
                                    locations, JSON types, min & max values,
                                    lengths and/or counts.
    -q, --doublequote TEXT          Set quoting character used around
                                    command parameters; useful for the Windows
                                    command-console which uses double-quotes
                                    rather than the default single-quotes;
                                    elimates having to escape quote
                                    characters around keynames.
    -I, --indent INTEGER            The default format when redirecting JSON
                                    output is compact JSON; this option
                                    instead indents the output for human
                                    readibility.
    -c, --nocolor                   Disable syntax highlighting.
    -s, --slice                     Used when the root of the JSON document
                                    is an array; the default is to iterate
                                    through that array; this option disables
                                    iteratation so that the root-level array
                                    can be sliced.
    --version                       Show the version and exit.
    --help                          Show this message and exit.


Common Usage Scenarios
-----------------------
* Point to an array of objects within the JSON document with 'root' and
  use 'get', 'getdefault' or 'del' to operate on each object.
* Use root to get a branch or a value from the document. 
* Use slice option to extract elements from a JSON array.
* There are other ways to use it, but these are the most common.

Selecting JSON keys
-------------------
Keys are specified in dot-notation and can be:
  * A key name
  * A Key number (use --list to show the key numbers)
  * An index number.
  * A Python-style slice (only the last key can be a slice)

JSON Key Examples
^^^^^^^^^^^^^^^^^

===================== ==================
1                     key #
.1                    key name
store                 key name
store.book            key names
store.book.2          key names w/ index
store.book.-1.price   key names /w index
store.book.:2         key name /w slice
===================== ==================

Installation
------------

.. code-block:: console

    $ pip install pygments jsoncut

.. note::

    Pygments is not required by jsoncut, but if installed it can provide
    syntax highlighting for any JSON written to STDOUT.


Loading the JSON document
-------------------------
If the jsonfile argument is:
  1. Left blank it will load the JSON document from STDIN if data
     is available, otherwise it will print a jsoncut usage message and exit.
  2. A dash character '-', it will load the JSON document from STDIN if
     data is available otherwise it will wait for the user to input data.
  3. A path/filename, it will load the JSON data from the file


Generated Key Numbers
---------------------
.. code-block:: console

     $ http earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson|jsoncut -l
      1 bbox
      2 features
      3 metadata
      4 metadata.api
      5 metadata.count
      6 metadata.generated
      7 metadata.status
      8 metadata.title
      9 metadata.url
     10 type


Select Root Key
---------------

By Key Number
^^^^^^^^^^^^^

.. code-block:: console

  $ http earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson|jsoncut -lr2
   1 geometry
   2 geometry.coordinates
   3 geometry.type
   4 id
   5 properties
   6 properties.alert
   7 properties.cdi
   8 properties.code
   9 properties.detail
  10 properties.dmin
  11 properties.felt
  12 properties.gap
  13 properties.ids
  14 properties.mag
  15 properties.magType
  16 properties.mmi
  17 properties.net
  18 properties.nst
  19 properties.place
  20 properties.rms
  21 properties.sig
  22 properties.sources
  23 properties.status
  24 properties.time
  25 properties.title
  26 properties.tsunami
  27 properties.type
  28 properties.types
  29 properties.tz
  30 properties.updated
  31 properties.url
  32 type

Or Key Name
^^^^^^^^^^^

.. code-block:: console

  $ http earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson|jsoncut -lr features
   1 geometry
   2 geometry.coordinates
   3 geometry.type
   ...


Get Keys
--------

.. code-block:: console

    $ http earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson|jsoncut -r2 -g 2,14,18

.. code-block:: json

    [
      {
        "mag": 1.45,
        "nst": 15,
        "coordinates": [
          -122.7269974,
          38.7626648,
          2.14
        ]
      },
      {
        "mag": 0.8,
        "nst": null,
        "coordinates": [
          -152.3008,
          61.4323,
          9.3
        ]
      },
      {
        "mag": 1,
        "nst": 27,
        "coordinates": [
          -116.4545,
          33.4861667,
          17.09
        ]
      },
      {
        "mag": 0.88,
        "nst": 9,
        "coordinates": [
          -118.8696671,
          37.6593323,
          1.43
        ]
      },
      {
        "mag": 1.4,
        "nst": null,
        "coordinates": [
          -147.7345,
          63.5458,
          0
        ]
      },
      {
        "mag": 0.92,
        "nst": 24,
        "coordinates": [
          -117.1195,
          33.9543333,
          13.04
        ]
      }
    ]

Key Names & Numbers can be Mixed
--------------------------------

.. code-block:: console

    jsoncut.cli -r features -g 2,14,18,properties.nst


Drop Keys
---------

.. code-block:: console

    http earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson|jsoncut -d features

.. code-block:: json

    {
      "type": "FeatureCollection",
      "metadata": {
        "generated": 1485141344000,
        "url": "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
        "title": "USGS All Earthquakes, Past Hour",
        "status": 200,
        "api": "1.5.4",
        "count": 7
      },
      "bbox": [
        -150.8798,
        33.495,
        1.89,
        -116.7903333,
        62.4321,
        78.9
      ]
    }

.. code-block:: console

    $ jsoncut.cli -r2 -g23-26,31-

.. code-block:: json

    [
      {
        "status": "automatic",
        "time": 1486089565460,
        "title": "M 1.1 - 4km WNW of Cobb, California",
        "tsunami": 0,
        "url": "http://earthquake.usgs.gov/earthquakes/eventpage/nc72759275",
        "type": "Feature"
      },
      {
        "status": "automatic",
        "time": 1486088328647,
        "title": "M 1.5 - 33km NNE of Anchor Point, Alaska",
        "tsunami": 0,
        "url": "http://earthquake.usgs.gov/earthquakes/eventpage/ak15193555",
        "type": "Feature"
      }
    ]


Inspect JSON document
---------------------
Let's say we know the JSON contains a list of earthquakes, but are not sure
which of the above keys contains that information.  We can use inspect to
crawl through the entire JSON document looking for both unique keys and
array locations and unique keys.  Array indexes are represented by the
'#' wildcard character.

.. code-block:: console

  $ http earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson|jsoncut -i
  bbox                              :array(count=6)
  bbox.#                            :number(minval=-152.1395, maxval=64.7845)
  features                          :array(count=5)
  features.#                        :object(keys=4)
  features.#.geometry               :object(keys=2)
  features.#.geometry.coordinates   :array(count=3)
  features.#.geometry.coordinates.# :number(minval=-152.1395, maxval=64.7845)
  features.#.geometry.type          :text(len=5)
  features.#.id                     :text(len=10)
  features.#.properties             :object(keys=26)
  features.#.properties.alert       :null
  features.#.properties.cdi         :null | number(val=4.1)
  features.#.properties.code        :text(len=8)
  features.#.properties.detail      :text(len=74)
  features.#.properties.dmin        :null | number(minval=0.1081, maxval=0.537)
  features.#.properties.felt        :null | number(val=48)
  features.#.properties.gap         :null | number(minval=17, maxval=90.63)
  features.#.properties.ids         :text(len=12)
  features.#.properties.mag         :number(minval=1.29, maxval=5.1)
  features.#.properties.magType     :text(minlen=2, maxlen=3)
  features.#.properties.mmi         :null
  features.#.properties.net         :text(len=2)
  features.#.properties.nst         :null | number(minval=21, maxval=32)
  features.#.properties.place       :text(minlen=19, maxlen=31)
  features.#.properties.rms         :number(minval=0.13, maxval=1.39) | null
  features.#.properties.sig         :number(minval=26, maxval=420)
  features.#.properties.sources     :text(len=4)
  features.#.properties.status      :text(minlen=8, maxlen=9)
  features.#.properties.time        :number(minval=1486083146340, maxval=1486086087592)
  features.#.properties.title       :text(minlen=27, maxlen=39)
  features.#.properties.tsunami     :number(val=0)
  features.#.properties.type        :text(len=10)
  features.#.properties.types       :text(minlen=17, maxlen=55)
  features.#.properties.tz          :number(minval=-540, maxval=-180)
  features.#.properties.updated     :number(minval=1486085163717, maxval=1486086668516)
  features.#.properties.url         :text(len=59)
  features.#.type                   :text(len=7)
  metadata                          :object(keys=6)
  metadata.api                      :text(len=5)
  metadata.count                    :number(val=5)
  metadata.generated                :number(val=1486086732000)
  metadata.status                   :number(val=200)
  metadata.title                    :text(len=31)
  metadata.url                      :text(len=73)
  type                              :text(len=17)