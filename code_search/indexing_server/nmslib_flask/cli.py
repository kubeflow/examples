import sys
import argparse
import logging
logging.basicConfig(level=logging.INFO)


def parse_args(args):
  parser = argparse.ArgumentParser(prog='NMSLib Flask Server')

  return parser.parse_args(args)

if __name__ == '__main__':
  args = parse_args(sys.argv[1:])
