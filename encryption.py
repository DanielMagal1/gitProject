import hashlib

from cryptography.fernet import Fernet as fernet
from pathlib import Path
from hashlib import sha1

class Encryption:
    def __init__(self, key):
        self.key = key

    def encrypt_file(self, file: Path):
        '''
        :param file:
        :return: the hash of the encrypted file
        '''

        if not file.exists():
            raise Exception("file dos not exist")

        with open(file, 'rb') as p1:
            f = fernet(self.key)
            encrypted_file = f.encrypt(p1.read())
        return encrypted_file

    def decrypt_file(self, hash_file):
        '''

        :param hash_file:
        :return: the decrypted file
        '''
        f = fernet(self.key)
        d = f.decrypt(hash_file)
        return d
    def file_hash_generator(self, file: Path):
        '''

        :param file:
        :return: the hash of a file
        '''
        with open(file, 'rb') as f:
            m = hashlib.sha1()
            m.update(f.read())
        return m.hexdigest()






def main():
    ec = Encryption("key").file_hash_generator(r'C:\Users\cyber\Desktop\testing.txt')
    original = "2d83d6189502dc4aeea960be2732b5a131ca19db"




if __name__ == '__main__':
    main()
