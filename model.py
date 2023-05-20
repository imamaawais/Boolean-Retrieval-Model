#libraries and utilities
#tokenization
import nltk
from nltk.tokenize import word_tokenize

import re #remove special characters

#stemming
from nltk.stem import PorterStemmer

#dictionary DS for indexing
from collections import defaultdict

#stop words
file = open('Stopword-List.txt','r')
stopWords = file.read() #read and store stop word list
file.close()

#saving inverted index
import json

#to view posting lists better
import pprint

#to get execution time
import time

#GUI
import tkinter as tk

####################################################################################
#preprocessing
####################################################################################


def stemmer(tokens):
    #make object
    stemmer = PorterStemmer()
    #stem words
    stemTokens = [stemmer.stem(token) for token in tokens]

    return stemTokens


#remove stop words
def removeStopWords(tokens):
    #create an empty list to store filtered tokens
    filTokens = []
    
    for token in tokens:
        if token not in stopWords:
            filTokens.append(token)

    return filTokens
    
def caseFolding(tokens):
    cfTokens = [token.lower() for token in tokens]
    return cfTokens

#remove special characters
def removeChar(tokens):

    #consider only alphabets in english
    pattern = re.compile('[^a-zA-Z]')
    #create empty list to store cleaned tokens
    newTokens = [] 

    #iterate through list
    for token in tokens:
        newToken = pattern.sub('', token) #clean the string
        newTokens.append(newToken) #append to the new  cleaned tokens list

    return newTokens

#extracting features
def tokenizer(content):

    #tokenize using nltk
    content = content.replace("-",' ').replace(';',' ')
    tokens = word_tokenize(content)
    #newtokens = word_tokenize(content)
    
    #return the tokens
    return tokens
    

#Reading documents
def readDoc(docNo):
    
    #create a list that contains the content of the file
    
    file = open('Dataset/'+str(docNo)+'.txt','r')
    #read content of file
    content = file.read()
    #close file
    file.close()
    #return the obtained contents of the files
    return content
        
def normalization(contents):
    
    #tokenize the content of the file
    tokens = tokenizer(contents)
    #print(tokens)
    #remove the special characters
    clean = removeChar(tokens)
    #print(clean)
    #print(len(clean))
    #change all terms to lowercase
    caseFolded = caseFolding(clean)
    #print(caseFolded)
    #filter the terms to remove stop words
    filtered = removeStopWords(caseFolded)
    #print(filtered)
    stemmed = stemmer(filtered)
    #return the final tokens
    return stemmed

####################################################################################
#inverted index
####################################################################################

#create a dictionary using default dict globally
invInd = defaultdict(lambda: {'df':0, 'postings': []})

def populateInvIndex(docNo, tokens):
    
    #for each term in the tokens list
    for term in tokens:
        #if term already in inv index 
        if term in invInd.keys():
            #check if it occured in the same document already
            if docNo not in invInd[term]['postings']:
                #add the docNo to its postings if it didnt
                invInd[term]['postings'].append(docNo)
                invInd[term]['df'] +=1
                #if it did, then do nothing
        #if the term is not in inverted index, add it
        else:
            invInd[term]['postings'].append(docNo)
            invInd[term]['df'] +=1

   
def saveInvIndex(index): #need parameter because sorted is in another variable
    with open("invertedIndex.json", "w") as file:
        json.dump(index, file)

def loadInvIndex():
    with open("invertedIndex.json", "r") as file:
        LoadedInvInd = json.load(file)
        return LoadedInvInd


def sortInvIndex(index):
    #sort index
    sortedInd = {term: invInd[term] for term in sorted(index)}
    #print(sortedInd)
    return sortedInd

####################################################################################
#positional index
####################################################################################
#create a dictionary using default dict globally
posInd = defaultdict(lambda: {'df':0, 'postings': []})

def populatePosIndex(docNo, tokens):
    #for each term in the tokens list
    for position, term in enumerate(tokens): #use enumerate to find relative positions
        #if term already in pos index 
        if term in posInd.keys():
            #check if it occurred in the same document already
            if docNo not in [p['docNo'] for p in posInd[term]['postings']]:
                #add the docNo to its postings if it didn't
                posInd[term]['postings'].append({'docNo': docNo, 'position': [position]})
                posInd[term]['df'] += 1
            else:
                #if it did occur in the same document, update the posting
                for posting in posInd[term]['postings']:
                    if posting['docNo'] == docNo:
                        posting['position'].append(position)
        else:
            #if the term is not in inverted index, add it
            posInd[term]['postings'].append({'docNo': docNo, 'position': [position]})
            posInd[term]['df'] += 1


def savePosIndex(index): #need parameter because sorted is in another variable
    with open("positionalIndex.json", "w") as file:
        json.dump(index, file)

def loadPosIndex():
    with open("positionalIndex.json", "r") as file:
        LoadedPosInd = json.load(file)
        return LoadedPosInd

def sortPosIndex(index):
    #sort index
    sortedInd = {term: posInd[term] for term in sorted(index)}
    #print(sortedInd)
    return sortedInd


####################################################################################
#indexing
####################################################################################
def indexer():
    #iterate over all 30 docs
    for docNo in range (1,31,1):
        #read the doc
        contents = readDoc(docNo)
        #tokenize and normalize the contents
        finalTokens = normalization(contents)

        #populate inverted index
        populateInvIndex(docNo, finalTokens)
        #sort the inverted index
        populatePosIndex(docNo,finalTokens)
    
    sortedInv = sortInvIndex(invInd) #this is saved globally
    #save the index to disk 
    #print(sortedInv)
    saveInvIndex(sortedInv)
    
    #pprint.pprint(sortedInv)
    #sort pos index
    sortedPos = sortPosIndex(posInd)
    #save pos index
    savePosIndex(sortedPos)


####################################################################################
#Boolean Query Processing
####################################################################################


def invQuery(qTokens):

    #convert tokens into a string
    query = ' '.join(qTokens)
    #add space between the terms and bracket
    query = query.replace('(', ' ( ')
    query = query.replace(')', ' ) ')
    #set precedence for each operator
    precedence = {'not': 3, 'and': 2, 'or': 1, '(': 0, ')': 0}
    #make empty list to store ops
    operator = []
    #make empty list to store terms
    terms = []

    for term in query.split():
        #if it is a term, append to terms
        if term not in precedence:
            terms.append(term)
        #if opening bracket,then append in operator
        elif term == '(':
            operator.append(term)
        #if closing bracket found
        elif term == ')': #shows ending
            #pop closing bracket
            top = operator.pop() 
            #pop every operator until open bracket is found
            while top != '(':
                terms.append(top)
                top = operator.pop()
        
        else:
            while operator and precedence[term] <= precedence[operator[-1]]:
                terms.append(operator.pop())
            operator.append(term)
    
    #pop every operator
    while operator:
        terms.append(operator.pop())

    return terms
        

def calcPostfix(expression):
    
    stem = PorterStemmer()

    #make empty result list
    result = []
    #iterate over terms in expression
    for term in expression:
        #if term is and, intersect top two lists
        if term == 'and':
            #pop top two lists
            if len(result) !=0:
                list1 = result.pop()
            else:
                list1 = []
            if len(result) !=0:
                list2 = result.pop()
            else:
                list2 = []
            #if len(list2) > len(list1): list1, list2 = list2, list1
            #call the and query function
            result.append(andQuery(list1,list2))
        #if the term is or, union the two lists
        elif term == 'or':
            #pop top two lists
           
            if len(result) !=0:
                list1 = result.pop()
            else:
                list1 = []
            if len(result) !=0:
                list2 = result.pop()
            else:
                list2 = []
            #call the or query function
            result.append(orQuery(list1,list2))
        #if the term is not, call not on it
        elif term == 'not':
            #pop top of the stack
            if len(result) !=0:
                list1 = result.pop()
            else:
                list1 = []
            result.append(notQuery(list1))
        #if term is not operator, keep adding to stack
        else:
            stemmed = stem.stem(term)
            loadedInvIndex = loadInvIndex()
            if stemmed in loadedInvIndex.keys():
                result.append(loadedInvIndex[stemmed]['postings'])

    return result.pop()
             

def andQuery(list1, list2):
    
    #empty result list
    result = []
    #iterator for list1
    i = 0 
    #iterator for list2
    j = 0 
    #ensure within bounds
    while i<len(list1) and j<len(list2):
        #compare with next element of list1
        if list1[i] < list2[j]:
            i += 1
        #compare with next element of list2
        elif list1[i] > list2[j]:
            j += 1
        #if common, add to result
        else:
            result.append(list1[i])
            i += 1
            j += 1

    return result


def orQuery(list1, list2):

    #concatenate both lists
    result = list1 + list2
    #remove any duplicates
    result = list(set(result))  #ans = list(dict.fromkeys(ans)) alternate
    
    return result


def notQuery(list1):
    #empty result list
    result = []

    for doc in range(1,31,1):
        if doc not in list1:
            result.append(doc)

    return result


####################################################################################
#Proximity Query Processing
####################################################################################


def proxQuery(term1, term2, dist):
    #empty list for result
    result = []

    #normalize terms - remove special chcar

    #load positional index
    loadedPosIndex = loadPosIndex()

    #if terms exist
    if term1 in loadedPosIndex.keys() and term2 in loadedPosIndex.keys():
        #for all the documents in term1's postling list
        docNos1 = [] #posting list of doc 1
        for posting in posInd[term1]['postings']:
            docNos1.append(posting['docNo']) #contains all documents in posting list of term1

        docNos2 =[] #posting list of doc 2
        for posting in posInd[term2]['postings']:
            docNos2.append(posting['docNo'])

        #if the document is also in term2's posting list
        for doc in docNos1:
            if doc in docNos2:
                
                #for positions of q1 in that document
                pos1 = []#store positions of q1
                for posting in loadedPosIndex[term1]['postings']:
                    if posting['docNo'] == doc:
                        pos1 = posting['position']
                        break
                
                
                #for positions of q1 in that document
                pos2 = []#store positions of q1
                for posting in loadedPosIndex[term2]['postings']:
                    if posting['docNo'] == doc:
                        pos2 = posting['position']
                        break
                
                          
                for pos in pos1:
                    #if term2 is at position + dist in its doc
                    #print(pos)
                    for i in range (pos-dist,pos+dist+1,1):
                        if i in pos2:
                            
                            result.append(doc)
            
    #print(pos1)
    return set(result)


####################################################################################
#User Query Processing
####################################################################################


def parseQuery(query):
    #do not use stemming/ char removal at this point 
    #tokenize
    tokens = word_tokenize(query)
    #casefold
    qTokens = caseFolding(tokens)

    return qTokens


def searchQuery(qTokens):

    result = []

    #if query does not contain any and/or/not
    if not any(op in ['and','or','not'] for op in qTokens):

        #if token len is 0 then return nothing
        if len(qTokens) == 0:
            return result 
        #if token length is 1
        if len(qTokens) == 1:
            #call stemmer
            stemToken = stemmer(qTokens)
            #load inverted index 
            loadedInvIndex = loadInvIndex()

            #get the posting list and return
            for term in stemToken:
                if term in loadedInvIndex.keys():
                    result =  loadedInvIndex[term]['postings']
                return result
                #print(list1)


        #if token length 2 and ofc it doesnt have not so must be prox query
        if len(qTokens) == 2:
            #consider prox dist =1 
            stemTokens = stemmer(qTokens)
            result = proxQuery(stemTokens[0],stemTokens[1], 1)
            return result

        #else it must be prox query with token[4] being the proximity dist
        else:
            #convert token[3] to int
            stemTokens = stemmer(qTokens)
            result = proxQuery(stemTokens[0],stemTokens[1], int(stemTokens[3]))
            return result
    #else if and/or/not
    else:
        postfix = invQuery(qTokens)
        result = calcPostfix(postfix)
        return result
    
####################################################################################
#Driver code
####################################################################################

def driver():
    # Get the query from the entry widget
    query = queryEntry.get()
    
    # Start the timer
    startTime = time.time()
    
    # Parse the query
    queryTokens = parseQuery(query)
    
    # Search the query
    result = searchQuery(queryTokens)
    
    # End the timer
    endTime = time.time()
    
    # Calculate the elapsed time
    elapsedTime = (endTime - startTime) * 1000 # in milliseconds
    
    # Update the result label
    if len(result) == 0:
        resultLabel.config(text="No results found")
    else:
        resultLabel.config(text=result)
    
    # Update the time label
    timeLabel.config(text=f"Elapsed time: {elapsedTime:.2f} milliseconds")
    

def clear():
    # Clear the query entry widget
    queryEntry.delete(0, tk.END)
    
    # Clear the result label
    resultLabel.config(text="")
    
    # Clear the time label
    timeLabel.config(text="")
    queryEntry

if __name__ == "__main__":
    # Call the indexer
    indexer()
    
    # Create the main window
    root = tk.Tk()
    root.geometry("400x300+100+100")
    root.title("Boolean Retrieval Model")
    
    # Create the query label and entry widget
    queryLabel = tk.Label(root, text="Enter Query:")
    queryEntry = tk.Entry(root, width=50)
    
    # Create the search button
    searchButton = tk.Button(root, text="Search", command=driver)
    
    # Create the clear button
    clearButton = tk.Button(root, text="Clear", command=clear)
    
    # Create the result label and time label
    resultLabel = tk.Label(root, text="")
    timeLabel = tk.Label(root, text="")
    
    # Add padding
    queryLabel.pack(pady=5)
    queryEntry.pack(pady=5)
    searchButton.pack(pady=5)
    clearButton.pack(pady=5)
    resultLabel.pack(pady=5)
    timeLabel.pack(pady=5)
    
    # Pack the widgets
    queryLabel.pack()
    queryEntry.pack()
    searchButton.pack()
    clearButton.pack()
    resultLabel.pack()
    timeLabel.pack()


    root.config(bg='black')

    queryLabel.config(fg='white', bg='black')
    queryEntry.config(fg='black', bg='white')

    searchButton.config(fg='white', bg='black')
    clearButton.config(fg='white', bg='black')

    resultLabel.config(fg='white', bg='black')
    timeLabel.config(fg='white', bg='black')

    
    # Start the main event loop
    root.mainloop()
