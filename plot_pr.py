import sys;
from pylab import *

# You can use this program to plot precison/recall curves.

labels = [];
for fn in sys.argv[1:]:
	scores = [[float(y) for y in x.strip().split("\t")] for x in open("Results/%s" % (fn))];
	#Each item in scores is a list: [threshold, prec, rec, F-score]
	curve, = plot([x[2] for x in scores], [x[1] for x in scores], '-');
        best = max(scores,key=lambda x:x[3]); 
	print "Precision, Recall and F-Score at maximum F-Score (", fn, "):";
	print "P:%0.2f\tR:%0.2f\tF:%0.2f" % (best[1],best[2],best[3]);
	col = getp(curve, 'color')
        plot(best[2],best[1], 'x', color = col, markersize=10, markeredgewidth=2);
	labels.append(fn);
        labels.append("F Max: %s" % (fn));

xlabel("Recall");
ylabel("Precision");
legend(labels);
show();
