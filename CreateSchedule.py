import Constants
from Observatory import Observatory
from Telescope import Swope, Nickel, Thacher, Keck
from Utilities import *
from Target import TargetType, Target

from dateutil.parser import parse
import argparse, warnings
from astropy.coordinates import SkyCoord
from astropy import units as unit
from astropy.time import Time
warnings.filterwarnings('ignore')

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
        help="CSV file with targets to schedule.")
    parser.add_argument("-d", "--date",
        help="YYYYMMDD formatted observation date.")
    parser.add_argument("-ot", "--obstele",
        help="Comma-delimited list of <Observatory>:<Telescope>.")
    parser.add_argument("-pp", "--plot",
        help="Preview the plot during command line execution.",
        action='store_true')
    parser.add_argument("-a", "--now",
        help="Start Now -- True or False")
    parser.add_argument("-b", "--start",
        help="Desired Start Time in the format of HHMM")
    parser.add_argument("-c", "--end",
        help="Desired End Time in the format of HHMM")
    args = parser.parse_args()

    file_name = args.file
    obs_date = args.date
    observatory_telescopes = args.obstele.split(",")
    preview_plot = args.plot

    obs_keys = [o.split(":")[0] for o in observatory_telescopes]
    tele_keys = [t.split(":")[1] for t in observatory_telescopes]

    startNow = args.now in ['True']
    startTime = args.start
    endTime = args.end


    lco = Observatory(
        name="LCO",
        lon="-70.6915",
        lat="-29.0182",
        elevation=2402,
        horizon="-12",
        telescopes={"Swope":Swope()},
        obs_date_str=obs_date,
        # Chile observes Chile Standard Time (CLT) from 5/13/2017 - 8/12/2017 => UTC-4
        utc_offset=lco_clt_utc_offset,
        utc_offset_name="CLST",
        startNow=startNow,
        start=startTime,
        end=endTime
    )

    lick = Observatory(
        name="Lick",
        lon="-121.6429",
        lat="37.3414",
        elevation=1283,
        horizon="-12",
        telescopes={"Nickel":Nickel()},
        obs_date_str=obs_date,
        # California observes Pacific Daylight Time (PDT) from 3/12/2017 - 11/5/2017 => UTC-7
        utc_offset=lick_pdt_utc_offset,
        # utc_offset=lick_pst_utc_offset, # California observes Pacific Standard Time (PST) from 1/1/2017 - 3/12/2017 => UTC-8
        utc_offset_name="PST",
        startNow=startNow,
        start=startTime,
        end=endTime
    )

    thacher = Observatory(
        name="Thacher",
        lon="-121.6431",
        lat="34.46479",
        elevation=630.0,
        horizon="-12",
        telescopes={"Thacher":Thacher()},
        obs_date_str=obs_date,
        # California observes Pacific Daylight Time (PDT) from 3/12/2017 - 11/5/2017 => UTC-7
        utc_offset=lick_pdt_utc_offset,
        utc_offset_name="PST",
        startNow=startNow,
        start=startTime,
        end=endTime
    )

    keck = Observatory(
        name="Keck",
        lon="-155.4747",
        lat="19.826",
        elevation=4159.58,
        horizon="-12",
        telescopes={"Keck":Keck()},
        obs_date_str=obs_date,
        # California observes Pacific Daylight Time (PDT) from 3/12/2017 - 11/5/2017 => UTC-7
        utc_offset=keck_offset,
        utc_offset_name="Hawaii",
        startNow=startNow,
        start=startTime,
        end=endTime
    )

    observatories = {"LCO":lco, "Lick":lick,"Thacher":thacher, "Keck":keck }

    # If a target list is provided via the file name then use it
    if file_name is not None:
        target_data = get_targets("%s" % file_name)
    # Otherwise download a target list from YSE PZ
    else:
        message = '\n\nDownloading target list for {tel}...\n\n'
        print(message.format(tel=tele_keys[0]))
        target_data = download_targets(tele_keys[0])

    # Check that we got some target data
    if target_data is None:
        error = 'ERROR: could not load or download any target data!'
        print(error)
        sys.exit(1)

    for i in range(len(observatory_telescopes)):

        targets = []
        obs = observatories[obs_keys[i]]

        for target in target_data:

            target_type = None
            disc_date = None

            if target['type'] == 'STD':
                target_type = TargetType.Standard
                disc_date = None
            elif target['type'] == 'TMP':
                target_type = TargetType.Template
            elif target['type'] == 'SN':
                target_type = TargetType.Supernova
            else:
                raise ValueError('Unrecognized target type!')

            targets.append(
                Target(
                    name=target['name'],
                    coord=target['coord'],
                    priority=target['priority'],
                    target_type=target_type,
                    observatory_lat=obs.ephemeris.lat,
                    sidereal_radian_array=obs.sidereal_radian_array,
                    disc_date=target['date'],
                    apparent_mag=target['mag'],
                    obs_date=Time(obs.obs_date)
                )
            )

            obs.telescopes[tele_keys[i]].set_targets(targets)

        print("# of %s targets: %s" % (tele_keys[i], len(targets)))
        print("First %s target: %s" % (tele_keys[i], targets[0].name))
        print("Last %s target: %s" % (tele_keys[i], targets[-1].name))

        obs.schedule_targets(tele_keys[i], preview_plot)

    if preview_plot:
        exit = input("\n\nENTER to exit")

if __name__ == "__main__": main()

