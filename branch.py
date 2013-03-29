# http://www.sublimetext.com/docs/commands
# http://www.sublimetext.com/docs/2/api_reference.html
# http://www.sublimetext.com/docs/plugin-basics

import os
import subprocess
import re
import sublime, sublime_plugin

class BranchStatusListener(sublime_plugin.EventListener):
    def on_activated(self, view):
        # print('on_activated')
        view.run_command('branch_status')
    def on_post_save(self, view):
        view.run_command('branch_status')
        # print('on_post_save')

class BranchStatusCommand(sublime_plugin.TextCommand):
    def run(self, view):
        hg_branch = None
        git_branch = None

        os.chdir(self.get_cwd())
        try:
            hg_branch = subprocess.check_output(['hg', 'branch'])
            hg_branch = hg_branch.decode("utf-8").strip()
        except subprocess.CalledProcessError:
            pass

        try:
            git_branch = subprocess.check_output(['git', 'branch'])
            git_branch = git_branch.decode("utf-8").strip()
        except subprocess.CalledProcessError:
            pass

        branch = hg_branch if hg_branch else git_branch

        if branch:
            self.view.set_status('vcs_branch', self.format(branch))
        else:
            self.view.set_status('vcs_branch', '')

    def format(self, branch_str):
        return "Branch {}".format(branch_str)

    def get_cwd(self):
        return '/'.join(self.get_filename().split('/')[:-1])

    def get_filename(self):
        return self.view.file_name()
