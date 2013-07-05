import numpy as np
import os
import csv


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
    rxs = range(1,26)

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
    for i, record in enumerate(sf.iterRecords()):
        cond = record[field_nums['cond']]
        stand_rxs = []
        for rx in rxs:
            rx_timeperiods = []
            # assumes variant and siteindex are constant and already weeded out of the csv files
            csv_path = glob.glob(os.path.join(csvdir, "*rx%s_cond%s*" % (rx, cond)))[0]
            fvsdata = csv.DictReader(open(csv_path, 'rb'), delimiter=',', quotechar='"')

            # pandas could help here but trying to reduce dependencies
            for line in fvsdata:
                vars = []
                offset = line['offset']
                # TODO other offsets?
                if offset == "00":
                    try:
                        f = float(line['FIREHZD'])
                        c = float(line['total_stand_carbon'])
                        t = float(line['removed_merch_ft3'])
                        vars.append(f)
                        vars.append(c)
                        vars.append(t)
                    except:
                        continue
                    rx_timeperiods.append(vars)

            stand_rxs.append(rx_timeperiods)

        property_stands.append(stand_rxs)

    arr = np.array(property_stands)
    import ipdb; ipdb.set_trace()
