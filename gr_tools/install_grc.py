#!/usr/bin/env python
"""Installer for GRC files

This module aids in the instalation of GRC by recursively finding all
the GRC files provided within a directory.  Installation will go
through installation multiple rounds in case GRC have dependencies
on other hierarchal blocks.
"""
import os
import logging
import numpy as np

GRC_EXT = ".grc"

def list_files(c_dir):
    """Recursively find .grc files in the specified directory

    Parameters
    ----------
    c_dir : str
        The absolute path to the directory to scan.

    Returns
    -------
    output : list
        The list of absolute paths to GRC files matching the
        GRC_EXT.
    """
    # --------------------------  error checking  ---------------------------
    assert os.path.isdir(c_dir), "Supplied directory is not a directory"

    # --------------------------  prepare output  ---------------------------
    output = []
    files_list = os.listdir(c_dir)
    for c_file in files_list:
        new_file = c_dir + "/" + c_file
        if os.path.isdir(new_file):
            # directory...scan recursively
            tmp = list_files(new_file)
            output = output + tmp
        elif new_file[-len(GRC_EXT):] == GRC_EXT:
            # track .grc files
            output.append(new_file)
    return output


def install_grc_files(files_list, target):
    """Install GRC files

    This install would go through the list multiple times in case some
    GRC hierarchal or flowgraph has dependency on another.  This function
    will keep attempting until all files have passed or no changes in the
    number of installed GRC.

    Parameters
    ----------
    files_list : list
        List of GRC files with absolute path

    target : str
        The path to install GRC files, where the py and py.block.yml files
        are installed.

    Returns
    -------
    files_pass : list
        List of files that passed

    files_fail : list
        List of files that failed to compile.
    """
    # -----------------------  initialize output  ---------------------------
    files_list = np.array(files_list)
    file_passed = np.array([False] * len(files_list))
    from gnuradio import gr
    while True:
        # NOTE: while loop to capture GRC that is dependent on other GRC file
        #       Each round should include more successful install of GRC.
        #       Otherwise exit.

        # reset number of installed
        num_installed = 0

        for file_ind, c_file in enumerate(files_list):
            # ------------------  skip installed GRC's  ---------------------
            if file_passed[file_ind]:
                continue

            # -----------  try install and track successes  -----------------
            try:
                if gr.api_version() == '7':
                    # on 3.7.14.0, '-d' is used to specify the target location
                    tmp = os.system("grcc %s -d %s"%(c_file, target))
                else:
                    # on 3.8.2.0, '-o' is used to specify the target location
                    tmp = os.system("grcc %s -o %s"%(c_file, target))

                # -------------  check if this worked  ----------------------
                if tmp != 0:
                    raise ValueError("\n\ngrcc failed for %s (%d)\n"\
                        %(c_file, tmp) + "-"*30)

                # -------------------  update success  ----------------------
                file_passed[file_ind] = True
                num_installed += 1

            except Exception as e:
                # don't care in this multi-round install
                pass

        # num_installed did not change or all files complete (time to exit)
        if num_installed == 0 or all(file_passed):
            break

    # return the list of file passing
    return files_list[file_passed], files_list[np.invert(file_passed)]

if __name__ == "__main__":
    # ------------------------  prepare parser  -----------------------------
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("dir", default="flowgraphs",
        help="Base directory to scan for GRC files")
    parser.add_argument("--target", default="~/.grc_gnuradio",
        help="Target location to install (default to ~/.grc_gnuradio)")
    parser.add_argument("--log", default="/tmp/install_grc.log",
        help="Specify location of log file")
    parser.add_argument("--log_level", default=0, type=int,
        help="Log level")
    args = parser.parse_args()

    # -------------------------  prepare logger  ----------------------------
    logging.basicConfig(filename=args.log, level=args.log_level,
        format='%(message)s')

    import time
    logging.info("\n" + "="*50 + \
        "\nRunning install_grc at %s\n"%time.ctime() + "="*50)

    # get list of files
    files = list_files(os.path.abspath(args.dir))

    # install grc
    passed, failed = install_grc_files(files, target=args.target)
    logging.info("\nPassed\n" + "="*40)
    for c_file in passed:
        logging.info("\t%s"%c_file)

    logging.info("\nFailed\n" + "="*40)
    for c_file in failed:
        logging.info("\t%s"%c_file)