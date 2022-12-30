import pytz
import os
import sys
import click
from datetime import datetime
from configparser import ConfigParser
from pyicloud import PyiCloudService


class Configuration:
    """Read in the Configuration Settings found in the 'config.ini' file.

    This is where we can customize certain filters for our retrieval,
    as well as specify our credentials used to log in."""

    # Establish some attributes to access later on via instance of a 'Configuration' object
    def __init__(self):
        config = ConfigParser()
        if len(sys.argv[1:]) == 0:
            config.read('pyicloud/config.ini')
        else:
            config.read(sys.argv[1:])

        # These are the customizeable variables found in the configuration file
        self.maxphotos = config.getint('Photos', 'max_photos')
        self.myid = config.get('User','appleid')
        self.mypass = config.get('User','applepwd')
        self.alb = config.get('Photos','album')
        self.to_dir = config.get('Photos','to_directory')
        self.from_date = config.get('Photos','date_from')
        self.to_date = config.get('Photos','date_to')
        self.asset_from = config.get('Photos','asset_from')
        self.asset_to = config.get('Photos','asset_to')
        self.time_zone = config.get('TimeZone','timezone')

        # Convert Dates for Photos into TZ Aware Dates
        self.tz = pytz.timezone(self.time_zone)
        self.from_date = datetime.fromisoformat(self.from_date)
        self.from_date = self.tz.localize(self.from_date, is_dst=None).astimezone(pytz.utc)
        self.to_date = datetime.fromisoformat(self.to_date)
        self.to_date = self.tz.localize(self.to_date, is_dst=None).astimezone(pytz.utc)
        self.asset_from = datetime.fromisoformat(self.asset_from)
        self.asset_from = self.tz.localize(self.asset_from, is_dst=None).astimezone(pytz.utc)
        self.asset_to = datetime.fromisoformat(self.asset_to)
        self.asset_to = self.tz.localize(self.asset_to, is_dst=None).astimezone(pytz.utc)


class iCloud:
    """Connects to iCloud using the credentials listed in the config.ini file.

    Loops through all requested photos to store into 'Local/Photos/',

    the photos are saved as their datetime and respective file type."""

    def __init__(self):
        # Initialize the configuration
        self.config = Configuration()

        try:
            # Connect to iCloud
            self.api = PyiCloudService(self.config.myid, self.config.mypass)
            print("#----------------------------------iCloud Connection----------------------------------#")
        except:
            print("\nUnable to connect to iCloud, please verify credentials and try again...\n")
            sys.exit(1)

    # Verify the connection and send authentication code if necessary
    def verification(self):
        if self.api.requires_2fa:
            print("Two-factor authentication required.")
            code = input("Enter the code you received of one of your approved devices: ")
            result = self.api.validate_2fa_code(code)
            print("Code validation result: %s" % result)

            if not result:
                print("Failed to verify security code")
                sys.exit(1)

            if not self.api.is_trusted_session:
                print("Session is not trusted. Requesting trust...")
                result = self.api.trust_session()
                print("Session trust result %s" % result)

                if not result:
                    print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

        elif self.api.requires_2sa:
            import click
            print("Two-step authentication required. Your trusted devices are:")
            
            devices = self.api.trusted_devices

            for i, device in enumerate(devices):
                print(
                    "  %s: %s" % (i, device.get('deviceName',
                    "SMS to %s" % device.get('phoneNumber')))
                )

            device = click.prompt('Which device would you like to use?', default=0)
            device = devices[device]
            if not self.api.send_verification_code(device):
                print("Failed to send verification code")
                sys.exit(1)

            code = click.prompt('Please enter validation code')
            if not self.api.validate_verification_code(device, code):
                print("Failed to verify verification code")
                sys.exit(1)

    # Start the Download of Photos, set start time for process
    def start_download(self):
        self.timefordownload = datetime.now()

        print()
        print("Collection Parameters:\n")
        print(" Date Period :", self.config.from_date.strftime("%b %d, %Y"), " - ", self.config.to_date.strftime("%b %d, %Y"))
        print(" Album(s)    :", self.config.alb)
        print()
        print("Starting collection...")

        # Set album or all photos
        if self.config.alb == 'all':
            self.photo = iter(self.api.photos.all)
        else:
            self.photo = iter(self.api.photos.albums[self.config.alb])

    # Main Function - Call Internal Methods
    def main(self):
        downloadedphotos = 0
        skippedphotos = 0
        photofileexists = 0
        
        self.start_download()

        while(True):

            # Process Next Photo
            dlphoto = next(self.photo, 'end')

            # Set Condition to stop processing photos.  And exit if met.
            exitloopcondition = (downloadedphotos >= self.config.maxphotos) \
                                or (not hasattr(dlphoto,'added_date')) \
                                or (dlphoto.added_date <= self.config.from_date)

            if exitloopcondition:
                totaltime = datetime.now()-self.timefordownload
                print()
                print(downloadedphotos,"FILE(S) DOWNLOADED")
                print(skippedphotos, "FILE(S) SKIPPED")
                print()
                print("Total download time:", totaltime)
                break

            # if exit condition was not met, process photo to download (or not download)
            else:
                # break out asset created date for creating directory structure and file name
                dlyear = str(dlphoto.asset_date)[0:4]
                dlmonth = str(dlphoto.asset_date)[5:7]
                dlday = str(dlphoto.asset_date)[8:10]
                dldirectory = self.config.to_dir + dlyear + "/" + dlmonth + "/" + dlday + "/"
                dlfullfile = dldirectory + dlphoto.filename

                # If the file does not exist in the target directory, and it is within the
                # requested asset date range in the config.ini file, start to download
                # the photo, or else loop.  Start timer on the process for downloading.
                validdate = self.config.asset_to >= dlphoto.asset_date >= self.config.asset_from

                if (not os.path.exists(dlfullfile)) and (validdate):

                    print("DOWNLOADING: ", dlfullfile)

                    # If the directory does not exist, create the directory
                    if not os.path.isdir(dldirectory):
                        os.makedirs(dldirectory)

                    # Download file and write into directory and
                    download = dlphoto.download()
                    with open(dlfullfile, 'wb') as opened_file:
                        opened_file.write(download.raw.read())

                    # Increment downloaded photo variable  
                    downloadedphotos = downloadedphotos + 1

                else:
                    # Increment skipped photo variable if photo was not downloaded
                    skippedphotos = skippedphotos + 1
                    if os.path.exists(dlfullfile):
                        photofileexists = photofileexists + 1


if __name__ == "__main__":
    obj = iCloud()
    obj.main()

print("\n...THE END")