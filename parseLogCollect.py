#!/usr/bin/env python -u
import os, sys
import subprocess
import pprint
from optparse import OptionParser
from xml.dom import minidom
from math import sqrt

def main():
    """
    Provide a logCollect tarball as input
    """
    usage = "Usage: %prog -l logCollect"
    parser = OptionParser(usage = usage)
    parser.add_option('-l', '--logCollet', help = 'Tarball for the logCollect jobs', dest = 'logCol')
    (options, args) = parser.parse_args()
    if not options.logCol:
        parser.error('You must provide a logCollect tarball')
        sys.exit(1)

    command = ["tar", "xvf", options.logCol]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    tarballs = out.split()

    readMetrics = ["Timing-file-read-maxMsecs","Timing-tstoragefile-read-maxMsecs","Timing-tstoragefile-readActual-maxMsecs",
                   "Timing-file-read-numOperations","Timing-tstoragefile-read-numOperations","Timing-tstoragefile-readActual-numOperations",
                   "Timing-file-read-totalMegabytes","Timing-tstoragefile-read-totalMegabytes","Timing-tstoragefile-readActual-totalMegabytes",
                   "Timing-file-read-totalMsecs","Timing-tstoragefile-read-totalMsecs","Timing-tstoragefile-readActual-totalMsecs"]

    writeMetrics = ["Timing-file-write-maxMsecs","Timing-tstoragefile-write-maxMsecs","Timing-tstoragefile-writeActual-maxMsecs",
                   "Timing-file-write-numOperations","Timing-tstoragefile-write-numOperations","Timing-tstoragefile-writeActual-numOperations",
                   "Timing-file-write-totalMegabytes","Timing-tstoragefile-write-totalMegabytes","Timing-tstoragefile-writeActual-totalMegabytes",
                   "Timing-file-write-totalMsecs","Timing-tstoragefile-write-totalMsecs","Timing-tstoragefile-writeActual-totalMsecs"]

    total = {}
    for i, file in enumerate(tarballs):
        subcommand = ["tar", "-x", "cmsRun1/FrameworkJobReport.xml", "-zvf", file]

        # making this call quiet, so /dev/null
        subprocess.call(subcommand, stdout=open(os.devnull, 'wb'))
        xmldoc = minidom.parse("cmsRun1/FrameworkJobReport.xml")
        items = ( (item.getAttribute('Name'),item.getAttribute('Value')) for item in xmldoc.getElementsByTagName('Metric') )
        matched = [item for item in items if item[0] in readMetrics or item[0] in writeMetrics ]
        #matched = [item for item in items if item[0] in readMetrics ]
        for ele in matched:
            if not i:
                total[ele[0]] = [float(ele[1])]
            else:
                total[ele[0]].append(float(ele[1]))
#    print "Number of logArchives: %d" % i
#    pprint.pprint(total)

    # Calculates average, standard deviation (old way, no numpy available) and
    # finds the maximum and minimum values
    results = {}
    for k, v in total.iteritems():
        results[k] = {}
        results[k]['avg'] = float(sum(v))/len(v)
        results[k]['std'] = 0
        results[k]['min'] = v[0]
        results[k]['max'] = v[0]
        for i in v:
            results[k]['std'] += (results[k]['avg'] - i) ** 2
            results[k]['max'] = i if (i > results[k]['max']) else results[k]['max']
            results[k]['min'] = i if (i < results[k]['min']) else results[k]['min']
        results[k]['std'] = "%.3f" % sqrt(float(results[k]['std']/len(v)))

        # Rounding in 3 digits to be nicely viewed
        results[k]['avg'] = "%.3f" % results[k]['avg']
        results[k]['max'] = "%.3f" % results[k]['max']
        results[k]['min'] = "%.3f" % results[k]['min']
        print "%-47s : %s" % (k, results[k])

    sys.exit(0)

if __name__ == "__main__":
        main()