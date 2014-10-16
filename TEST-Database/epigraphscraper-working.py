#For use with python 3.x.
# Program only checks xml files in directory that contains this python file.
# Delete all csv files before running script. Script appends to csv files of 
# the same name if they already exist.

# libraries
from bs4 import BeautifulSoup            # select XML tags and parse text
from os import walk, getcwd, listdir     # grab all files in directory of script
import os                                
import csv                               # interact with csv files (not yet working)
import re                                # use regular expressions to standardize authors
#import sys                              # take input from command line

# variables & functions
totalEpigraphCount = 0                   #number of epigraphs in xml files in corpus
epigraphlessFileCount = 0                #number of xml files in corpus that do not have epigraphs

def remove_characters(listofstrings, characters_to_be_removed):
    for string in range(0,len(listofstrings)):
        cleaned_text = ""
        for character in listofstrings[string]:
            if character not in characters_to_be_removed:
                cleaned_text += character 
        listofstrings[string] = cleaned_text 
    return listofstrings 


## COLLECTING INFORMATION FROM CORPUS 
allFilesInDirectory = [ filename for filename in listdir(getcwd()) if filename.endswith('.xml')] #get filenames in current directory ending in ".xml"
for document in range(0, len(allFilesInDirectory)):                   # Loop through all files in directory
    root, ext = os.path.splitext(allFilesInDirectory[document])       # Select file extension for particular file "x" in the list "allFilesInDirectory"
    if (ext == '.xml'):                                               # If file ends in ".xml", read file. Skip file otherwise. 
    # open file to be read
        readfile = open(str(allFilesInDirectory[document]))	          # Specify file to be read & open file
        soup = BeautifulSoup(readfile)                                # Make "soup" object of file to search 
    
    # collect novel author, title of novel, pub date, epigraph, epigraph attrib, pub location, publisher, & encoding company from individual file
        author_list = [author.text for author in soup('author')]   # collect text "author" entries
        title_list = [title.text for title in soup('title')]       # collect text "title" entries
        
        publication_date = [date.text for date in soup('date')]    # collect text pub year entries
        if "eaf" in root:                                          # select correct year depending on EAF or Wright corpus. Throw warning if not one of these two corpora.
                pub_year = str(publication_date[1])                # pick 2nd date tag for EAF corpus
        else:
            if "VAC" in root:
                pub_year = str(publication_date[0])                # pick 1st date tag for Wright corpus
            else: 
                pub_year = 'Unknown Corpus, see terminal warning'                  # user must check pub year entry
                print('WARNING: Check publication year for file ' + root + ext + '\n') 
                print('List of publication dates in file: \n')
                print(publication_date)
        
        publication_place = [pubplace.text for pubplace in soup('pubplace')]  #collect text pub location
        if len(soup('epigraph')) > 0:                                         #collect entries tagged "epigraph" and place it in the list "epigraphlist'
            epigraph_list = [epigraph.text for epigraph in soup('epigraph')]  
            epigraph_attribution = ["No Attribution" if soup('epigraph')[epigraphs].bibl == None \
                                                 else  soup('epigraph')[epigraphs].bibl.text \
                                                 for epigraphs in range(0,len(soup('epigraph')))]
            #see how many quote tags are nested in epigraph tags (for error checking; see line 59)
            quote_tags_in_epigraph = ["No quote tags" if soup('epigraph')[epigraphs].quote == None \
                                                 else soup('epigraph')[epigraphs].quote.text \
                                                 for epigraphs in range(0,len(soup('epigraph')))]
        else: 
            epigraph_list = ['No Epigraphs']
            epigraph_attribution = ['No Epigraphs']
        if len(soup('publisher')) > 0:         
            publishers = [publisher.text for publisher in soup('publisher')]
        else: 
            publishers = ['Unknown Publisher', 'Unknown Publisher','Unknown Publisher']
        
    # Checks to identify epigraphs with 'quote' tag & tracking of who did encoding (see also lines 47-50)
        total_epigraph_tags = str(len(soup('epigraph')))        # number of tagged "epigraph"s in file
        total_quote_tags = str(len(soup('quote')))              # number of tagged "quote"s in file
        quotes_in_epigraphs = str(len(quote_tags_in_epigraph))  # number of "quote"s in "epigraph"s

    # identify company that produced xml file (c.f. labor issues involving corpus creation)
        encoding_company = 'No Company Attribution Found'
        encoding_counter = 0
        if len(soup('name')) > 0 :
            encoding_company = str(soup('name')[0].text)
        if soup(text='Apex Data Services'):
            encoding_company = 'Apex Data Services'
            encoding_counter = encoding_counter+1
        if soup(text='Digital Library Program'):
            encoding_company = ' AEL Data, Pacific Data Conversion Corp (now SPI Content Sciences), OR Techbooks. see http://webapp1.dlib.indiana.edu/TEIgeneral/projectinfo/encoding.do'
            encoding_counter = encoding_counter+1
        if soup(text='ACR'):
            encoding_company = 'ACR'
            encoding_counter = encoding_counter+1
        if (encoding_counter > 1):
            encoding_company = 'Multiple companies detected. CHECK FILE.'

    ## CLEANING INFORMATION COLLECTED FROM CORPUS
    # remove "/n" characters
        epigraph_attribution = remove_characters(epigraph_attribution, '-\n')
        author_list = remove_characters(author_list, '\n')
        title_list = remove_characters(title_list, '\n')
        publication_place = remove_characters(publication_place, '\n')
        publishers = remove_characters(publishers, '\n')
        pub_year = remove_characters([pub_year], '\n')[0]
        print(pub_year)
        encoding_company = str(remove_characters([encoding_company], '\n'))                                   
    
    # standardize names in author list
    # generate a dict for first and last names based on corpus entries for XML texts
    #reg_ex_for_year = re.compile(r'^(10|11|12|13|14|15|16|17|18|19|20)\d{2}$') #find 4-digit year b/w 1000 & 2999

        readfile.close() #close file "x"

# Error Checking Print-To-Terminal: print all information collected
        if (len(soup('epigraph')) == 0):                         #check if file has epigraphs                
            if (len(soup('author')) > 0):
                epigraphlessFileCount += 1     
            else:
                if (len(soup('author')) == 0):
                    author_list = ['NO AUTHOR TAG IN FILE. CHECK XML FILE!']
                    epigraphlessFileCount += 1 
        else:
            for i in range(0, len(soup.findAll('epigraph'))):          
                if (len(soup.findAll('author')) == 0):
                   totalEpigraphCount += 1
                else:    
                    totalEpigraphCount += 1

#output to a CSV file -- NOTE: need to wrap strings in a list for csvwriter to output properly
        with open('epigraph_metadata.csv', 'a') as csvfile: #output metadata
            epi_meta = csv.writer(csvfile, dialect='excel')
            for i in range(0,len(soup('epigraph'))):
                if (len(soup('author')) ==0):
                    epi_meta.writerow([str(i) + '|' + allFilesInDirectory[document] + '|'+ str(document) + '|' +  'Unknown Author' + '|' + str(title_list[0])+ '|' + str(epigraph_attribution[i])+ '|' + str(publishers[1]) + '|' + str(publication_place[1])+ '|' + pub_year])           
                else:
                    epi_meta.writerow([str(i) + '|' + allFilesInDirectory[document] + '|'+ str(document) + '|' +  author_list[0] + '|' + str(title_list[0])+ '|' + str(epigraph_attribution[i])+ '|' +  str(publishers[1]) + '|' + str(publication_place[1])+ '|' + pub_year])

        with open('epigraph_list.csv', 'a') as csvfile: #output metadata
            epi_list = csv.writer(csvfile, dialect='excel')
            for i in range(0,len(soup('epigraph'))):
                epi_list.writerow(['Text ' + str(document+1)+ ', epigraph ' + str(i+1)]) 
                epi_list.writerow([epigraph_list[i]])           

        #output ratio of epigraphs-to-quotes for each file, warnings, & error checks
        with open('epigraph_to_quotes.csv', 'a') as csvfile: 
            epi_to_quote = csv.writer(csvfile, dialect='excel')
            if (document == 0):
                epi_to_quote.writerow(['file number' + '|' + 'file name' + '|' + 'encoding credit' + '|' + 'total epigraph tags' + '|' + 'total quote tags' + '|' + 'quote pairs in epigraphs' ])
            
            author_error_check = 'Field Empty -- ERROR'
            if len(soup('author')) == 0:
                author_error_check = 'No Author Tags!'
            else:
                author_error_check = str(len(soup('author')))

            epi_to_quote.writerow([str(document) + '|' + str(allFilesInDirectory[document]) + '|' +  encoding_company + '|' + total_epigraph_tags + '|' + total_quote_tags + '|' + quotes_in_epigraphs])
        
#Error Checking Print-To-Terminal: Print total number of epigraphs collected  
print("TOTAl NUMBER OF EPIGRAPHS: " + str(totalEpigraphCount))
print("TOTAL NUMBER OF FILES: " + str(len(allFilesInDirectory)))
print("FILES WITHOUT EPIGRAPHS: " + str(epigraphlessFileCount))

#SYNTAX NOTE FOR BS4  ----
#Can directly access individual epigraph as follows:
#soup('author')[0].text
#soup('author')[1].text
#etc. 
#
#ALSO, NOTE FOR BS4: soup('epigraph') == soup.find_all('epigraph') == soup.findAll('epigraph')
