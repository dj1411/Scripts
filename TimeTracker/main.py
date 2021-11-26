# custom utility functions
def myassert(cond, msg, raise_excep = False) :
    if not cond :
        print( "ERROR: " + msg )
        if raise_excep :
            input("Press <enter> to see details.")
            raise
        else :
            input("Press <enter> to exit...")
            os.abort()

# import modules
try :
    import os
    import configparser
    from datetime import *
    import json
    import prettytable 
except :
    myassert( False, "Could not import some modules. Use \'pip install <module>\' to install them", True )

# import internal modules
from Menu import *

# Globals
config = configparser.ConfigParser()
config.read('config.ini')

# display the current statistics
def show_stats() :
    # read database file
    file = open( config['DEFAULT']['TIMEDB'], 'r' )
    timedb = json.loads( file.read() )
    file.close()

    # print current week data
    table = prettytable.PrettyTable(["Date", "Day", "Work Day", "Duration"])
    # table.add_row( ["22-10-22", "Fri", 1, 34 ] )
    # print(table)
    ( _, curweek, _) = datetime.today().isocalendar()

    # calculate deficit hours
    ndays = 0
    acttd = timedelta(0)
    for entry in timedb :
        # calculate number of working days
        ndays += entry['workday']

        # calculate total
        td = timedelta(0)
        for tim in entry['timestamps'] :
            (h, m, s) = tim['start'].split(":")
            start = datetime.combine(date.today(), time(int(h),int(m),int(s)))
            (h, m, s) = tim['end'].split(":")
            end = datetime.combine(date.today(), time(int(h),int(m),int(s)))
            td += (end - start)
        acttd += td 

        # collect data for current week
        (y, mm, s) = entry['date'].split("-")
        dat = datetime( int(y), int(mm), int(s) )
        ( _, week, _) = dat.isocalendar()
        if week == curweek :
            table.add_row( [ entry['date'], dat.strftime("%a"), entry['workday'], f"{td.seconds/3600:.2f}" ] )

    exphrs = ndays * float( config['DEFAULT']['DAILYEFFORT'] )
    acthrs = acttd.seconds/3600
    defhrs = exphrs - acthrs
    print(table)

def start_timer() :
    # read database file
    file = open( config['DEFAULT']['TIMEDB'], 'r' )
    timedb = json.loads( file.read() )
    file.close()

    # modify contents
    tod = datetime.today().strftime("%Y-%m-%d")
    idx = None
    for i in range( len(timedb) ) :
        if tod == timedb[i]['date'] :
            idx = i
            break
    if idx is None :
        datentry =     {
            "date": tod,
            "workday": 1,
            "timestamps": [],
            "correction" : 0
        }
        idx = len(timedb)
        timedb.append(datentry)
    timentry = {
          "start": datetime.now().strftime("%H:%M:%S"),
          "end": None
        }
    timedb[idx]['timestamps'].append(timentry)
    
    # write back
    file = open( config['DEFAULT']['TIMEDB'], 'w' )
    file.write( json.dumps(timedb, indent=4) )
    file.close()

def stop_timer() :
    # read the file
    file = open( config['DEFAULT']['TIMEDB'], 'r' )
    timedb = json.loads( file.read() )
    file.close()

    # modify contents
    tod = datetime.today().strftime("%Y-%m-%d")
    for i in range( len(timedb) ) :
        if tod == timedb[i]['date'] :
            for j in range( len(timedb[i]['timestamps']) ) :
                if timedb[i]['timestamps'][j]['end'] is None :
                    timedb[i]['timestamps'][j]['end'] = datetime.now().strftime("%H:%M:%S")
                    break
            break
    
    # write back
    file = open( config['DEFAULT']['TIMEDB'], 'w' )
    file.write( json.dumps(timedb, indent=4) )
    file.close()

# main wrapped around to catch any exceptions to keep the console open
def main() :
        show_stats()
        menu = Menu()
        menu.add( MenuItem( "Start Timer", start_timer ) )
        menu.add( MenuItem( "Stop Timer", stop_timer ) )
        while True: menu.show()

if __name__ == "__main__":
    try :
        main()
    except SystemExit :
        pass
    except:
        myassert( False, "An exception has occurred.", True )            
