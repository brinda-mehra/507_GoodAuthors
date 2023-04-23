# SI507 Final Project: GoodAuthors
This program is a 507 final project designed to provide users with more information about their favorite authors, scraped from the GoodReads website.

After starting the program, users can input an author of interest and obtain information about
the genres the authors write for, a link to their personal website or to their Amazon page. Users can also view a visualization of a network of all their searched authors and their influences. 

**Built with:** 
* Python3 - programming language on backend
* Packages: 
    1. Networkx
    2. Unidecode
    3. BeautifulSoup
    4. Matplotlib

# Data Sources
The program scraped multiple sites on GoodReads to create a universe of author data depending on
the searches

# Getting Started
Make sure you have downloaded the Networkx, Unidecode and BeautifulSoup packages, as well as all the files to allow for reading and writing data to disk. The code comes with a set of default authors that provide an initial baseline, but these can be replaced according to your preferences.

💡**Note:** You can also delete the _myauthors.json_ file after downloading the program and once you replace the author names in the _defaultauth_ variable, you can run the program again and it will generate a new cache file with your chosen authors.

To run the program, simply use the command **python3 AuthorSearch.py**

# Data Presentation
After downloading the program and running it, users will be given an initial prompt that allows them to either: 
* type _new_ to clear the data from previous sessions and start over from scratch 
* search for a new author 
* type _view_ to see additional information options 
* type _exit_ to close the program and save all searches to a cache

If users choose to _view_ additional information options, they can then: 
* Type '1' to create a visualization of all their searched authors and their influences, sourced from the GoodReads site
* Type '2' to see the genres your last search is classified into 
* Type '3' to open up the last search's personal website 
* Type '4' to open up the Amazon page for your last search 

💡**Note:** If you create a network visualization, please remember to close it if you want to see the interaction prompt again
💡**Note:**If users choose the view option without searching for a new author, they will be shown the network diagram of the defaultauth list but redirected to the search if they try to view the genres, personal website or amazon page since no search was carried out. 

# Author
Brinda Mehra 

# Acknowledgements
Professor Bobby Madamanchi and the SI507 Winter 2023 instruction team, for their feedback and advice! 
