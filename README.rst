cnx-easybake
============

Easybake is a library (and cli tool) for using an extended subset of CSS3 to describe and 'bake-in'
some manipulations of HTML files, in particular collation (moving content around) and numbering.

INSTALL
-------

To install ``cnx-easybake``::

    ./scripts/setup


Primarily for use as a library to process etree HTML trees.
Example::

    from lxml import etree
    from cnxeasybake import Oven

    oven = Oven(myRuleSet)  # an CSS3 based ruleset - see docs

    myHTML = etree.HTML(myHTMLstring)
    oven.bake(myHTML)


Example usage::

    cnx-easybake poc.css poc-raw.html poc-baked.html


TEST
----

Test files are available on in the `tests` folder.

To run the tests::

    ./scripts/test
