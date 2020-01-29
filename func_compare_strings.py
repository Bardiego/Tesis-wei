# -*- coding: utf-8 -*-
"""
Created on Fri Nov 29 11:17:17 2019

@author: Diego
"""
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import word_tokenize, pos_tag


def SimScore(S1, S2, language):     
    sumSimilarityscores = 0
    scoreCount = 0
    synsets1 = [sin1 for x in S1 for sin1 in wn.synsets(x, lang=language)]
    synsets2 = [sin2 for x in S2 for sin2 in wn.synsets(x, lang=language)]
        
#    print("Synsets1: %s\n" % synsets1)
#    print("Synsets2: %s\n" % synsets2)
    # For each synset in the first sentence...
    for synset1 in synsets1:
     
        synsetScore = 0
        similarityScores = []
     
        # For each synset in the second sentence...
        for synset2 in synsets2:
     
            # Only compare synsets with the same POS tag. Word to word knowledge
            # measures cannot be applied across different POS tags.
            if synset1.pos() == synset2.pos():
#                print('entre')
                # Note below is the call to path_similarity mentioned above. 
                synsetScore = synset1.path_similarity(synset2)
     
                if synsetScore != None:
#                    print("Path Score %0.2f: %s vs. %s" % (synsetScore, synset1, synset2))
                    similarityScores.append(synsetScore)
     
                # If there are no similarity results but the SAME WORD is being
                # compared then it gives a max score of 1.
                elif synset1.name().split(".")[0] == synset2.name().split(".")[0]:
                    synsetScore = 1
#                    print("Path MAX-Score %0.2f: %s vs. %s" % (synsetScore, synset1, synset2))
                    similarityScores.append(synsetScore)
     
                synsetScore = 0
     
        if(len(similarityScores) > 0):
            sumSimilarityscores += max(similarityScores)
            scoreCount += 1
      
    # Average the summed, maximum similarity scored and return.
    if scoreCount > 0:
        avgScores = sumSimilarityscores / scoreCount
      
#    print("Func Score: %0.2f" % avgScores)
        ##esto de abajo por si no encuentra sinonimos 
    else:
        pass
    return(avgScores)
    

    

def SymmetricSimScore(S1, S2, language):
    return (SimScore(S1, S2, language)+SimScore(S2, S1, language)/2)


def Levenshtein(s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
                
        return v1[len(t)]
    
    
def SimCosine(S1, S2, language):
    ##LANGUAGE TIENE QUE SER SPA Y NO SPANISH
    S1_list = word_tokenize(S1)
    S2_list = word_tokenize(S2)
    
    sw = stopwords.words(language)  
    l1 =[];l2 =[] 
      
    # remove stop words from string 
    S1_set = {w for w in S1_list if not w in sw}  
    S2_set = {w for w in S2_list if not w in sw} 
#    print(S1_set)
#    print(S2_set)
    # form a set containing keywords of both strings  
    rvector = S1_set.union(S2_set)  
    for w in rvector: 
        if w in S1_set: l1.append(1) # create a vector 
        else: l1.append(0) 
        if w in S2_set: l2.append(1) 
        else: l2.append(0) 
    c = 0  
#    print(l1)
#    print(l2)
#    print(rvector)
    # cosine formula  
    for i in range(len(rvector)): 
            c+= l1[i]*l2[i] 
    cosine = c / float((sum(l1)*sum(l2))**0.5) 
#    print("similarity: ", cosine)
    return cosine

def RemoveStopWords(S, language):
    ##LANGUAGE DEBE SER SPANISH Y NO SPA
    sw = stopwords.words(language)
    clean_string = [cs for cs in S.split() if not cs in sw]
    return clean_string


def lcsubstring_length(a, b):
    table = {}
    l = 0
    for i, ca in enumerate(a, 1):
        for j, cb in enumerate(b, 1):
            if ca == cb:
                table[i, j] = table.get((i - 1, j - 1), 0) + 1
                if table[i, j] > l:
                    l = table[i, j]
    return l