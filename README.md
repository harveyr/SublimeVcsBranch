Sublime Text VCS Branch Plugin
==============

*Note*: I made this primarily to tide me over until the full-fledged Git plugin started working with ST3. It appears to be now, so I may not give this much attention. Though I'll probably continue to use it on my Mercurial projects.

---

Sublime Text plugin that displays a few repo stats in the status bar.

**Requires Sublime Text 3**, as it uses the new asynchronous API.

Only Git and Mercurial are supported at this time (since they're all I use).

Currently, the plugin displays:

* branch name
* modified file count
* incoming changeset count (for the current branch)
* outgoing changeset count (for the current branch)

![Example](http://i1217.photobucket.com/albums/dd393/gfizeek/vcs-branch.jpg "Image Example")

There is no config (yet). The plugin will figure out which VCS you're in.

It's still in its quick-and-dirty stage. Suggestions are very welcome!
