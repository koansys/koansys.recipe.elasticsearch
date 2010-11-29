A brief documentation
=====================

This recipe takes a number of options:

url
    The URL to download the jar.


Tests
=====

We will define a buildout template used by the recipe:

    >>> buildout_cfg = """
    ... [buildout]
    ... parts = elasticsearch
    ...
    ... [elasticsearch]
    ... recipe = koansys.recipe.elasticsearch
    ... url = http://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.13.0.tar.gz
    ... """

We'll start by creating a buildout:

    >>> import os.path
    >>> write('buildout.cfg', buildout_cfg)

Running the buildout gives us:

    >>> output = system(buildout)
    >>> 'koansys.recipe.elasticsearch: downloading elasticsearch distribution...' in output
    True

Check whether the binaries are copied:

    >>> set(os.listdir('bin')).issuperset(['elasticsearch'])
    True

A start script with the format 'start_PART-NAME_mongod.sh' should be generated.

    >>> 'start_elasticsearch.sh' in os.listdir('bin')
    True

It is possible to change the name of this start script with the 'script_name'
option. Furthermore all options of mongod (version v1.6.0) are supported via
buildout options. A more comprehensive recipe could be for example:

    >>> buildout_cfg = """
    ... [buildout]
    ... parts = elasticsearch.sh
    ... [elasticsearch]
    ... recipe = koansys.recipe.elasticsearch
    ... url = http://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.13.0.tar.gz
    ... script_name = start_es.sh
    ... quiet=true
    ... fork=true
    ... logpath=${buildout:parts-directory}/elasticsearch/log
    ... dbpath=${buildout:parts-directory}/elasticsearch/data
    ... """
