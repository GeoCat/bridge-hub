import os
import argparse
import json

from bridgehub import api
from bridgehub.publish.publish import publish_project

def main():
    parser = argparse.ArgumentParser(description='Starts the Bridgehub server or publishes a Bridgehub project.')
    parser.add_argument('-f', '--filename' help='Filename with a publish project to process')

    args = parser.parse_args()

    if args.filename:
        with open(args.filename) as f:
            project = json.load(f)
        ret = publish_project(project)
        print(ret)
    else:
        api.main()

if __name__ == "__main__":
    main()
