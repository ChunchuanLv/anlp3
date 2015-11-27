import json;
import sys;
import math;
sys.path.append("jellyfish/");
import jellyfish;

# There are various string similarity metrics included in the jellyfish package
# Run import jellyfish; help(jellyfish) to see what is available;

class Similarity:
	def __init__(self):
		pass;

	# Computes the cosine similarity:
	def cos_sim(self,v0,v1):
		return sum([y*v1[x] for (x,y) in v0.iteritems() if x in v1]);

	# This fucntion returns 1 if there is more than th elements in the intersection of x and y:
	def overlap(self,x,y,th=1):
		print x;
		return int(len(set(x)&set(y)) >= th);

	# Computes the Jaccard Similarity:
	def jaccard(self,x,y):
		print x;
		x = set(x);
		y = set(y);
		return len(x&y)/float(len(x|y)+1e-6); # Slighly smoothed so empty sets return zero
	def extractTF_IDF(self,m,s):
		tfidf = m[s+'_tf_idf']
		keys = m[s+'_VEs']
		result = dict()
		s = 0
		for k in keys:
		    k = k.replace(" ","")
		    if k in tfidf.keys():
		        result[k] = tfidf[k]
		        s = s + result[k]**2
		s = math.sqrt(s)
		for k in result.keys():
		    result[k] = result[k]/s
		return result
        
	# This function takes two mentions and returns a dictonary of similarity features
	# You should define your own mention similarity features and add them to the returned dictonary
	def compute(self,m0,m1,keys = ['DOC_SIM','WIN_SIM','SENT_SIM','OVERLAP']):
		sims = {};
    
		mt_sim = jellyfish.levenshtein_distance(unicode(m0['mention_text']),unicode(m1['mention_text']));
		#return {'MT_SIM': mt_sim};
          #      sims['DOC_SIM'] = self.cos_sim(m0['doc_tf_idf'],m1['doc_tf_idf']);
                sims['WIN_SIM']= self.cos_sim(m0['win_tf_idf'],m1['win_tf_idf']);
            #    sims['SENT_SIM'] = self.cos_sim(m0['sentence_tf_idf'],m1['sentence_tf_idf']);
             #   sims['OVERLAP'] = self.overlap(m0['NER_tags'],m1['NER_tags'],2);
              #  sims['jaccard'] =self.jaccard(m0['win_VEs'],m1['win_VEs'])
             #   sims['overlapVe'] =self.overlap(m0['sentence_VEs'],m1['sentence_VEs'],3)
                sims['win_SIMVe'] =self.cos_sim(self.extractTF_IDF(m0,'win'),self.extractTF_IDF(m1,'win'))
            #    sims['sentence_SIMVe'] =self.cos_sim(self.extractTF_IDF(m0,'sentence'),self.extractTF_IDF(m1,'sentence'))
            #    sims['doc_SIMVe'] =self.cos_sim(self.extractTF_IDF(m0,'doc'),self.extractTF_IDF(m1,'doc'))
		return sims;