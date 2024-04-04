import dan as D

def main():
    """
    testing the diff function (currently does not work)
    """
    num_diff = D.GitRepository.diff("text1.txt", "text2.txt")
    print(num_diff)


if __name__ == "__main__":
    main()