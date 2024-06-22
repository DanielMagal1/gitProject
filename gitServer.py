import socket
import threading
import json
import os
import pathlib
import shutil
import hashlib
import datetime

class GitServer:
    def _init_(self, host='localhost', port=5000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.gitdir = "./server_repo/.git"
        self.logfile = os.path.join(self.gitdir, "log.txt")
        self.gitRepoPath = os.path.join(self.gitdir, "Repository")
        self.trackingAreaPath = os.path.join(self.gitdir, "trackingArea.json")
        self.treeOfCommitsPath = os.path.join(self.gitdir, "treeOfCommits.json")
        self.indexFilePath = os.path.join(self.gitdir, "index.json")
        self.commitHeadPath = os.path.join(self.gitdir, "commitHead.txt")

        self.trackingArea = {}
        self.treeOfCommits = {}
        self.index = {}
        self.commitHead = None

        if not os.path.exists(self.gitdir):
            os.makedirs(self.gitRepoPath)
            open(self.trackingAreaPath, 'w').close()
            open(self.treeOfCommitsPath, 'w').close()
            open(self.indexFilePath, 'w').close()
            open(self.commitHeadPath, 'w').close()
            open(self.logfile, 'w').close()
        else:
            self.load_repository()

    def load_repository(self):
        with open(self.trackingAreaPath, 'r') as file:
            self.trackingArea = json.load(file) if os.path.getsize(self.trackingAreaPath) > 0 else {}
        with open(self.treeOfCommitsPath, 'r') as file:
            self.treeOfCommits = json.load(file) if os.path.getsize(self.treeOfCommitsPath) > 0 else {}
        with open(self.indexFilePath, 'r') as file:
            self.index = json.load(file) if os.path.getsize(self.indexFilePath) > 0 else {}
        with open(self.commitHeadPath, 'r') as file:
            self.commitHead = file.read().strip() if os.path.getsize(self.commitHeadPath) > 0 else None

    def save_repository(self):
        with open(self.trackingAreaPath, 'w') as file:
            json.dump(self.trackingArea, file)
        with open(self.treeOfCommitsPath, 'w') as file:
            json.dump(self.treeOfCommits, file)
        with open(self.indexFilePath, 'w') as file:
            json.dump(self.index, file)
        with open(self.commitHeadPath, 'w') as file:
            file.write(self.commitHead if self.commitHead else "")

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(4096).decode('utf-8')
                if not message:
                    break
                response = self.process_command(json.loads(message))
                client_socket.send(json.dumps(response).encode('utf-8'))
            except ConnectionResetError:
                break

        client_socket.close()

    def process_command(self, command):
        action = command.get('action')
        if action == 'init':
            self.init_repo()
        elif action == 'add':
            self.add_files(command.get('files'))
        elif action == 'commit':
            self.commit(command.get('message'))
        elif action == 'status':
            return self.status()
        elif action == 'diff':
            return self.diff(command.get('commit1'), command.get('commit2'))
        elif action == 'log':
            return self.log()
        elif action == 'rollback':
            self.rollback()
        elif action == 'checkout':
            self.checkout(command.get('commitID'))
        elif action == 'push':
            return self.push(command.get('client_tracking_area'), command.get('client_index'), command.get('client_commit_head'))
        elif action == 'pull':
            return self.pull()
        elif action == 'help':
            return self.help()
        else:
            return {'status': 'error', 'message': 'Unknown action'}
        self.save_repository()
        return {'status': 'success'}

    def init_repo(self):
        if not os.path.exists(self.gitdir):
            os.makedirs(self.gitRepoPath)
            open(self.trackingAreaPath, 'w').close()
            open(self.treeOfCommitsPath, 'w').close()
            open(self.indexFilePath, 'w').close()
            open(self.commitHeadPath, 'w').close()
            open(self.logfile, 'w').close()
        else:
            return {'status': 'error', 'message': 'Repository already initialized'}

    def add_files(self, files):
        for file in files:
            file_path = pathlib.Path(file)
            if file_path.is_file():
                self.trackingArea[str(file_path)] = self.sha_of(file)
                dest = os.path.join(self.gitRepoPath, self.sha_of(file))
                shutil.copy(file, dest)

    def commit(self, message):
        commit_id = self.get_commit_id()
        self.treeOfCommits[commit_id] = self.commitHead
        self.index[commit_id] = self.trackingArea.copy()
        self.commitHead = commit_id
        log_entry = f"Commit ID: {commit_id}\nCommit Message: {message}\nTimestamp: {datetime.datetime.now()}\n"
        with open(self.logfile, 'a') as log_file:
            log_file.write(log_entry)

    def status(self):
        modified_files = [f for f in self.trackingArea if self.sha_of(f) != self.trackingArea[f]]
        untracked_files = [str(p) for p in pathlib.Path('.').rglob('*') if p.is_file() and str(p) not in self.trackingArea]
        return {
            'trackingArea': self.trackingArea,
            'modifiedFiles': modified_files,
            'untrackedFiles': untracked_files,
            'commitHead': self.commitHead
        }

    def diff(self, commit1, commit2):
        if commit1 not in self.index or commit2 not in self.index:
            return {'status': 'error', 'message': 'Invalid commit ID'}
        files1 = set(self.index[commit1].keys())
        files2 = set(self.index[commit2].keys())
        added = files2 - files1
        removed = files1 - files2
        modified = {f for f in files1 & files2 if self.index[commit1][f] != self.index[commit2][f]}
        return {'status': 'success', 'added': list(added), 'removed': list(removed), 'modified': list(modified)}

    def log(self):
        with open(self.logfile, 'r') as log_file:
            return {'status': 'success', 'log': log_file.read()}

    def rollback(self):
        if self.commitHead in self.treeOfCommits:
            self.checkout(self.treeOfCommits[self.commitHead])

    def checkout(self, commitID):
        if commitID not in self.index:
            return {'status': 'error', 'message': 'Invalid commit ID'}
        self.trackingArea = self.index[commitID]
        self.commitHead = commitID

    def push(self, client_tracking_area, client_index, client_commit_head):
        # Check for conflicts
        for file, sha in client_tracking_area.items():
            if file in self.trackingArea and self.trackingArea[file] != sha:
                return {'status': 'error', 'message': f'Conflict detected in file: {file}'}

        # Update server with client changes
        self.trackingArea.update(client_tracking_area)
        self.index.update(client_index)
        self.commitHead = client_commit_head
        self.save_repository()

        # Copy client files to server repository
        for file, sha in client_tracking_area.items():
            src = file
            dest = os.path.join(self.gitRepoPath, sha)
            shutil.copy2(src, dest)

        return {'status': 'success', 'message': 'Push successful'}

    def pull(self):
        return {
            'status': 'success',
            'trackingArea': self.trackingArea,
            'index': self.index,
            'commitHead': self.commitHead
        }

    def help(self):
        commands = [
            'init', 'add', 'status', 'commit', 'diff',
            'log', 'rollback', 'checkout', 'push', 'pull', 'help'
        ]
        return {'status': 'success', 'commands': commands}

    def get_commit_id(self):
        t = str(datetime.datetime.now())
        return hashlib.sha256(t.encode('utf-8')).hexdigest()

    def sha_of(self, filename):
        sha1_hash = hashlib.sha1()
        with open(filename, 'rb') as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha1_hash.update(byte_block)
        return sha1_hash.hexdigest()

    def start(self):
        print("Server started...")
        while True:
            client_socket, addr = self.server.accept()
            print(f"Connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if _name_ == "_main_":
    server = GitServer()
    server.start()
