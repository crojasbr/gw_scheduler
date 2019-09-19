from datetime import tzinfo, timedelta, datetime
from astropy import units as u
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.io import ascii
from astropy.time import Time
from astropy.table import unique
import csv, requests, sys

target_lists = {
    'nickel': 'https://ziggy.ucolick.org/yse/explorer/10/download?format=csv'
}

dum_coord = SkyCoord(0., 0., unit='deg')
dum_time  = Time('2019-01-01T00:00:00')
target_table_names = ('name', 'coord', 'priority', 'date', 'mag', 'type')
target_table_row   = [['X' * 40], [dum_coord], [0.0],
    [dum_time], [0.0], ['X' * 40]]

class UTC_Offset(tzinfo):

    # Offset assumed to be hours
    def __init__(self, offset=0, name=None):
        self.offset = timedelta(seconds=offset*3600)
        self.name = name or self.__class__.__name__

    def utcoffset(self, dt):
        return self.offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return timedelta(0)

# Chile observes Chile Summer Time (CLST) from 1/1/2017 - 5/13/2017 => UTC-3
# Chile observes Chile Standard Time (CLT) from 5/13/2017 - 8/12/2017 => UTC-4
# Chile observes Chile Summer Time (CLST) from 8/13/2017 - 12/31/2017 => UTC-3
lco_clst_utc_offset = -3 # hours
lco_clt_utc_offset = -4 # hours

# California observes Pacific Standard Time (PST) from 1/1/2017 - 3/12/2017 => UTC-8
# California observes Pacific Daylight Time (PDT) from 3/12/2017 - 11/5/2017 => UTC-7
# California observes Pacific Standard Time (PST) from 11/5/2017 - 12/31/2017 => UTC-8
lick_pst_utc_offset = -8 # hours
lick_pdt_utc_offset = -7 # hours

keck_offset=-10


# Get a blank target table
def blank_target_table():
    tab = Table(target_table_row, names=target_table_names)
    return(tab[:0].copy())

# file_name assumed to be CSV with headers...
def get_targets(file_name):
    csvfile = open(file_name, 'r')
    reader = csv.reader(csvfile, delimiter=',')
    #next(reader, None) # Skip headers
    data = list(reader)

    # Reformat data to create SkyCoord and Time objects
    ref_data = []
    for row in data:
        coord = SkyCoord(row[1], row[2], unit=(u.hour, u.deg))
        time  = Time(row[4])
        line = [row[0], coord, row[3], time, row[5], row[6]]
        ref_data.append(line)


    # Reformat as astropy table
    targets = Table(list(map(list, zip(*ref_data))), names=target_table_names)

    return(targets)

def download_targets(telescope):

    # Resolve the URL for the correct target list
    if telescope.lower() in target_lists.keys():
        url = target_lists[telescope.lower()]

        # Use requests to get list of targets
        data = requests.get(url)

        # Format into a table with the same names as standard target file
        table = ascii.read(data.text)

        # We can get duplicte targets from the queries, weed these out by name
        table = unique(table, keys='name')

        # Start by generating a blank table
        targets = blank_target_table()

        # Add targets one by one from
        for row in table:
            coord   = SkyCoord(row['ra'], row['dec'], unit='deg')
            time    = Time(row['obs_date'])
            add_row = [row['name'], coord, 1.0, time, row['Recent mag'], 'SN']
            targets.add_row(add_row)

        return(targets)

    # Can't resolve list so throw print an error and return None
    else:
        error = 'ERROR: could not resolve a target list for telescope={tel}'
        print(error.format(tel=telescope.lower()))
        return(None)
