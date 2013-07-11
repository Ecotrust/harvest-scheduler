import numpy as np
import os
import csv
import json


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


def from_files(shp="data/test_stands", csvdir="data/csvs"):
    import shapefile
    import glob
    sf = shapefile.Reader(shp)

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
        if rx == 1:
            # for grow only, offsets are pointless
            available_offsets = ['00']
        else:
            available_offsets = ['00', '01', '02', '03', '04']

        for offset in available_offsets:
            axis_map['mgmt'].append((rx, offset))

    property_stands = []
    valid_mgmts = []
    for i, record in enumerate(sf.iterRecords()):
        cond = record[field_nums['cond']]
        acres = record[field_nums['acres']]
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
            csv_path = glob.glob(os.path.join(csvdir, "*rx%s_cond%s*" % (rx, cond)))[0]

            if rx == 1:
                # for grow only, offsets are pointless
                available_offsets = ['00']
            else:
                available_offsets = ['00', '01', '02', '03', '04']

            for offset in available_offsets:
                mgmt_timeperiods = []
                # ugh , open each file 5 times, gross
                # pandas could help here but trying to reduce dependencies
                fvsdata = csv.DictReader(open(csv_path, 'rb'), delimiter=',', quotechar='"')
                for line in fvsdata:
                    vars = []
                    if offset == line['offset']:
                        try:
                            f = float(line['FIREHZD']) * acres
                            c = float(line['total_stand_carbon']) * acres
                            t = float(line['removed_merch_ft3']) * acres / 1000.0
                            vars.append(c)
                            vars.append(t)
                            vars.append(t)
                            vars.append(f)
                            # TODO: calculate actual cost!
                        except:
                            continue
                        mgmt_timeperiods.append(vars)

                if rx in restricted_rxs:
                    temporary_mgmt_list.append(mgmt_id)
                mgmt_id += 1
                stand_mgmts.append(mgmt_timeperiods)

        valid_mgmts.append(temporary_mgmt_list)
        property_stands.append(stand_mgmts)

    arr = np.array(property_stands)

    # caching
    np.save('cache.array', arr)
    with open('cache.axis_map', 'w') as fh:
        fh.write(json.dumps(axis_map, indent=2))
    with open('cache.valid_mgmts', 'w') as fh:
        fh.write(json.dumps(valid_mgmts, indent=2))

    return arr, axis_map, valid_mgmts
