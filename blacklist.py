from difflib import SequenceMatcher
import string

class Blacklist:
    def __init__(self, wordlist=[]):
        self.letter_set = frozenset(string.ascii_lowercase + string.ascii_uppercase + ' ')
        #self.word_list
        self.setWordList(wordlist)
        
    def checkWord(self, word):
        ### This function takes a word, and checks for similarity to 
        ### entries in the stored word list.
        ### It returns a tuple (hiscore, match) of the
        ### score and word corresponding to the best match in the blacklist.
        ### TODO: One could imagine selectable score algorithms.
        def getScore(inputword, blacklistword):
            m = SequenceMatcher(None,inputword,blacklistword)
            return m.ratio()

        tocheck = self.simplify(word)    
        scores = [getScore(tocheck, blword) for blword in self.word_list]  
        score_dict = dict(zip(scores,self.word_list))
        
        hiscore = sorted(score_dict,reverse=True)[0]
        return (hiscore, score_dict[hiscore])

    def getWordList(self):
        return self.word_list
        
    def setWordList(self, wordlist=[]):
        self.word_list = frozenset([self.simplify(w) for w in wordlist])
        
    def simplify(self, word):
        return filter(self.letter_set.__contains__, word).lower()
