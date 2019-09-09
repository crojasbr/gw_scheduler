# gw_scheduler
GW Scheduler based on Dave Coulter's SN scheduler

Some dependencies needed: 

pip install ephem

Usage: (python 3)


python master.py --tiles_file example_tiles.txt --date 20190802 --telescope Swope 

Options include: --start HHMM --end HHMM or --now True (UT times); --asap (observe high-priority targets first)

Telescope options: Swope, Thacher, Nickel

Note: exposure times, bands, etc, can be changed in the Telescopes.py file
