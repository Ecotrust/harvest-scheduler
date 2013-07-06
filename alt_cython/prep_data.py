import numpy as np
import os
import csv
import json


def from_random():
    # consistently generate a random set
    np.random.seed(42)
    # 4D: stands, rxs, time periods, variables
    # gaussian distribution; mean of 10, stddev of 1
    stand_data = 3 * np.random.randn(37, 25, 20, 3) + 10
    stand_data = stand_data.astype(float)
    return stand_data


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
    stands = sf.shapes()

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

    """
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
    """
    property_stands = []
    axis_map = {'rx': []}
    for i, record in enumerate(sf.iterRecords()):
        cond = record[field_nums['cond']]
        acres = record[field_nums['acres']]
        stand_rxs = []
        for rx in rxs:
            # assumes variant and siteindex are constant and already weeded out of the csv files
            csv_path = glob.glob(os.path.join(csvdir, "*rx%s_cond%s*" % (rx, cond)))[0]

            if rx == 1:
                # for grow only, offsets are pointless
                available_offsets = ['00']
            else:
                available_offsets = ['00', '01', '02', '03', '04']

            for offset in available_offsets:
                rx_timeperiods = []
                # ugh , open each file 6 times, gross
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
                        except:
                            continue
                        rx_timeperiods.append(vars)

                axis_map['rx'].append((rx, offset))
                stand_rxs.append(rx_timeperiods)

        property_stands.append(stand_rxs)

    arr = np.array(property_stands)

    # caching
    np.save('arr.cache', arr)
    with open('axis_map.cache', 'w') as fh:
        fh.write(json.dumps(axis_map, indent=2))

    return arr, axis_map
