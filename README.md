SmaliReverse
============

SmaliReverse is a simple Sublime Text plugin to help when reversing
Android APKs. It's especially useful on APKs that have ProGuard run
on them because you can easily CTRL-Click on a method and Sublime
will jump to it without you having to hunt through hundreds of
classes with no names. The plugin expects that you have run
apktool on your apk and have opened the whole output folder in
Sublime.

In addition to the CTRL-Click functionality you can also do
CTRL+Option+Command+Left arrow to go back to where you came
from or CTRL+Option+Command+Right to go to the method definition

Finally you can do CTRL+Option+Command+Enter and Sublime will
prompt you to enter a comment. A new smali comment will be
entered on that line. This functionality tries to mimick how
comments in IDA Pro works.
