import dan as D

def main():
    """
    testing the diff function (currently does not work)
    """
    num_diff = D.GitRepository.diff("file1.txt", "file2.txt")
    print(num_diff)


if __name__ == "__main__":
    main()