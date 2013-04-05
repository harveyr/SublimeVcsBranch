Sublime Text VCS Branch Plugin
==============

- - -
**NOTE: I believe this plugin is a cpu hog at the moment. I'll be debugging performance issues shortly.**
- - -

Sublime Text plugin that displays a few repo stats in the status bar.

**Requires Sublime Text 3**, as it uses some of the new asynchronous functionality.

Only git and mercurial are supported at this time (since they're all I use).

Currently, the plugin displays:
* branch name
* modified file count
* incoming changeset count (for the current branch)
* outgoing changeset count (for the current branch)

![Example](http://i1217.photobucket.com/albums/dd393/gfizeek/vcs-branch.jpg "Image Example")

There is no config (yet). The plugin will figure out which VCS you're in.

It's still in its quick-and-dirty stage. Suggestions are very welcome!
