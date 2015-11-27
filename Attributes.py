import json;
from collections import defaultdict;
from math import log, sqrt;
import string;
# This file will read in a JSON file of documents and convert it to a JSON file of mentions with attributes
# Attributes are properies of the mention in hand that you will use to compute the mention similarity

# NOTE: In this file:
# word means the lexical word plus the meta data
# term means just the lecical word after processing (eg: coveting to lower case)

class Attributes:
	def __init__(self):
		self.stopwords = set([x.strip() for x in open("/afs/inf.ed.ac.uk/group/teaching/anlp/asgn3/stopwords")]); # Load up the list of stopwords 
		self.df = json.load(open("/afs/inf.ed.ac.uk/group/teaching/anlp/asgn3/df.json")); # Load up document frequency counts
		self.N = 18022.0; # Store the amount of documents used for the document freuquency counts
       
    
    # This function converts a list of words to a bag of terms, it takes a list of words, removes all the meta data about the words, removes stop words, punction and lower cases the words:
	def bo_terms(self,words):
		terms = [];
		for word in words:
                        term = filter(lambda x: x in string.printable,word[1].lower()).strip(string.punctuation);
			if(term in self.stopwords): continue;
			if(len(term) <= 3): continue;
			if(word[3] in set(["TIME","NUMBER"])): continue;
			terms.append(term);
		return terms;

    # This function takes a list of words, converts them to a bag of terms and tf-idf weights them
	def tf_idf(self,words):
		tf = defaultdict(int);
		for t in self.bo_terms(words): tf[t]+=1; # Perform tf counting over the bag of terms
        
		tf_idf = [(x,log(y+1)*log((self.N-self.df[x]+0.5)/float(self.df[x]+0.5))) for (x,y) in tf.iteritems()]; # TF-IDF weighting.
		tf_idf = [(x,y) for (x,y) in tf_idf if y > 0]; # Strip terms that occur in more than half of the documents.
		n = sqrt(sum([pow(y,2) for (x,y) in tf_idf]));
		tf_idf = dict([(x,y/n) for (x,y) in tf_idf]);
		return tf_idf;

    # Take a mention text and convert it to a bag of terms:
	def pp_mention(self,mt):
		return [("",x,"","PERSON") for x in mt.lower().split(" ")];

    # Extract the named entity mentions from a list of words:
	def extract_NEs(self,words):
		mentions = [[]];
		types = [];
		for word in words:
			if(word[3] == "O") & (len(mentions[-1]) == 0): continue;
			if(word[3] == "O") & (len(mentions[-1]) > 0): mentions.append([]);
			if(word[3] != "O") & (len(mentions[-1]) > 0): mentions[-1].append(word[1]);
			if(word[3] != "O") & (len(mentions[-1]) == 0):
				mentions[-1].append(word[1]);
				types.append(word[3]);
		NEs = [];
		for (m,t) in zip(mentions,types):
			if(t in set(["PERSON", "LOCATION", "MISC", "ORGANIZATION"])): NEs.append(" ".join(m));
		return NEs;
    
        # Extract the named entity mentions from a list of words:
	def extract_VEs(self,words):
		VEs = [];
		for word in words:
			if(word[2][0]==u'V'): VEs.append(" ".join(word[1]))
		return VEs;
    
    # Converts a list of named entity mentions to a bag of terms:
	def ne_words(self,NEs):
		words = [];
		for ne in NEs:
			words.extend(ne.split(" "));
		return list(set(self.bo_terms([["",x,"","NE"] for x in  words])));

    # Return all words in the document:
	def doc_words(self,text):
		return reduce(lambda x,y: x+y,text);

    # Find all words within win of the mention m:
	def window_words(self,m,text,win):
		m_begin = (m['location'][0],m['location'][1]);
		m_end = (m['location'][0],m['location'][2]);
		pos = 0;
		start_pos = 0;
		end_pos = 0;
		for s in range(len(text)):
			for i in range(len(text[s])):
				if((s,i) == m_begin): start_pos = pos;
				if((s,i) == m_end): end_pos = pos;
				pos += 1;

		words = self.doc_words(text);
		start_pos = start_pos-win;
		if(start_pos < 0): start_pos = 0;

		end_pos = end_pos+win;
		if(end_pos > len(words)): end_pos = len(words);
		return words[start_pos:end_pos];

    # Find all words in sentences that mention the entity in m using the predicted within document coreference chains:
	def sentence_words(self,m,coref,text):
		sentences = set();
		sentences.add(m['location'][0]);
		if(m['coref_id'] >=0):
			sentences |= set([x[0] for x in coref[m['coref_id']]]);
		sentence_text = [];
		for s in sentences: sentence_text.extend(text[s]);
		return sentence_text;

    # Extract all the mention texts used to refer to the entity using the predicted coreference chains:
	def mention_terms(self,m,coref):
		mention_words = [("",x.strip(string.punctuation),"","PERSON") for x in m['mention_text'].lower().split(" ")]
		if(m['coref_id'] > 0):
			mention_words.extend([["", x, "", "PERSON",] for x in reduce(lambda x,y:x+y,[x[4].split(" ") for x in coref[m['coref_id']]])]);
		return self.bo_terms(mention_words);
	

    # This function takes a document, the predicted coreference chains and a list of mentions
    # It extracts various attributes about each mention which may be useful for similarity computation.
	def createNERs(self,m,text):
		location = m['location']
		sindex = location[0]
		begin_index = location[1]
		end_index = location[2]
		tags = []
		allInformations = text[sindex]
		for i in range(begin_index,end_index):
		    if allInformations[i][3] != '0':
		        tags.append(allInformations[i][3])
		return tags    # This function takes a document, the predicted coreference chains and a list of mentions
    # It extracts various attributes about each mention which may be useful for similarity computation.
	def createVERs(self,m,text):
		location = m['location']
		sindex = location[0]
		begin_index = location[1]
		end_index = location[2]
		tags = []
		allInformations = text[sindex]
		for i in range(begin_index,end_index):
		    if allInformations[i][2] != '0':
		        tags.append(allInformations[i][2])
		return tags
	def process(self,doc):
		text = doc['text'];
		coref = doc['coref'];
		doc_words = self.doc_words(text); # extract all the words in the document
		doc_tf_idf = self.tf_idf(doc_words); # Convert the words to a bag of terms and tf-idf weight them  
	
		mention_attributes = []; # DO NOT MODIFY!
		for m in doc['mentions']:
			mention_words = self.pp_mention(m['mention_text']); # Convert the mention text to words
			win_words = self.window_words(m,text,55); # Find words within a window of 55 words of the mention text
			sentence_words = self.sentence_words(m,coref,text); # Extract words in sentences that mention the entity (using the predicted within document coference chains)
	
			attributes = {}; # Define a dictionary we will store the mentions in. 
			attributes['mention_text'] = m['mention_text']; # Lets use the mention text as an attribute, we may want to compute the edit distance between two mentions as a similarity feature.
			attributes['mention_tf_idf'] = self.tf_idf(mention_words); # The tf-idf weighted mention text terms may also be useful (we can them compute similarity with cosine similarity)
           
            # We should extract the list of entities mentioned as they may be useful for computing similarity
			attributes['doc_NEs'] = self.extract_NEs(doc_words); # Extract the named entities mentioned in the document
			attributes['win_NEs'] = self.extract_NEs(win_words); # Extract the named entities mentioned near the mention
			attributes['sentence_NEs'] = self.extract_NEs(sentence_words); # Extract the named entity mentions from the sentences that mention the entity.
			attributes['doc_VEs'] = self.extract_VEs(doc_words); # Extract the named entities mentioned in the document
			attributes['win_VEs'] = self.extract_VEs(win_words); # Extract the named entities mentioned near the mention
			attributes['sentence_VEs'] = self.extract_VEs(sentence_words); # Extract the named entity mentions from the sentences that mention the entity.
            
	        # Instead, we may also want to treat these named entity mentions as just bags of words
			attributes['doc_NE_terms'] = self.ne_words(attributes['doc_NEs']);
			attributes['win_NE_terms'] = self.ne_words(attributes['win_NEs']);
			attributes['sentence_NE_terms'] = self.ne_words(attributes['sentence_NEs']);
            
			attributes['NER_tags'] = self.createNERs(m,text);
			attributes['VER_tags'] = self.createVERs(m,text);
	        # The tf-idf weighted document, window and sentences may also be useful
			attributes['doc_tf_idf'] = doc_tf_idf;
			attributes['win_tf_idf'] = self.tf_idf(win_words);
			attributes['sentence_tf_idf'] = self.tf_idf(sentence_words);

			attributes['mention_terms'] = self.mention_terms(m,coref);

    		# Leave the Following lines unchanged! Changing them WILL cause things to stop working.
			attributes['mid'] = m['mid']; # DO NOT MODIFY
			mention_attributes.append(attributes); # DO NOT MODIFY
		return mention_attributes; # DO NOT MODIFY

# You can ignore all the following code, it just loads up the documents and processes them:
attr = Attributes();

fp_in = open("/afs/inf.ed.ac.uk/group/teaching/anlp/asgn3/Docs.json");
fp_out = open("Data/Mentions.json", 'w');
for (i,line) in enumerate(fp_in):
	print "%i/18022\r" % (i),;
	if(line == "\n"): continue;
	doc = json.loads(line);
	for m in attr.process(doc):
		fp_out.write("%s\n" 
                     % (json.dumps(m)));
fp_out.close();
print "";
