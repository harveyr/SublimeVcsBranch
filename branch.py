# http://www.sublimetext.com/docs/commands
# http://www.sublimetext.com/docs/2/api_reference.html
# http://www.sublimetext.com/docs/plugin-basics
# http://www.sublimetext.com/docs/3/porting_guide.html

import os
import subprocess
import threading
import re
import sublime, sublime_plugin

class CommandRunner(threading.Thread):
    def __init__(self, command_str, callback):
        threading.Thread.__init__(self)
        self.callback = callback
        self.command = command_str
        self.start()

    def run(self):
        try:
            output = subprocess.check_output(self.command.split(' '))
            self.callback(output.decode("utf-8").strip())
        except subprocess.CalledProcessError:
            self.callback(None)

class BranchStatusListener(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        view.run_command('branch_status')
    def on_post_save_async(self, view):
        view.run_command('branch_status')

class BranchStatusCommand(sublime_plugin.TextCommand):
    vcs = None
    branch = None
    modified_count = 0
    git_label = 'Git'
    hg_label = 'Hg'

    def run(self, view):
        self.reset()
        self.set_branch()

    def set_branch(self):
        cwd = self.get_cwd()
        if not cwd:
            return False

        os.chdir(self.get_cwd())

        CommandRunner('hg branch', self.hg_branch_callback)
        CommandRunner('git branch', self.git_branch_callback)

    def hg_branch_callback(self, output):
        if output:
            self.branch = output
            self.vcs = self.hg_label
            self.update_status()
            self.set_modified_count()

    def git_branch_callback(self, output):
        if output:
            branch = re.findall(r'\* (\S+)$', output)[0]
            self.branch = branch
            self.vcs = self.git_label
            self.update_status()
            self.set_modified_count()

    def set_modified_count(self):
        # return
        if self.in_git():
            CommandRunner('git status --porcelain',
                self.modified_count_callback)
        elif self.in_hg():
            CommandRunner('hg status', self.modified_count_callback)

    def modified_count_callback(self, data):
        if not data:
            self.modified_count = 0
        else:
            self.modified_count = len(data.split('\n'))
        self.update_status()

    def update_status(self):
        if not self.vcs:
            self.reset()

        s = "[{}: {} | {} modified]".format(self.vcs, self.branch,
            self.modified_count)
        self.view.set_status('vcs_branch', s)
        return True

    def run_command(self, command):
        try:
            output = subprocess.check_output(command.split(' '))
            return output.decode("utf-8").strip()
        except subprocess.CalledProcessError:
            return None

    def reset(self):
        self.vcs = None
        self.branch = None
        self.modified_count = 0
        self.view.set_status('vcs_branch', '')

    def in_git(self):
        return self.vcs == self.git_label

    def in_hg(self):
        return self.vcs == self.hg_label

    def get_cwd(self):
        file_name = self.get_filename()
        if file_name:
            return '/'.join(self.get_filename().split('/')[:-1])
        else:
            return None

    def get_filename(self):
        return self.view.file_name()
