# -*- coding: utf-8 -*-
"""
Created on Mon 02 of Feb 10:42:17 2015

Build script zum erstellen einer lauff�higen .exe

@author: mayers
"""

from cx_Freeze import setup, Executable
import matplotlib
import site
import sys
import gettext

site_packages_dir=site.getsitepackages()

if sys.platform == "win32":
    base = "Win32GUI"
    scipy_ufuncs=site_packages_dir[-1]+'\\scipy\\special\\_ufuncs.pyd'
    
#includefiles = ["CoolPropLogo.ico","msvcp100.dll","msvcr100.dll"]
includefiles = ["CoolPropLogo.ico"]
excludefiles = []

includes = []

build_exe_options = { 'packages': ['scipy'],
                     "includes":["matplotlib.backends.backend_tkagg"],
                     "include_files": [(scipy_ufuncs,
                                        '_ufuncs.pyd'),
                                        "CoolPropLogo.ico",
                                        "simplecycle.png",
                                        (matplotlib.get_data_path(),
                                        "mpl-data")]
                     }

cpgui = Executable(
    script = "cpgui.py",
    initScript = None,
    base = base,
    targetName = "CPGUI.exe",
    compress = True,
    copyDependentFiles = True,
    appendScriptToExe = False,
    appendScriptToLibrary = False,
    icon = "CoolPropLogo.ico"
    )

setup(
        name = "CoolProp GUI",
        version = "0.1",
        author = 'Reiner Mayers',
        description = "GUI for Coolprop",
        options={"build_exe": build_exe_options},
        #options = {"build_exe": {"includes":includes,'include_files':includefiles}},
        executables = [cpgui]
        )
