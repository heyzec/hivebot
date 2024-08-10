from dotenv import load_dotenv
from hivebot.app import start


def main():
    load_dotenv()
    start()

if __name__ == "__main__":
    main()
