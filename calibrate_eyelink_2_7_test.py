# -*- coding: utf-8 -*-



import argparse
# defined command line options
# this also generates --help and error handling
CLI=argparse.ArgumentParser()

CLI.add_argument(
    "--edf_path",  # name on the CLI - drop the `--` for positional/required parameters
    type=str,
    default="py27_calibration.edf",  # default if nothing is provided
)


CLI.add_argument(
    "--displayResolution",  # name on the CLI - drop the `--` for positional/required parameters
    nargs="*",  # 0 or more values expected => creates a list
    type=int,
    default= [1920,1080],  # default if nothing is provided
)


CLI.add_argument(
    "--monWidth",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 67.5,  # default if nothing is provided
)


CLI.add_argument(
    "--monDistance",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 90.0,  # default if nothing is provided
)

CLI.add_argument(
    "--monHeight",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 37.5,  # default if nothing is provided
)


CLI.add_argument(
    "--foregroundColor",  # name on the CLI - drop the `--` for positional/required parameters
    nargs="*",  # 0 or more values expected => creates a list
    type=int,
    default= [1,1,1],  # default if nothing is provided
)

CLI.add_argument(
    "--backgroundColor",  # name on the CLI - drop the `--` for positional/required parameters
    nargs="*",  # 0 or more values expected => creates a list
    type=int,
    default= [1,1,1],  # default if nothing is provided
)

CLI.add_argument(
    "--textHeightETclient",  # name on the CLI - drop the `--` for positional/required parameters
    type=float,
    default= 0.5,  # default if nothing is provided
)



# parse the command line
args = CLI.parse_args()
# access CLI options
print("running script with arguments:")

print("edf_path: %r" % args.edf_path)
print("displayResolution: %r" % args.displayResolution)
print("monWidth: %r" % args.monWidth)
print("monDistance: %r" % args.monDistance)
print("monHeight: %r" % args.monHeight)
print("foregroundColor: %r" % args.foregroundColor)
print("backgroundColor: %r" % args.backgroundColor)
print("textHeightETclient: %r" % args.textHeightETclient)


