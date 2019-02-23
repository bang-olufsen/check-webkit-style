# Copyright (C) 2010 Chris Jerdonek (cjerdonek@webkit.org)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1.  Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# 2.  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY APPLE INC. AND ITS CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL APPLE INC. OR ITS CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# This module is required for Python to treat this directory as a package.

"""Autoinstalls third-party code required by WebKit."""


import codecs
import json
import os
import re
import sys
import urllib2

from collections import namedtuple
from distutils import spawn
from webkitpy.common.system.autoinstall import AutoInstaller
from webkitpy.common.system.filesystem import FileSystem

_THIRDPARTY_DIR = os.path.dirname(__file__)
_AUTOINSTALLED_DIR = os.path.join(_THIRDPARTY_DIR, "autoinstalled")

CHROME_DRIVER_URL = "http://chromedriver.storage.googleapis.com/"
FIREFOX_RELEASES_URL = "https://api.github.com/repos/mozilla/geckodriver/releases"

# Putting the autoinstall code into webkitpy/thirdparty/__init__.py
# ensures that no autoinstalling occurs until a caller imports from
# webkitpy.thirdparty.  This is useful if the caller wants to configure
# logging prior to executing autoinstall code.

# FIXME: If any of these servers is offline, webkit-patch breaks (and maybe
# other scripts do, too). See <http://webkit.org/b/42080>.

# We put auto-installed third-party modules in this directory--
#
#     webkitpy/thirdparty/autoinstalled

fs = FileSystem()
fs.maybe_make_directory(_AUTOINSTALLED_DIR)

init_path = fs.join(_AUTOINSTALLED_DIR, "__init__.py")
if not fs.exists(init_path):
    fs.write_text_file(init_path, "")

readme_path = fs.join(_AUTOINSTALLED_DIR, "README")
if not fs.exists(readme_path):
    fs.write_text_file(readme_path,
        "This directory is auto-generated by WebKit and is "
        "safe to delete.\nIt contains needed third-party Python "
        "packages automatically downloaded from the web.")


class AutoinstallImportHook(object):
    def __init__(self, filesystem=None):
        self._fs = filesystem or FileSystem()

    def _ensure_autoinstalled_dir_is_in_sys_path(self):
        # Some packages require that the are being put somewhere under a directory in sys.path.
        if not _AUTOINSTALLED_DIR in sys.path:
            sys.path.insert(0, _AUTOINSTALLED_DIR)

    def find_module(self, fullname, _):
        # This method will run before each import. See http://www.python.org/dev/peps/pep-0302/
        if '.autoinstalled' not in fullname:
            return

        # Note: all of the methods must follow the "_install_XXX" convention in
        # order for autoinstall_everything(), below, to work properly.
        if '.mechanize' in fullname:
            self._install_mechanize()
        elif '.pep8' in fullname:
            self._install_pep8()
        elif '.pylint' in fullname:
            self._install_pylint()
        elif '.coverage' in fullname:
            self._install_coverage()
        elif '.buildbot' in fullname:
            self._install_buildbot()
        elif '.keyring' in fullname:
            self._install_keyring()
        elif '.twisted_15_5_0' in fullname:
            self._install_twisted_15_5_0()
        elif '.selenium' in fullname:
            self._install_selenium()
        elif '.chromedriver' in fullname:
            self.install_chromedriver()
        elif '.geckodriver' in fullname:
            self.install_geckodriver()
        elif '.mozlog' in fullname:
            self._install_mozlog()
        elif '.mozprocess' in fullname:
            self._install_mozprocess()
        elif '.pytest_timeout' in fullname:
            self._install_pytest_timeout()
        elif '.pytest' in fullname:
            self._install_pytest()

    def _install_mechanize(self):
        self._install("https://files.pythonhosted.org/packages/source/m/mechanize/mechanize-0.2.5.tar.gz",
                             "mechanize-0.2.5/mechanize")

    def _install_keyring(self):
        self._install("https://files.pythonhosted.org/packages/7d/a9/8c6bf60710781ce13a9987c0debda8adab35eb79c6b5525f7fe5240b7a8a/keyring-7.3.1.tar.gz",
                             "keyring-7.3.1/keyring")

    def _install_pep8(self):
        self._install("https://files.pythonhosted.org/packages/source/p/pep8/pep8-0.5.0.tar.gz",
                             "pep8-0.5.0/pep8.py")

    def _install_mozlog(self):
        self._ensure_autoinstalled_dir_is_in_sys_path()
        self._install("https://files.pythonhosted.org/packages/10/d5/d286b5dc3f40e32d2a9b3cab0b5b20a05d704958b44b4c5a9aed6472deab/mozlog-3.5.tar.gz",
                              "mozlog-3.5/mozlog")

    def _install_mozprocess(self):
        self._ensure_autoinstalled_dir_is_in_sys_path()
        self._install("https://files.pythonhosted.org/packages/cb/26/144dbc28d1f40e392f8a0cbee771ba624a61017f016c77ad88424d84b230/mozprocess-0.25.tar.gz",
                              "mozprocess-0.25/mozprocess")

    def _install_pytest_timeout(self):
        self._install("https://files.pythonhosted.org/packages/cc/b7/b2a61365ea6b6d2e8881360ae7ed8dad0327ad2df89f2f0be4a02304deb2/pytest-timeout-1.2.0.tar.gz",
                              "pytest-timeout-1.2.0/pytest_timeout.py")

    def _install_pytest(self):
        self._install("https://files.pythonhosted.org/packages/90/e3/e075127d39d35f09a500ebb4a90afd10f9ef0a1d28a6d09abeec0e444fdd/py-1.5.2.tar.gz",
                              "py-1.5.2/py")
        self._install("https://files.pythonhosted.org/packages/11/bf/cbeb8cdfaffa9f2ea154a30ae31a9d04a1209312e2919138b4171a1f8199/pluggy-0.6.0.tar.gz",
                              "pluggy-0.6.0/pluggy")
        self._install("https://files.pythonhosted.org/packages/c0/2f/6773347277d76c5ade4414a6c3f785ef27e7f5c4b0870ec7e888e66a8d83/more-itertools-4.2.0.tar.gz",
                              "more-itertools-4.2.0/more_itertools")
        self._install("https://files.pythonhosted.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz",
                              "six-1.11.0/six.py")
        self._install("https://files.pythonhosted.org/packages/a1/e1/2d9bc76838e6e6667fde5814aa25d7feb93d6fa471bf6816daac2596e8b2/atomicwrites-1.1.5.tar.gz",
                              "atomicwrites-1.1.5/atomicwrites")
        self._install("https://files.pythonhosted.org/packages/94/4a/db842e7a0545de1cdb0439bb80e6e42dfe82aaeaadd4072f2263a4fbed23/funcsigs-1.0.2.tar.gz",
                              "funcsigs-1.0.2/funcsigs")
        self._install("https://files.pythonhosted.org/packages/e4/ac/a04671e118b57bee87dabca1e0f2d3bda816b7a551036012d0ca24190e71/attrs-18.1.0.tar.gz",
                              "attrs-18.1.0/src/attr")
        self._install("https://files.pythonhosted.org/packages/a2/ec/415d0cccc1ed41cd7fdf69ad989da16a8d13057996371004cab4bafc48f3/pytest-3.6.2.tar.gz",
                              "pytest-3.6.2/src/_pytest")

    def _install_pylint(self):
        self._ensure_autoinstalled_dir_is_in_sys_path()
        if (not self._fs.exists(self._fs.join(_AUTOINSTALLED_DIR, "pylint")) or
            not self._fs.exists(self._fs.join(_AUTOINSTALLED_DIR, "logilab/astng")) or
            not self._fs.exists(self._fs.join(_AUTOINSTALLED_DIR, "logilab/common"))):
            installer = AutoInstaller(target_dir=_AUTOINSTALLED_DIR)
            files_to_remove = []
            if sys.platform == 'win32':
                files_to_remove = ['test/data/write_protected_file.txt']
            installer.install("https://files.pythonhosted.org/packages/source/l/logilab-common/logilab-common-0.58.1.tar.gz", url_subpath="logilab-common-0.58.1", target_name="logilab/common", files_to_remove=files_to_remove)
            installer.install("https://files.pythonhosted.org/packages/source/l/logilab-astng/logilab-astng-0.24.1.tar.gz", url_subpath="logilab-astng-0.24.1", target_name="logilab/astng")
            installer.install('https://files.pythonhosted.org/packages/source/p/pylint/pylint-0.25.2.tar.gz', url_subpath="pylint-0.25.2", target_name="pylint")

    # autoinstalled.buildbot is used by BuildSlaveSupport/build.webkit.org-config/mastercfg_unittest.py
    # and should ideally match the version of BuildBot used at build.webkit.org.
    def _install_buildbot(self):
        # The buildbot package uses jinja2, for example, in buildbot/status/web/base.py.
        # buildbot imports jinja2 directly (as though it were installed on the system),
        # so the search path needs to include jinja2.  We put jinja2 in
        # its own directory so that we can include it in the search path
        # without including other modules as a side effect.
        jinja_dir = self._fs.join(_AUTOINSTALLED_DIR, "jinja2")
        installer = AutoInstaller(append_to_search_path=True, target_dir=jinja_dir)
        installer.install(url="https://files.pythonhosted.org/packages/source/J/Jinja2/Jinja2-2.6.tar.gz",
                                                url_subpath="Jinja2-2.6/jinja2")

        SQLAlchemy_dir = self._fs.join(_AUTOINSTALLED_DIR, "sqlalchemy")
        installer = AutoInstaller(append_to_search_path=True, target_dir=SQLAlchemy_dir)
        installer.install(url="https://files.pythonhosted.org/packages/source/S/SQLAlchemy/SQLAlchemy-0.7.7.tar.gz",
                                                 url_subpath="SQLAlchemy-0.7.7/lib/sqlalchemy")

        twisted_dir = self._fs.join(_AUTOINSTALLED_DIR, "twisted")
        installer = AutoInstaller(prepend_to_search_path=True, target_dir=twisted_dir)
        installer.install(url="https://files.pythonhosted.org/packages/source/T/Twisted/Twisted-12.1.0.tar.bz2", url_subpath="Twisted-12.1.0/twisted")

        self._install("https://files.pythonhosted.org/packages/source/b/buildbot/buildbot-0.8.6p1.tar.gz", "buildbot-0.8.6p1/buildbot")

    def _install_coverage(self):
        self._ensure_autoinstalled_dir_is_in_sys_path()
        self._install(url="https://files.pythonhosted.org/packages/source/c/coverage/coverage-3.5.1.tar.gz", url_subpath="coverage-3.5.1/coverage")

    def _install_twisted_15_5_0(self):
        twisted_dir = self._fs.join(_AUTOINSTALLED_DIR, "twisted_15_5_0")
        installer = AutoInstaller(prepend_to_search_path=True, target_dir=twisted_dir)
        installer.install(url="https://files.pythonhosted.org/packages/source/T/Twisted/Twisted-15.5.0.tar.bz2", url_subpath="Twisted-15.5.0/twisted")
        installer.install(url="https://files.pythonhosted.org/packages/source/z/zope.interface/zope.interface-4.1.3.tar.gz", url_subpath="zope.interface-4.1.3/src/zope")

    @staticmethod
    def greater_than_equal_to_version(minimum, version):
        for i in xrange(len(minimum.split('.'))):
            if int(version.split('.')[i]) > int(minimum.split('.')[i]):
                return True
            if int(version.split('.')[i]) < int(minimum.split('.')[i]):
                return False
        return True

    def _install_selenium(self):
        self._ensure_autoinstalled_dir_is_in_sys_path()

        installer = AutoInstaller(prepend_to_search_path=True, target_dir=self._fs.join(_AUTOINSTALLED_DIR, "urllib3"))
        installer.install(url="https://files.pythonhosted.org/packages/b1/53/37d82ab391393565f2f831b8eedbffd57db5a718216f82f1a8b4d381a1c1/urllib3-1.24.1.tar.gz", url_subpath="urllib3-1.24.1")

        minimum_version = '3.5.0'
        if os.path.isfile(os.path.join(_AUTOINSTALLED_DIR, 'selenium', '__init__.py')):
            import selenium.webdriver
            if AutoinstallImportHook.greater_than_equal_to_version(minimum_version, selenium.webdriver.__version__):
                return

        try:
            url, url_subpath = self.get_latest_pypi_url('selenium')
        except urllib2.URLError:
            # URL for installing the minimum required version.
            url = 'https://files.pythonhosted.org/packages/ac/d7/1928416439d066c60f26c87a8d1b78a8edd64c7d05a0aa917fa97a8ee02d/selenium-3.5.0.tar.gz'
            url_subpath = 'selenium-{}/selenium'.format(minimum_version)
            sys.stderr.write('\nFailed to find latest selenium, falling back to minimum {} version\n'.format(minimum_version))
        self._install(url=url, url_subpath=url_subpath)

    def install_chromedriver(self):
        filename_postfix = get_driver_filename().chrome
        if filename_postfix != "unsupported":
            version = urllib2.urlopen(CHROME_DRIVER_URL + 'LATEST_RELEASE').read().strip()
            full_chrome_url = "{base_url}{version}/chromedriver_{os}.zip".format(base_url=CHROME_DRIVER_URL, version=version, os=filename_postfix)
            self.install_binary(full_chrome_url, 'chromedriver')

    def install_geckodriver(self):
        filename_postfix = get_driver_filename().firefox
        if filename_postfix != "unsupported":
            firefox_releases_blob = urllib2.urlopen(FIREFOX_RELEASES_URL)
            firefox_releases_line_separated = json.dumps(json.load(firefox_releases_blob), indent=0).strip()
            all_firefox_release_urls = "\n".join(re.findall(r'.*browser_download_url.*', firefox_releases_line_separated))
            full_firefox_url = re.findall(r'.*%s.*' % filename_postfix, all_firefox_release_urls)[0].split('"')[3]
            self.install_binary(full_firefox_url, 'geckodriver')

    def _install(self, url, url_subpath=None, target_name=None):
        installer = AutoInstaller(target_dir=_AUTOINSTALLED_DIR)
        installer.install(url=url, url_subpath=url_subpath, target_name=target_name)

    def get_latest_pypi_url(self, package_name, url_subpath_format='{name}-{version}/{lname}'):
        json_url = "https://pypi.org/pypi/%s/json" % package_name
        response = urllib2.urlopen(json_url, timeout=30)
        data = json.load(response)
        url = data['urls'][1]['url']
        subpath = url_subpath_format.format(name=package_name, version=data['info']['version'], lname=package_name.lower())
        return (url, subpath)

    def install_binary(self, url, name):
        self._install(url=url, target_name=name)
        directory = os.path.join(_AUTOINSTALLED_DIR, name)
        os.chmod(os.path.join(directory, name), 0755)
        open(os.path.join(directory, '__init__.py'), 'w+').close()


_hook = AutoinstallImportHook()
sys.meta_path.append(_hook)


def autoinstall_everything():
    install_methods = [method for method in dir(_hook.__class__) if method.startswith('_install_')]
    for method in install_methods:
        getattr(_hook, method)()

def get_driver_filename():
    os_name, os_type = get_os_info()
    chrome_os, filefox_os = 'unsupported', 'unsupported'
    if os_name == 'Linux' and os_type == '64':
        chrome_os, firefox_os = 'linux64', 'linux64'
    elif os_name == 'Linux':
        chrome_os, firefox_os = 'linux32', 'linux32'
    elif os_name == 'Darwin':
        chrome_os, firefox_os = 'mac64', 'macos'
    DriverFilenameForBrowser = namedtuple('DriverFilenameForBrowser', ['chrome', 'firefox'])
    return DriverFilenameForBrowser(chrome_os, firefox_os)

def get_os_info():
    import platform
    os_name = platform.system()
    os_type = platform.machine()[-2:]
    return (os_name, os_type)