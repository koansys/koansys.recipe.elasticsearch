"""Recipe for setting up Elasticsearch."""

import errno
import logging
import os
import re
import shutil
import stat
import subprocess
import tempfile
import urllib
import zc.recipe.egg

logger = logging.getLogger(__name__)

ELASTICSEARCH_BINARIES = (
    'elasticsearch',
    )

JAVA_VERSION="1\.[6-7]\.[0-9]+"

# value awaits abitrary string
# flag test only for 'true'/'false defined in the buildout config
#  and sets only this paramt without any value

#dir is a special kind of value tag where a os.makedirs is done
#file is a special kind fo vlaue tag where a os.makedirs on basebath is done
ELASTICSEARCH_OPTIONS = {
    'f' : 'flag',
    #'Dnetwork.host' : 'value',
    #'Des.config' : 'file',
    'Des.logs' : 'dir',
    'Des.data' : 'dir',
}

class Recipe(zc.recipe.egg.Eggs):
    """Buildout recipe for installing elasticsearch."""

    def __init__(self, buildout, name, opts):
        """Standard constructor for zc.buildout recipes."""

        self.options = opts
        self.buildout = buildout
        self.name = name

    def install_elasticsearch(self):
        """Downloads and installs elasticsearch."""

        installed = []
        p = subprocess.Popen("java -version",
                             shell=True,
                             stderr=subprocess.PIPE)
        version_line=p.stderr.readline()
        logger.info("found: {0}".format(version_line))
        assert re.search("1\.[6-7]\.[0-9]+", version_line), \
               "Java 1.6 or higher ust be installed"
        filename = self.options['url'].split(os.sep)[-1]
        dst = os.path.join(self.buildout['buildout']['parts-directory'],
                           self.name)
        downloads_dir = os.path.join(os.getcwd(), 'downloads')
        if not os.path.isdir(downloads_dir):
            os.mkdir(downloads_dir)
        src = os.path.join(downloads_dir, filename)
        if not os.path.isfile(src):
            logger.info("downloading elasticsearch distribution...")
            urllib.urlretrieve(self.options['url'], src)
        else:
            logger.info("{0} already downloaded.".format(filename))
        extract_dir = tempfile.mkdtemp("buildout-" + self.name)
        remove_after_install = [extract_dir]
        is_ext = filename.endswith
        is_archive = True
        if is_ext('.tar.gz') or is_ext('.tgz'):
            call = ['tar', 'xzf', src, '-C', extract_dir]
        elif is_ext('.tar.bz2') or is_ext('.tbz2'):
            call = ['tar', 'xjf', src, '-C', extract_dir]
        elif is_ext('.zip'):
            call = ['unzip', src, '-d', extract_dir]
        else:
            is_archive = False

        if is_archive:
            retcode = subprocess.call(call)
            if retcode != 0:
                raise Exception("extraction of file %r failed (tempdir: %r)" %
                                (filename, extract_dir))
        else:
            shutil.copy(filename, extract_dir)

        if is_archive:
            top_level_contents = os.listdir(extract_dir)
            if len(top_level_contents) != 1:
                raise ValueError("can't strip top level directory because "
                                 "there is more than one element in the "
                                 "archive.")
            base = os.path.join(extract_dir, top_level_contents[0])
        else:
            base = extract_dir

        if not os.path.isdir(dst):
            os.mkdir(dst)

            for filename in os.listdir(base):
                shutil.move(os.path.join(base, filename),
                            os.path.join(dst, filename))
        else:
            logger.info("elasticsearch already installed.")

        bindir = self.buildout['buildout']['bin-directory']
        for fn in ELASTICSEARCH_BINARIES:
            fullname = os.path.join(dst, 'bin', fn)
            if os.path.exists(fullname):
                destfile = os.path.join(bindir, fn)
                if os.path.exists(destfile):
                    os.unlink(destfile)
                installed.append(destfile)
                os.symlink(fullname, destfile)

        for path in remove_after_install:
            shutil.rmtree(path)

        installed.append(dst)
        self._build_start_script(installed)
        return installed

    def _build_start_script(self, installed):
        bin_dir = self.buildout['buildout']['bin-directory']
        command_line = []

        command_line.append(os.path.join(bin_dir, 'mongod'))

        for option_name, option_type in ELASTICSEARCH_OPTIONS.iteritems():
            if option_name not in self.options:
                continue
            else:
                option_value = self.options[option_name]

            if option_type in ('value', 'file', 'dir'):
                option = "-%s %s" % (option_name, option_value)
                command_line.append(option)

            elif option_type == 'flag' and option_value == 'true':
                option = "-%s" % option_name
                command_line.append(option)

            if option_type == 'file':
                self._create_directory(
                    option_name, os.path.dirname(option_value))
            elif option_type == 'dir':
                self._create_directory(option_name, option_value)

        if 'script_name' in self.options:
            script_name = self.options['script_name']
        else:
            script_name = 'start_%s_elascticsearch.sh' % self.name
        full_script_path = os.path.join(bin_dir, script_name)

        installed.append(full_script_path)
        script = open(full_script_path, 'w')
        print >> script, "#!/bin/bash"
        print >> script, ' '.join(command_line)
        script.close()
        os.chmod(full_script_path, stat.S_IRWXU)

    def _create_directory(self, option_name, directory_name):
        try:
            os.makedirs(directory_name)
        except OSError, error:
            if error.errno == errno.EEXIST:
                warn_string = "Directory (%s) for Option (%s) already exists"
                logger.warn(warn_string % (directory_name, option_name))

    def install(self):
        """Creates the part."""

        return self.install_elasticsearch()

    def update(self):
        """Updates the part."""

        bindir = self.buildout['buildout']['bin-directory']
        for fn in ELASTICSEARCH_BINARIES:
            fullname = os.path.join(bindir, fn)
            if os.path.isfile(fullname):
                os.remove(fullname)
        dst = os.path.join(self.buildout['buildout']['parts-directory'],
                           self.name)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        return self.install_mongodb()
