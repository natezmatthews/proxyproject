#!/bin/bash
rm -R /System/Library/Frameworks/Python.framework/Versions/3.3
mv /Library/Frameworks/Python.framework/Versions/3.3 /System/Library/Frameworks/Python.framework/Versions
chown -R root:wheel /System/Library/Frameworks/Python.framework/Versions/3.3
 
rm /System/Library/Frameworks/Python.framework/Versions/Current
ln -s /System/Library/Frameworks/Python.framework/Versions/3.3 /System/Library/Frameworks/Python.framework/Versions/Current
 
rm /usr/bin/pydoc
rm /usr/bin/python
rm /usr/bin/pythonw
rm /usr/bin/python-config
 
rm /System/Library/Frameworks/Python.framework/Versions/3.3/bin/pydoc
rm /System/Library/Frameworks/Python.framework/Versions/3.3/bin/python
rm /System/Library/Frameworks/Python.framework/Versions/3.3/bin/pythonw
rm /System/Library/Frameworks/Python.framework/Versions/3.3/bin/python-config
 
ln -s /System/Library/Frameworks/Python.framework/Versions/3.3/bin/pydoc3 /usr/bin/pydoc
ln -s /System/Library/Frameworks/Python.framework/Versions/3.3/bin/python3 /usr/bin/python
ln -s /System/Library/Frameworks/Python.framework/Versions/3.3/bin/pythonw3 /usr/bin/pythonw
ln -s /System/Library/Frameworks/Python.framework/Versions/3.3/bin/python3-config /usr/bin/python-config
