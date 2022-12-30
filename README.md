The purpose of this library is to be able to easily run a Python script to update
a local backup of all your current media to disk.

By streamlining manual entry of photos into different folders, sorted by some "key" (i.e. year),
we can eliminate the need to manually check whether or not a picture already exists in the
library, as well as verify that a backup of all photos exists.

As far as importing the data, all that matters is that Python 3+ is installed and the library has been copied to the local directory of the user.

One of the advantages of using the automator app is that we can take out important pieces of the code, passing them as command line arguments - one potential use for this might be to change where the files are getting stored without actually having to change the script itself.

This application is meant to be run from MacOS only. Developed in Monterey 12.6 on a MBP 2020 - M1.

