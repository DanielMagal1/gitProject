import os
import sys
import time
import json
import shutil
import pathlib
import hashlib
import datetime
from colorama import Fore


class GitRepository:
    """A git repository"""

    def __init__(self, path, force=False):
        self.gitdir = os.path.join(path, ".git")
        self.logfile = os.path.join(self.gitdir, "log.txt")
        self.gitRepoPath = os.path.join(self.gitdir, "Repository")
        self.trackedFilePath = os.path.join(self.gitdir, "trackedFile.txt")
        self.commitHeadPath = os.path.join(self.gitdir, "commitHead.txt")
        self.trackingAreaPath = os.path.join(self.gitdir, "trackingArea.json")
        self.treeOfCommitsPath = os.path.join(
            self.gitdir, "treeOfCommits.json")
        self.indexFilePath = os.path.join(self.gitdir, "index.json")
        self.workingDirectoryFiles = set()
        self.modifiedFiles = set()
        self.trackedFiles = set()
        self.treeOfCommits = {}
        self.trackingArea = {}
        self.index = {}
        self.commitHead = None
        self.RemoteRepo = "/Users/daniel/Downloads/Remote"

    # writing from data structures into the files in .git folder

    def writeToTxt_tf(self):
        tracked_txt = open('./.git/trackedFile.txt', 'w')
        for file in self.trackedFiles:
            line = str(file) + "\n"
            tracked_txt.write(line)

    def writeToTxt_ch(self):
        tracked_txt = open('./.git/commitHead.txt', 'w')
        if self.commitHead is None:
            to_write = "None"
        else:
            to_write = str(self.commitHead)

        tracked_txt.write(to_write)

    def writeToJson_ta(self):
        tracking_json = open('./.git/trackingArea.json', 'w')
        temp = {}
        for item in self.trackingArea:
            temp[str(item)] = self.trackingArea[item]
        json.dump(temp, tracking_json)

    def writeToJson_toc(self):
        toc_json = open('./.git/treeOfCommits.json', 'w')
        temp = {}
        for item in self.treeOfCommits:
            temp[str(item)] = self.treeOfCommits[item]
        json.dump(temp, toc_json)

    def writeToJson_index(self):
        index_json = open('./.git/index.json', 'w')
        json.dump(self.index, index_json)

    # reading from files into data structures from .git folder

    def readFromTxt_tf(self):
        self.trackedFiles.clear()
        tracked_txt = open('./.git/trackedFile.txt', 'r')
        for file in tracked_txt:
            path = pathlib.Path(os.path.relpath(file))
            self.trackedFiles.add(path)

    def readFromTxt_ch(self):
        tracked_txt = open('./.git/commitHead.txt', 'r')
        self.commitHead = tracked_txt.read()

    def readFromJson_ta(self):
        tracking_json = open('./.git/trackingArea.json', 'r')
        self.trackingArea = json.load(tracking_json)

    def readFromJson_toc(self):
        toc_json = open('./.git/treeOfCommits.json', 'r')
        self.treeOfCommits = json.load(toc_json)

    def readFromJson_index(self):
        index_json = open('./.git/index.json', 'r')
        self.index = json.load(index_json)

    # utility functions

    def shaOf(self, filename):
        sha1_hash = hashlib.new('sha1')
        with open(filename, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha1_hash.update(byte_block)
        return sha1_hash.hexdigest()

    def delFilesOfWorkingDirectory(self, path):
        relative = pathlib.Path(os.path.relpath(path))
        for p in pathlib.Path(relative).iterdir():
            if p.is_file():
                os.remove(p)
            elif p.is_dir():
                self.delFilesOfWorkingDirectory(p)
                os.rmdir(p)

    # git_INIT

    def ExecInit(self, cmd):
        if os.path.exists(self.gitdir):
            print("\n<<-- Git Directory has been ALREADY initialised -->>\n")
            sys.exit(0)

        if not os.path.exists(self.gitdir):
            os.mkdir(self.gitdir)

        if not os.path.exists(self.logfile):
            open(self.logfile, 'w').close()

        if not os.path.exists(self.trackedFilePath):
            open(self.trackedFilePath, 'w').close()

        if not os.path.exists(self.commitHeadPath):
            open(self.commitHeadPath, 'w').close()

        if not os.path.exists(self.treeOfCommitsPath):
            open(self.treeOfCommitsPath, 'w').close()

        if not os.path.exists(self.indexFilePath):
            open(self.indexFilePath, 'w').close()

        if not os.path.exists(self.trackingAreaPath):
            open(self.trackingAreaPath, 'w').close()

        if not os.path.exists(self.gitRepoPath):
            os.mkdir(self.gitRepoPath)

    # git_ADD

    def addDir(self, path):
        for p in pathlib.Path(path).iterdir():
            if p.is_file() and p not in self.trackingArea:
                self.trackingArea[self.shaOf(p)] = p.read_text()
                self.trackedFiles.add(p)
            elif p.is_dir() and not p.match("*/.git"):
                self.addDir(p)

    def gitAdd(self, p):
        # p is a list of arguments
        for element in p:
            relative = pathlib.Path(os.path.relpath(element))
            if relative.is_file():
                self.trackingArea[relative] = self.shaOf(element)
                relative = str(relative).strip()
                if relative == "" or relative == "\n":
                    continue
                self.trackedFiles.add(relative)
            elif relative.is_dir():
                for k in list(self.trackingArea.keys()):  # To Handle if file is deleted
                    if k.startswith(element):  # To Handle if file is deleted
                        del self.trackingArea[k]
                self.addDir(relative)

    # git_STATUS

    def addFilesOfWorkingDirectory(self, path):
        relative = pathlib.Path(os.path.relpath(path))
        for p in pathlib.Path(relative).iterdir():
            if p.is_file():
                self.workingDirectoryFiles.add(p)
            elif ((p.is_dir()) & (not p.match(".git"))):
                self.addFilesOfWorkingDirectory(p)

    def gitStatus(self):
        self.workingDirectoryFiles.clear()
        self.modifiedFiles.clear()
        self.addFilesOfWorkingDirectory(".")

        temp = set()
        temp2 = set()
        untrackedFiles = set()

        for i in self.workingDirectoryFiles:
            temp.add(str(i))

        for i in self.trackingArea:
            temp2.add(str(i))

        untrackedFiles = temp.difference(temp2)

        cwd = pathlib.Path(os.path.abspath("."))
        position = len(str(cwd))

        if len(self.trackedFiles) != 0:
            print("\nAdded Files: ")
            counter = 0
            for item in self.trackedFiles:
                item = str(item).strip()
                if item == "":
                    continue
                print(str(counter + 1) + " -> " +
                      Fore.GREEN + str(item) + Fore.WHITE, "\n")
                counter = counter + 1

        if len(untrackedFiles) != 0:
            print("\nUntracked Files: ")
            counter = 0
            for item in untrackedFiles:
                print(str(counter + 1) + " -> " +
                      Fore.RED + str(item) + Fore.WHITE + "\n")
                counter = counter + 1

        for i in self.trackingArea:
            if self.trackingArea[i] != self.shaOf(i):
                self.modifiedFiles.add(i)

        if len(self.modifiedFiles) != 0:
            print("\nModified Files: ")
            counter = 0
            for item in self.modifiedFiles:
                print(str(counter + 1) + " -> " +
                      Fore.YELLOW + str(item) + Fore.WHITE)
                counter = counter + 1

    # git_COMMIT

    def getCommitId(self):
        t = str(time.time())
        t_encoded = t.encode("utf-8")
        soc = hashlib.sha256()
        soc.update(t_encoded)
        return soc.hexdigest()

    def getExtension(self, fileName):
        pos = str(fileName).rfind(".")
        extension = str(fileName)[pos:]
        return extension

    def ExecCommit(self, msg):
        if len(self.index) == 0:
            self.commitHead = None

        curr_commit_id = self.getCommitId()
        # if no changes then why commit..?

        self.treeOfCommits[curr_commit_id] = self.commitHead
        self.index[curr_commit_id] = {}

        for fileName in self.trackingArea:
            self.index[curr_commit_id][fileName] = self.shaOf(fileName)
            if (self.trackingArea[fileName] is None) or (
                    self.index.get(self.treeOfCommits.get(curr_commit_id, {}), {}).get('fileName') !=
                    self.index[curr_commit_id][fileName]):
                # need to ponder
                self.trackingArea[fileName] = self.index[curr_commit_id][fileName]
                extension = self.getExtension(fileName)
                dest = self.gitRepoPath + "/" + \
                       self.index[curr_commit_id][fileName] + extension
                shutil.copy(fileName, dest)

        self.commitHead = curr_commit_id
        # updating logs
        log_txt = open('./.git/log.txt', 'r+')
        commit_id = str(self.commitHead)
        if commit_id == "None":
            commit_id = "Initial Commit"
        to_write = "Commit ID : " + commit_id + "\n"
        to_write += "Commit Message : " + str(msg) + "\n"
        time = datetime.datetime.now()
        to_write += "Timestamp : " + str(time.strftime("%c")) + "\n\n"
        prev_log = log_txt.read()
        log_txt.seek(0, 0)
        log_txt.write(to_write.rstrip('\r\n') + '\n' + prev_log)

        self.trackedFiles.clear()
        self.modifiedFiles.clear()

    # git_DIFF
    @staticmethod
    def diff(f1, f2):
        file_1 = open(f1, 'r')
        file_2 = open(f2, 'r')
        a = file_1.readlines()
        b = file_2.readlines()
        len1 = len(a)  # the length of file 1
        len2 = len(b)  # the length of file 2
        dp = [[0 for i in range(len1 + 1)] for j in range(len2 + 1)]
        # when len1 = 0 (meaning all lines had been deleted)
        if len1 == 0:
            for j in range(len1 + 1):
                dp[0][j] = j
        # when len2 = 0 (meaning all lines had been deleted)
        if len2 == 0:
        for i in range(len2 + 1):
            dp[i][0] = i
        # taking into account the different scenarios(deletion, adding, changing etc.)
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if a[i-1] == b[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],  # Insertion
                        dp[i][j - 1],  # Deletion
                        dp[i - 1][j - 1]  # Replacement
                    )

        return dp[len1][len2]

    @staticmethod
    def printDifference(x1, x2):
        # Open File in Read Mode
        file_1 = open(x1, 'r')
        file_2 = open(x2, 'r')

        file_1_line = file_1.readline()
        file_2_line = file_2.readline()

        # Use as a Counter
        line_no = 1

        print("Difference Lines in Both Files :\n")
        while file_1_line != '' or file_2_line != '':

            # Removing whitespaces
            file_1_line = file_1_line.rstrip()
            file_2_line = file_2_line.rstrip()

            # Compare the lines from both file
            if file_1_line != file_2_line:

                # otherwise output the line on file1 and use @ sign
                if file_1_line == '':
                    print("@", "Line-%d" % line_no, file_1_line)
                else:
                    print(Fore.RED, "@-", " Line-%d " %
                          line_no, Fore.WHITE, file_1_line, sep="")

                # otherwise output the line on file2 and use # sign
                if file_2_line == '':
                    print("#", "Line-%d" % line_no, file_2_line)
                else:
                    print(Fore.GREEN, "#+", " Line-%d " %
                          line_no, Fore.WHITE, file_2_line, sep="")

                # Print a empty line
                print()

            # Read the next line from the file
            file_1_line = file_1.readline()
            file_2_line = file_2.readline()

            line_no += 1

        file_1.close()
        file_2.close()


def main():
    num_diff = GitRepository.diff("text.txt", "text2.txt")
    print(num_diff)

if __name__ == "__main__":
    main()
