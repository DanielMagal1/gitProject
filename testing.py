import hashlib



def file_hash_generator(file):
    '''

    :param file:
    :return: the hash of a file
    '''
    with open(file, 'rb') as f:
        m = hashlib.sha1()
        m.update(f.read())
    return m.hexdigest()



def main():
    ec = file_hash_generator(r'C:\Users\cyber\Desktop\testing.txt')
    print(ec)


if __name__ == '__main__':
    main()
