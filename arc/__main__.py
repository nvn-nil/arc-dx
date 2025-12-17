import argparse

from arc.cleanup_untracked_git import find_and_move_untracked_files


parser = argparse.ArgumentParser(description="ARC Main Entry Point")
parser.add_argument("command", help="Command to execute")
def main():
    args = parser.parse_args()

    if args.command == "sweep":
        find_and_move_untracked_files()


if __name__ == "__main__":
    main()
