import dan as D

def main():
    """
    testing the diff fuction (currently does not work)
    """
    num_diff = D.GitRepository.diff("text.txt", "text2.txt")
    print(num_diff)


if __name__ == "__main__":
    main()