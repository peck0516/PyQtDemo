'''
Created on 2020年2月17日

@author: DELL
'''
from distutils.core import setup
import py2exe

setup(
console=[{"script": "main.py", "icon_resources": [(1, "icon.icon")] }]
) 