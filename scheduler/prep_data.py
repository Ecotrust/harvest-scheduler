import numpy as np
import os
import csv
import json
import math


def from_random():
    # consistently generate a random set
    np.random.seed(42)
    # 4D: stands, mgmts, time periods, variables
    # gaussian distribution; mean of 10, stddev of 3
    stand_data = 3 * np.random.randn(37, 121, 20, 4) + 10
    stand_data = stand_data.astype(int)
    axis_map = {'mgmt': [(x, '00') for x in range(stand_data.shape[1])]}
    valid_mgmts = [[] for x in range(stand_data.shape[0])]

    return stand_data, axis_map, valid_mgmts


def from_demo():
    stand_data = np.array(
        [  # list of stands
            [  # list of rxs
                [  # list of time periods
                    [12, 6, 5],  # <-- list of variable values
                    [12, 0, 6],
                    [3, 7, 4],
                ],
                [
                    [11, 2, 2],
                    [2, 1, 6],
                    [10, 9, 3],
                ],
            ],
            [   # stand 2
                [   # rx 1
                    [12, 6, 5],  # time period 1
                    [1, 0, 6],
                    [1, 7, 4],
                ],
                [   # rx 2
                    [11, 2, 2],
                    [3, 1, 6],
                    [9, 9, 3],
                ],
            ],
        ]
    )
    return stand_data


def get_offsets(rx):
    if rx == 1:
        # for grow only, offsets are pointless
        available_offsets = [0]
    else:
        available_offsets = [0, 1, 2, 3, 4]

    return available_offsets


def bbox_center(bbox):
    x = (bbox[0] + bbox[2])/2.0
    y = (bbox[1] + bbox[3])/2.0
    return x, y


def mercator_to_lonlat(pt):
        "Converts XY point from Spherical Mercator EPSG:900913 to lat/lon in WGS84 Datum"
        originShift = 2 * math.pi * 6378137 / 2.0  # 20037508.342789244
        lon = (pt[0] / originShift) * 180.0
        lat = (pt[1] / originShift) * 180.0

        lat = 180 / math.pi * (2 * math.atan(math.exp(
                                             lat * math.pi / 180.0)) - math.pi / 2.0)
        return lon, lat


def from_shp_csv(shp="data/test_stands2", csvdir="data/csvs2", cache=True):
    try:
        stand_data = np.load('cache.array.npy')
        axis_map = json.loads(open('cache.axis_map').read())
        valid_mgmts = json.loads(open('cache.valid_mgmts').read())
        print "Using cached data to reduce calculation time..."
        return stand_data, axis_map, valid_mgmts
    except:
        pass  # calculate it

    import shapefile
    import glob
    from forestcost import main_model
    from forestcost import routing
    from forestcost import landing

    sf = shapefile.Reader(shp)

    shapes = sf.shapes()

    rxs = range(1, 26)
    #rxs = range(1, 3)

    field_nums = {
        'acres': None,
        'name': None,
        'cond': None,
        'rx': None,
    }
    for a, b in enumerate(sf.fields):
        if b[0] == 'ACRES':
            field_nums['acres'] = a - 1
        if b[0] == 'name':
            field_nums['name'] = a - 1
        if b[0] == 'cond':
            field_nums['cond'] = a - 1
        if b[0] == 'rx':
            field_nums['rx'] = a - 1
        if b[0] == 'SLOPE_MEAN':
            field_nums['slope'] = a - 1
        if b[0] == 'ELEV_MEAN':
            field_nums['elev'] = a - 1

    assert None not in field_nums.values()

    # populate axis map
    axis_map = {'mgmt': []}
    for rx in rxs:
        for offset in get_offsets(rx):
            axis_map['mgmt'].append((rx, offset))

    property_stands = []
    valid_mgmts = []

    fvsdata = {}

    # Landing Coordinates
    # Assumes original shapefile in mercator
    centroid_coords = mercator_to_lonlat(bbox_center(sf.bbox))
    landing_coords = landing.landing(centroid_coords=centroid_coords)
    haulDist, haulTime, coord_mill = routing.routing(
        landing_coords, mill_shp='/usr/local/apps/land_owner_tools/lot/fixtures/mills/mills.shp'  # TODO
    )

    for i, record in enumerate(sf.iterRecords()):
        print "Reading shape %d" % i

        cond = record[field_nums['cond']]
        acres = record[field_nums['acres']]
        slope = record[field_nums['slope']]
        elev = record[field_nums['elev']]
        raw_restricted_rxs = record[field_nums['rx']]
        try:
            restricted_rxs = [int(x) for x in raw_restricted_rxs.split(",")]
        except ValueError:
            restricted_rxs = []
        temporary_mgmt_list = []
        mgmt_id = 0

        stand_mgmts = []

        for rx in rxs:
            # assumes variant and siteindex are constant and already weeded out of the csv files
            # assumes csvs rows are sorted by year
            csv_path = glob.glob(os.path.join(csvdir, "varPN_rx%s_cond%s*.csv" % (rx, cond)))[0]
            if (rx, cond) not in fvsdata.keys():
                # print "reading (%s, %s)" % (rx, cond)
                reader = csv.DictReader(open(csv_path, 'rb'), delimiter=',', quotechar='"')
                fvsdata[(rx, cond)] = list(reader)

            lines = fvsdata[(rx, cond)]

            for offset in get_offsets(rx):
                mgmt_timeperiods = []
                for line in lines:
                    vars = []
                    if offset == int(line['offset']):
                        try:
                            carbon = float(line['total_stand_carbon']) * acres
                            timber = float(line['removed_merch_ft3']) * acres / 1000.0  # mbf
                            owl = float(line['NSONEST']) * acres
                        except ValueError:
                            continue
                        vars.append(carbon)
                        vars.append(timber)
                        vars.append(owl)

                        ###################################################################
                        # Calculate actual cost

                        poly = shapes[i]
                        # TODO assert poly is single part
                        wkt = "POLYGON((%s))" % (",".join(["%f %f" % (x, y) for (x, y) in poly.points]))

                        try:
                            cut_type = line['CUT_TYPE']
                            cut_type = int(float(cut_type))
                        except ValueError:
                            # no harvest so don't attempt to calculate
                            cut_type = 0

                        # PartialCut(clear cut = 0, partial cut = 1)
                        PartialCut = None
                        if cut_type == 3:
                            PartialCut = 0
                        elif cut_type in [1, 2]:
                            PartialCut = 1

                        #print cond, line['year'], rx, offset, "Cut type", cut_type, "PartialCut", PartialCut

                        if PartialCut is not None:
                            cost_args = (
                                # stand info
                                acres, elev, slope, wkt,
                                # harvest info
                                float(line['CH_TPA']), float(line['CH_CF']),
                                float(line['SM_TPA']), float(line['SM_CF']),
                                float(line['LG_TPA']), float(line['LG_CF']),
                                float(line['CH_HW']), float(line['SM_HW']), float(line['LG_HW']),
                                PartialCut,
                                # routing info
                                landing_coords, haulDist, haulTime, coord_mill
                            )

                            if sum(cost_args[4:10]) == 0:
                                #print "No chip, small or log trees but cut indicated ... how did we get here?"
                                #print cond, line['year'], rx, offset, "Cut type", cut_type, "PartialCut", PartialCut
                                vars.append(0.0)
                            else:
                                try:
                                    result = main_model.cost_func(*cost_args)
                                    #print "Cost model run successfully"
                                    cost = result['total_cost']
                                    vars.append(cost)
                                except ZeroDivisionError:
                                    print "\nZeroDivisionError:\n"
                                    print cost_args
                                    print "--------------"
                                    vars.append(0.0)
                        else:
                            # No cut == no cost
                            # print "No cut, no cost"
                            vars.append(0.0)

                        ###################################################################

                        assert len(vars) == 4
                        mgmt_timeperiods.append(vars)

                if rx in restricted_rxs:
                    temporary_mgmt_list.append(mgmt_id)
                mgmt_id += 1
                assert len(mgmt_timeperiods) > 0
                stand_mgmts.append(mgmt_timeperiods)

        valid_mgmts.append(temporary_mgmt_list)
        property_stands.append(stand_mgmts)

    arr = np.array(property_stands)

    # fill in NaN costs with max possible cost
    maxcost = np.nanmax(arr)
    print "Filling in NaN costs with the max cost of %d" % (maxcost,)
    arr[np.isnan(arr)] = maxcost
    #assert np.isnan(arr).max() is False

    # caching
    np.save('cache.array', arr)
    with open('cache.axis_map', 'w') as fh:
        fh.write(json.dumps(axis_map, indent=2))
    with open('cache.valid_mgmts', 'w') as fh:
        fh.write(json.dumps(valid_mgmts, indent=2))

    return arr, axis_map, valid_mgmts


def from_shp_sqlite(shp="data/test_stands2", db="data/data.db"):
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    NOT READY YET
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    Uses shapefile and sqlitedb as created by
    https://github.com/Ecotrust/growth-yield-batch/blob/master/scripts/csvs_to_sqlite.py
    """
    import shapefile
    import glob
    import sqlite3

    sf = shapefile.Reader(shp)

    con = sqlite3.connect(db)
    cur = con.cursor()

    # TODO
    rxs = range(1, 26)

    field_nums = {
        'acres': None,
        'name': None,
        'cond': None,
        'rx': None,
    }
    for a, b in enumerate(sf.fields):
        if b[0] == 'ACRES':
            field_nums['acres'] = a - 1
        if b[0] == 'name':
            field_nums['name'] = a - 1
        if b[0] == 'cond':
            field_nums['cond'] = a - 1
        if b[0] == 'rx':
            field_nums['rx'] = a - 1

    assert None not in field_nums.values()

    # populate axis map
    axis_map = {'mgmt': []}
    for rx in rxs:
        available_offsets = get_offsets(rx)
        for offset in available_offsets:
            axis_map['mgmt'].append((rx, offset))

    # First pass, get unique conds
    unique_conds = []
    for i, record in enumerate(sf.iterRecords()):
        cond = record[field_nums['cond']]
        if cond not in unique_conds:
            unique_conds.append(cond)

    sql = """
        SELECT cond, rx, offset, year, firehzd, total_stand_carbon, removed_merch_ft3
        FROM trees_fvsaggregate
        WHERE cond IN (%s)
        AND var = 'PN'
    """ % (",".join([str(x) for x in unique_conds]))
    rs = cur.execute(sql)
    results = rs.fetchall()
