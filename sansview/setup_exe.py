#!/usr/bin/env python

#
# The setup to create a Windows executable.
# Inno Setup can then be used with the installer.iss file 
# in the top source directory to create an installer. 
#
# Setuptools clashes with py2exe 0.6.8 (and probably later too).
# For that reason, most of the code needs to have direct imports
# that are not going through pkg_resources. 
#
# Attention should be paid to dynamic imports. Data files can
# be added to the distribution directory for that purpose.
# See for example the 'images' directory below.

import os, sys
import platform

if len(sys.argv) == 1:
    sys.argv.append('py2exe')
# When using the SansView build script, we need to be able to pass
# an extra path to be added to the python path. The extra arguments
# should be removed from the list so that the setup processing doesn't
# fail.
try:
    if sys.argv.count('--extrapath'):
        path_flag_idx = sys.argv.index('--extrapath')
        extra_path = sys.argv[path_flag_idx+1]
        sys.path.insert(0, extra_path)
        del sys.argv[path_flag_idx+1]
        sys.argv.remove('--extrapath')
except:
    print "Error processing extra python path needed to build SansView\n  %s" % sys.exc_value

from distutils.core import setup
from distutils.filelist import findall
import matplotlib
import py2exe
import shutil
# Remove the build folder
shutil.rmtree("build", ignore_errors=True)
# do the same for dist folder
shutil.rmtree("dist", ignore_errors=True)

if sys.version_info < (2, 6):
    is_64bits = False 
    origIsSystemDLL = py2exe.build_exe.isSystemDLL
    def isSystemDLL(pathname):
            if os.path.basename(pathname).lower() in ("msvcp71.dll", "comctl32.dll"):
                    return 0
            return origIsSystemDLL(pathname)
    py2exe.build_exe.isSystemDLL = isSystemDLL
else:
    is_64bits = sys.maxsize > 2**32

if is_64bits and sys.version_info >= (2, 6):
    manifest = """
       <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
       <assembly xmlns="urn:schemas-microsoft-com:asm.v1"
       manifestVersion="1.0">
       <assemblyIdentity
           version="0.64.1.0"
           processorArchitecture="amd64"
           name="Controls"
           type="win32"
       />
       <description>SansView</description>
       <dependency>
           <dependentAssembly>
               <assemblyIdentity
                   type="win32"
                   name="Microsoft.Windows.Common-Controls"
                   version="6.0.0.0"
                   processorArchitecture="amd64"
                   publicKeyToken="6595b64144ccf1df"
                   language="*"
               />
           </dependentAssembly>
       </dependency>
       </assembly>
      """
else:
    manifest_for_python26 = """
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
          <assemblyIdentity
            version="5.0.0.0"
            processorArchitecture="x86"
            name="SansView"
            type="win32">
          </assemblyIdentity>
          <description>SansView</description>
          <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
            <security>
              <requestedPrivileges>
                <requestedExecutionLevel
                  level="asInvoker"
                  uiAccess="false">
                </requestedExecutionLevel>
              </requestedPrivileges>
            </security>
          </trustInfo>
          <dependency>
            <dependentAssembly>
              <assemblyIdentity
                type="win32"
                name="Microsoft.VC90.CRT"
                version="9.0.21022.8"
                processorArchitecture="x86"
                publicKeyToken="1fc8b3b9a1e18e3b">
              </assemblyIdentity>
            </dependentAssembly>
          </dependency>
          <dependency>
            <dependentAssembly>
              <assemblyIdentity
                type="win32"
                name="Microsoft.Windows.Common-Controls"
                version="6.0.0.0"
                processorArchitecture="x86"
                publicKeyToken="6595b64144ccf1df"
                language="*">
              </assemblyIdentity>
            </dependentAssembly>
          </dependency>
        </assembly>
        """
    manifest_for_python25 = """
       <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
       <assembly xmlns="urn:schemas-microsoft-com:asm.v1"
       manifestVersion="1.0">
       <assemblyIdentity
           version="0.64.1.0"
           processorArchitecture="x86"
           name="Controls"
           type="win32"
       />
       <description>SansView</description>
       <dependency>
           <dependentAssembly>
               <assemblyIdentity
                   type="win32"
                   name="Microsoft.Windows.Common-Controls"
                   version="6.0.0.0"
                   processorArchitecture="X86"
                   publicKeyToken="6595b64144ccf1df"
                   language="*"
               />
           </dependentAssembly>
       </dependency>
       </assembly>
      """

# Select the appropriate manifest to use.
py26MSdll_x86 = None
if sys.version_info >= (3, 0) or sys.version_info < (2, 5):
    print "*** This script only works with Python 2.5, 2.6, or 2.7."
    sys.exit()
elif sys.version_info >= (2, 6):
    manifest = manifest_for_python26
    from glob import glob
    py26MSdll = glob(r"C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*")
    try:
        py26MSdll_x86 = glob(r"C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*")
    except:
        pass
elif sys.version_info >= (2, 5):
    manifest = manifest_for_python25
    py26MSdll = None
    
class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "2.1.0"
        self.company_name = "U Tennessee"
        self.copyright = "copyright 2009 - 2012"
        self.name = "SansView"
        
#
# Adapted from http://www.py2exe.org/index.cgi/MatPlotLib
# to use the MatPlotLib.
#
path = os.getcwd()

media_dir = os.path.join(path, "media")
images_dir = os.path.join(path, "images")
test_dir = os.path.join(path, "test")

matplotlibdatadir = matplotlib.get_data_path()
matplotlibdata = findall(matplotlibdatadir)
data_files = []
# Copying SLD data
import periodictable
import logging
data_files += periodictable.data_files()

import sans.perspectives.fitting as fitting
data_files += fitting.data_files()

import sans.perspectives.calculator as calculator
data_files += calculator.data_files()

import sans.perspectives.invariant as invariant
data_files += invariant.data_files()

import sans.guiframe as guiframe
data_files += guiframe.data_files()

import sans.models as models
data_files += models.data_files()

for f in matplotlibdata:
    dirname = os.path.join('mpl-data', f[len(matplotlibdatadir)+1:])
    data_files.append((os.path.split(dirname)[0], [f]))

# Copy the settings file for the sans.dataloader file extension associations
import sans.dataloader.readers
f = os.path.join(sans.dataloader.readers.get_data_path(),'defaults.xml')
if os.path.isfile(f):
    data_files.append(('.', [f]))
f = 'custom_config.py'
if os.path.isfile(f):
    data_files.append(('.', [f]))
    data_files.append(('config', [f]))
f = 'local_config.py'
if os.path.isfile(f):
    data_files.append(('.', [f]))
    
if os.path.isfile("BUILD_NUMBER"):
    data_files.append(('.',["BUILD_NUMBER"]))

# Copying the images directory to the distribution directory.
for f in findall(images_dir):
    if os.path.split(f)[0].count('.svn')==0:
        data_files.append(("images", [f]))

# Copying the HTML help docs
for f in findall(media_dir):
    if os.path.split(f)[0].count('.svn')==0:
        data_files.append(("media", [f]))

# Copying the sample data user data
for f in findall(test_dir):
    if os.path.split(f)[0].count('.svn')==0:
        data_files.append(("test", [f]))
        
if py26MSdll != None:
    # install the MSVC 9 runtime dll's into the application folder
    data_files.append(("Microsoft.VC90.CRT", py26MSdll))
if py26MSdll_x86 != None:
    # install the MSVC 9 runtime dll's into the application folder
    data_files.append(("Microsoft.VC90.CRT", py26MSdll_x86))


# packages
#
packages = ['matplotlib', 'scipy', 'pytz', 'encodings', 'comtypes']
includes = ['site']

# Exclude packages that are not needed but are often found on build systems
excludes = ['Tkinter', 'PyQt4', '_ssl', '_tkagg', 'sip']

dll_excludes = ['libgdk_pixbuf-2.0-0.dll',
                'libgobject-2.0-0.dll',
                'libgdk-win32-2.0-0.dll',
                'tcl84.dll',
                'tk84.dll',
                'QtGui4.dll',
                'QtCore4.dll',
                'msvcp90.dll',
                'w9xpopen.exe',
                'cygwin1.dll']

target_wx_client = Target(
    description = 'SansView',
    script = 'sansview.py',
    icon_resources = [(1, os.path.join(images_dir, "ball.ico"))],
    other_resources = [(24,1,manifest)],
    dest_base = "SansView"
    )

bundle_option = 2
if is_64bits:
    bundle_option = 3

setup(
    windows=[target_wx_client],
    console=[],
    
    options={
        'py2exe': {
            'dll_excludes': dll_excludes,
            'packages' : packages,
            'includes':includes,
            'excludes':excludes,
            "compressed": 1,
            "optimize": 0,
            "bundle_files":bundle_option,
            },
    },
    data_files=data_files,
    
)


