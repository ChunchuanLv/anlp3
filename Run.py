import sys;
import json;
from pylab import *;
from math import log;
sys.path.append("liblinear-1.93/python/");
from liblinearutil import *;
import random;

from Similarity import Similarity;

# I have written this portion of the code for speed/convenience rather than interperatability
# YOU SHOULD NOT EDIT THIS CODE

# Removing unicode using the method described here: http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
def convert_json(input):
    if isinstance(input, dict):
        return dict([(convert_json(key),convert_json(value)) for (key, value) in input.iteritems()]);
    elif isinstance(input, list):
        return [convert_json(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


# Decide where to store the results:
if(len(sys.argv) != 2):
    print "Using Default output Results/Test";
    out_name = "Test";
else:
    out_name = sys.argv[1];
try:
    loaded
except NameError:
    print "Loading Data";
    mentions = [convert_json(json.loads(x)) for x in open("Data/Mentions.json")];
    mid_mention = dict([(x['mid'],x) for x in mentions]);
    pairs = json.load(open("/afs/inf.ed.ac.uk/group/teaching/anlp/asgn3/Train_Test_Pairs"));
    mid_eid = dict([apply(lambda x,y:(int(x),y),line.strip().split("\t")) for line in open("/afs/inf.ed.ac.uk/group/teaching/anlp/asgn3/mid_eid")]);
    loaded = True;

print "Computing Training Similarities";
s = Similarity();
labels = [];
features = [];
for (mid0,mid1) in pairs['training']:
	labels.append(int(mid_eid[mid0] == mid_eid[mid1]));
	features.append(s.compute(mid_mention[mid0],mid_mention[mid1]));
    #Adding features here!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# A little hack so that first class is always 1:
labels.insert(0,1);
features.insert(0,{});

print "Active Similarities:"
print "\t".join(reduce(lambda x,y:x|y, [set(x.keys()) for x in features]));

print "Training";
# We need to convert string feature names to feature numbers for liblinear:
# Feature numbers need to start from 1
feature_map = dict([(y,x+1) for (x,y) in enumerate(reduce(lambda x,y: x|y,[set(x) for x in features]))]);
mapped_features = [];
for fs in features:
	mapped_features.append(dict([(feature_map[x],y) for (x,y) in fs.iteritems()]));

# Wighting the classes by their proportion. 
label_freq = {0:0,1:0};
for l in labels: label_freq[l]+=1;
w0 = 1.0/label_freq[0];
w1 = 1.0/label_freq[1];

# Train the model:
prob  = problem(labels, mapped_features);
param = parameter('-s 0 -w0 %f -w1 %f' % (w0,w1));
model = train(prob, param);

print "Computing Testing Similarities";
labels = [];
features = [];
for (mid0,mid1) in pairs['testing']:
	labels.append(int(mid_eid[mid0] == mid_eid[mid1]));
	features.append(s.compute(mid_mention[mid0],mid_mention[mid1]));

# Mapping the features to *the same* numbers:
mapped_features = [];
for fs in features:
	mapped_features.append(dict([(feature_map[x],y) for (x,y) in fs.iteritems()]));

(labels_p,accs,pdists) = predict([1]*len(mapped_features), mapped_features, model, '-b 1 -q')
label_score = [];
for (label,(pp,pn)) in zip(labels,pdists):
	label_score.append((label,pp)); # Ranking on P(coreferent)

# I am performing the threshold sweep here:
label_score.sort(key=lambda x:x[1],reverse=True);
th_prf = [];
Nc = 0;
Tc = float(sum(labels));
for (i,(label,score)) in enumerate(label_score):   #every step relax threshold
	Nc += label;                               #positive and correct sofar
	p = Nc/float(i+1);                         #predicted to be correct
	r = Nc/Tc;                                #total correct
	f = 2*p*r/(p+r) if p+r > 0 else 0;       #f score
	th_prf.append((score,p,r,f));

# Write th,p,r,f to disk:
fp = open("Results/%s" % (out_name), 'w');
fp.write("\n".join(["%f\t%f\t%f\t%f" % (th,p,r,f) for (th,p,r,f) in th_prf]));
fp.close();

# Plot precision recall curve:
(th,p,r,f) = max(th_prf,key=lambda x:x[-1]);
print "Precision, Recall and F-Score at maximum F-Score:";
print "P:%0.2f\tR:%0.2f\tF:%0.2f" % (p,r,f);
plot([x[2] for x in th_prf],[x[1] for x in th_prf], 'r-');
plot([r],[p],'kx', markersize=10, markeredgewidth=2);
xlabel("Recall");
ylabel("Precision");
show();
