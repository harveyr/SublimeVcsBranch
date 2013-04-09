# http://www.sublimetext.com/docs/commands
# http://www.sublimetext.com/docs/2/api_reference.html
# http://www.sublimetext.com/docs/plugin-basics
# http://www.sublimetext.com/docs/3/porting_guide.html

import os
import subprocess
import threading
import re
import datetime
import sublime, sublime_plugin

class CommandRunner(threading.Thread):
    def __init__(self, command_str, callback=None):
        threading.Thread.__init__(self)
        self.callback = callback
        self.command = command_str
        self.start()

    def run(self):
        result = None
        try:
            output = subprocess.check_output(self.command.split(' '))
            result = output.decode("utf-8").strip()
        except Exception as e:
            # print("{}: {}".format(self.command, e))
            result = None
        if self.callback:
            self.callback(result)

class BranchStatusListener(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        view.run_command('branch_status')
    def on_post_save_async(self, view):
        view.run_command('branch_status')

class BranchStatusCommand(sublime_plugin.TextCommand):
    last_full_run = None
    vcs = None
    branch = None
    modified_count = 0
    incoming_count = 0
    outgoing_count = 0
    git_label = 'Git'
    hg_label = 'Hg'

    hg_log_re = r'branch:\s+(\S+)'
    git_log_re = r'^commit \S+'

    def run(self, view):
        self.reset()

        cwd = self.getcwd()
        if not cwd:
            return
        os.chdir(self.getcwd())

        self.fetch_branch()

    def set_branch(self, branch_name):
        """Sets the branch name and fires off the second group of fetchers."""
        if not self.vcs:
            # Stop the rest of the plugin execution
            return

        self.branch = branch_name

        self.fetch_modified_count()

        if self.been_awhile() and self.in_git():
            # Run this stuff only every so often
            CommandRunner('git fetch')

        self.fetch_incoming()
        self.fetch_outgoing()

    def fetch_branch(self):
        """Fetches the branch name, and, in the process, figures out which
        VCS we're in."""
        def hg_callback(output):
            if output:
                self.vcs = self.hg_label
                self.set_branch(output)

        def git_callback(output):
            if output:
                self.set_branch(output)

        CommandRunner('hg branch', hg_callback)
        CommandRunner('git rev-parse --abbrev-ref HEAD', git_callback)

    def fetch_modified_count(self):
        pattern = None
        if self.in_git():
            pattern = r'\s?M \S+'
        else:
            pattern = r'^M \S+'

        def callback(output):
            if not output:
                self.modified_count = 0
                return
            self.modified_count = len(re.findall(pattern, output))
            self.update_status()

        if self.in_git():
            CommandRunner('git status --porcelain', callback)
        elif self.in_hg():
            CommandRunner('hg status', callback)

    def fetch_incoming(self):
        def hg_callback(output):
            if not output:
                self.incoming_count = 0
            else:
                self.incoming_count = self.count_hg_log_matches(
                    re.findall(self.hg_log_re, output))
            self.update_status()

        def git_callback(output):
            if not output:
                self.incoming_count = 0
            else:
                matches = re.findall(self.git_log_re, output,
                    flags=re.MULTILINE)
                self.incoming_count = len(matches)
            self.update_status()

        if self.in_hg():
            CommandRunner('hg incoming', hg_callback)
        elif self.in_git():
            command = 'git whatchanged ..origin/{}'.format(self.branch)
            CommandRunner(command, git_callback)

    def fetch_outgoing(self):
        def hg_callback(output):
            if not output:
                self.outgoing_count = 0
            else:
                self.outgoing_count = self.count_hg_log_matches(
                    re.findall(self.hg_log_re, output))
            self.update_status()

        def git_callback(output):
            if not output:
                self.outgoing_count = 0
            else:
                matches = re.findall(self.git_log_re, output,
                    flags=re.MULTILINE)
                self.outgoing_count = len(matches)
            self.update_status()

        if self.in_git():
            command = 'git whatchanged origin/{}..'.format(self.branch)
            CommandRunner(command, git_callback)

        if self.in_hg():
            CommandRunner('hg outgoing', hg_callback)

    def update_status(self):
        if not self.vcs:
            # We're not in a repo. Clear the status bar
            self.view.set_status('vcs_branch', '')
            return

        s = "({}) {} {}Δ {}↓ {}↑".format(
            self.vcs,
            self.branch,
            self.modified_count,
            self.incoming_count,
            self.outgoing_count)
        self.view.set_status('vcs_branch', s)
        return True

    def count_hg_log_matches(self, matches):
        count = 0
        for match in matches:
            if match == self.branch:
                count += 1
        return count

    def run_command(self, command):
        try:
            output = subprocess.check_output(command.split(' '))
            return output.decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return None

    def reset(self):
        self.vcs = None
        self.branch = '?'
        self.modified_count = '?'
        self.incoming_count = '?'
        self.outgoing_count = '?'
        # self.update_status()

    def in_git(self):
        return self.vcs == self.git_label

    def in_hg(self):
        return self.vcs == self.hg_label

    def been_awhile(self):
        if not self.last_full_run:
            # If we've never set the timestamp, it's been awhile
            self.last_full_run = datetime.datetime.now()
            return True

        delta = datetime.datetime.now() - self.last_full_run
        if delta.seconds > 30:
            # Longer than ^^^ seconds == been awhile
            self.last_full_run = datetime.datetime.now()
            return True

        # Hasn't been very long
        return False

    def getcwd(self):
        file_name = self.get_filename()
        if file_name:
            return '/'.join(self.get_filename().split('/')[:-1])
        else:
            return None

    def get_filename(self):
        return self.view.file_name()

    def test(self, data):
        print(str(data))
