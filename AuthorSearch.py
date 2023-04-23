import requests
import webbrowser
import networkx as nx 
from bs4 import BeautifulSoup, Tag
import unidecode
import matplotlib.pyplot as plt
import sys
import jsonIO  #json reader/writer file

# list of error msgs to be called for different user inputs
error_msgs = {
    'Author': "Sorry, GoodReads did not find this author. Check the spelling or try another author",
    'Influence': "Sorry, GoodReads has no influences for this author on record!",
    'Web': "This author doesn't have a personal website listed on Goodreads :(",
    'Genre': "No genres on record for this author",
    'Requests': "Error connecting to goodreads, please try again"
}


def getAuthorURL(input):
    """
    Searches Goodreads for the URL of an author page based on their name.

    Parameters:
        input (str): The name of the author to search for. May contain accented
            characters. Uses the unidecode library to account for that

    Returns:
        list or None: A list with two elements: the name of the author (str) and
            the URL of their Goodreads page (str), if found. Returns None if no
            matching author is found. If multiple authors are found, returns the
            first one.
    """
    accented_name = input
    if accented_name == "new":
        pass
    else:
        ascii_name = unidecode.unidecode(accented_name)
        # Replace spaces with plus signs to create the GoodReads URL
        search_input = ascii_name.replace(" ", "+")
        searchURL = 'https://www.goodreads.com/search?q=' + search_input
        response = requests.get(searchURL)
        content = response.content.decode('utf-8')
        # Parse the HTML response with BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")
        # Find the divs containing author names and URLs
        author_div = soup.find_all("div",{"class": 'authorName__container'})
        # Clean up the divs to extract author names and URLs
        author_url_clean = [y for x in author_div for y in x.children if isinstance(y, Tag )]
        author_url_list = [[x.contents[0], x.get("href")] for x in author_url_clean]
        author_span = [[x[0].contents[0], x[1]] for x in author_url_list if isinstance(x[0], Tag)]
        auth_span = [[unidecode.unidecode(x[0]), x[1]] for x in author_span]
        # Find the author with a name that matches the input (case-insensitive)
        authorList = [x for x in auth_span if ascii_name.lower() in x[0].lower()]
        if len(authorList) == 0:
            print("Sorry, GoodReads did not find this author. Check the spelling or try another author")
            return None
        # Return the name and URL of the first matching author
        author_url = authorList[0]
        print(author_url[0])
        return author_url


def getInfluences(url):
    """
    Extracts a list of authors who influenced a given author, based on their Goodreads page.

    Parameters:
        url (str): The URL of the Goodreads page for the author whose influences to extract.

    Returns:
        list: A list of dictionaries, where each dictionary contains the name and URL of an
            author who influenced the target author. The dictionaries are sorted in the order
            they appear on the Goodreads page. Returns an empty list if no influences are found.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    # Find the section containing influences (if any) using BeautifulSoup
    influences_section = soup.find_all("div",string="Influences")
    if len(influences_section) == 0:
       return []
    # Extract the text containing influence names and URLs
    influences_text = influences_section[0].find_next_sibling("div")
    influences_span = influences_text.find_all("span")[-1]
    authorList = influences_span.find_all("a")
    # Create a list of dictionaries with author names and URLs
    authorNames = [{'name': x["title"], 'url': x["href"]} for x in authorList]
    return authorNames

def getAuthorDetails(url):
    """
    Extracts author's website and genres from a given Goodreads author profile URL.

    Args:
        url (str): The URL of the Goodreads author profile.

    Returns:
        dict: A dictionary containing the author's website and a list of genres.

    Raises:
        None

    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    website_section = soup.find_all("div", string="Website")
    if website_section:
        website_div = website_section[0].find_next_sibling("div")
        website = website_div.find_all("a")
        web = website[0]["href"]
    else:
        web = None
    genre_section = soup.find_all("div", string="Genre")
    genres = []
    if genre_section: 
        genre_div = genre_section[0].find_next_sibling("div")
        genre_list = genre_div.find_all("a")
        for genre in genre_list: 
            genres.append(genre.text)
    else: 
        genres = None
    # Create a dictionary containing the author's website and genres
    authordetails = {"website": web, "genres":genres}
    return authordetails


# Building the Author-Influence Universe
class Universe:
    #creating an empty dict to store data upon program closing, a cache file and
    # a default author list to allow users to test the interaction options
    authordetailsmap = {}
    myauthdisk = "myauthors.json"
    defaultauth = ["Haruki Murakami", "Charlotte Bronte", "Agatha Christie", "Bram Stoker"]

    def __init__(self) -> None:
        """
        Class constructor for initializing an object of the Graph class.

        Attributes:
        authordetailsmap (dict): A dictionary that maps author names to their details (website and genres).
    
        Methods:
        createemptygraph: Initializes an empty graph.
        """
        self.createemptygraph()
        self.authordetailsmap = {}
    
    def createemptygraph(self): 
        #create a directed graph using the networkx library
        self.graph = nx.DiGraph()

    def addauth(self, search_string):
        """
    Adds an author and their details to the graph.

    Parameters:
    -----------
    search_string : str
        The name of the author to add.

    Returns:
    --------
    str
        The name of the author that was added to the graph.
        """
         # Check if author already exists in graph
        if search_string in self.authordetailsmap.keys():
            details = self.authordetailsmap[search_string]
            auth = [search_string, details["url"]]
        else:
            auth = getAuthorURL(search_string)
        if auth is None: 
            return 
        # Add author URL to graph and fetch author details and influences
        self.addurl(auth[0], auth[1])
        details = getAuthorDetails(auth[1])
        self.addauthordetails(auth[0], details)
        influence = getInfluences(auth[1])
        # Add author's influences to the graph and update author's details
        self.addmultiurldict(influence)
        self.addtoauthdetails(auth[0],influence)
        self.authtograph(auth, influence)
        return auth[0]
    
    def addtoauthdetails(self, name, influence):
        # Add influence details to the existing author details map.
        self.authordetailsmap[name]["influence"] = [x["name"] for x in influence]

    def addauthordetails(self, name, details):
        """Add the list of author's influences to the author's details map.

        Args:
            name (str): The name of the author.
            influence (list): A list of dictionaries containing influence details.

        Returns:
         None
        """
        if not name in self.authordetailsmap.keys():
            self.authordetailsmap[name] = {}
        self.authordetailsmap[name]["website"] = details["website"]
        self.authordetailsmap[name]["genres"] = details["genres"]


    def addurl(self, name, url): 
        """
        Add a URL to the author details map.

            Parameters
            ----------
            name : str
                The name of the author.
            url : str
                The URL of the author's page.

            Returns
            -------
            None
        """
        if not name in self.authordetailsmap.keys():
            self.authordetailsmap[name] = {}
        self.authordetailsmap[name]['url'] = url

    def addmultiurl(self, urlmap): 
        """
        Add multiple URLs to the author details map.
        
        Args:
        - urlmap (dict): A dictionary mapping author names to their URLs.
        
        Returns: None
         """
        for k in urlmap:
            if not k[0] in self.authordetailsmap.keys():
                self.authordetailsmap[k[0]] = {}
            self.authordetailsmap[k[0]]["url"] = k[1]

    def addmultiurldict(self, influencemap):
        """
            Add multiple author URLs to the graph, along with corresponding author details.
    
            Parameters:
            -----------
            influencemap : list of dictionaries
                A list of dictionaries containing author name and URLs of their works.
            
            Returns:
            --------
            None
        """
        for item in influencemap:
            if not item["name"] in self.authordetailsmap.keys():
                self.authordetailsmap[item["name"]] = {}
            self.authordetailsmap[item["name"]]["url"] = item["url"]

    def authtograph(self, auth, influencemap):
        """
    Add nodes and edges to the graph for a given author and their influences.

    Parameters:
        auth (list): A list containing the author name and their URL.
        influencemap (list): A list of dictionaries containing the names and URLs of the author's influences.

    Returns:
        None
    """
        self.graph.add_node(auth[0])
        for influence in influencemap: 
            self.graph.add_node(influence["name"])
            self.graph.add_edge(auth[0], influence["name"])

    def addtograph(self, auth, influences):
        """
    Adds a node to the graph for the given author and edges to the graph connecting the author to their influences.

    Parameters
    ----------
    auth : str
        The name of the author to add to the graph.
    influences : list of str
        A list of names of authors that have influenced the given author.

    Returns
    -------
    None
    """
        self.graph.add_node(auth)
        for influence in influences: 
            self.graph.add_node(influence)
            self.graph.add_edge(auth, influence)


    def createuniverse(self, authorlist):
        """
    Creates a universe of authors by adding them to the graph.

    Parameters:
    -----------
    authorlist : list
        A list of author names to be added to the graph.

    Returns:
    --------
    None
    """
        [self.addauth(x) for x in authorlist]

    
    def draw_graph(self):
        """
    Draws the graph representation of the universe of authors using NetworkX

    Parameters:
    -----------
    None

    Returns:
    --------
    None
    """
        nx.draw(self.graph, with_labels=True)
        plt.show()

    def write_to_disk(self):
        """
            Writes the author details map to disk.

            Parameters:
            -----------
            None

            Returns:
            --------
            None
    """
        jsonIO.write_to_disk(self.authordetailsmap, self.myauthdisk)
      
    def read_from_disk(self):
        """
        Reads the author details from the disk and loads it to the Universe object.

        Returns:
        None
        """
        self.authordetailsmap = jsonIO.read_from_disk(Universe.myauthdisk)
        if self.authordetailsmap is None:
            self.authordetailsmap = {}
            self.createuniverse(self.defaultauth)
        else:
            [self.addtograph(k, v.get("influence", [])) for k,v in self.authordetailsmap.items()]

    
# Building the User Input

class SearchAuth:
    def __init__(self) -> None:
        self.Universe = Universe()
        self.last_search = ""
        self.started = False

    def openAmazon(self, author_name):
        """
    Opens a new tab in the default web browser with the Amazon search results page for a given author name.

    Parameters:
    -----------
    author_name : str
        The name of the author to search for on Amazon.

    Returns:
    --------
    None
    """
        amazon_url = f"https://www.amazon.com/s?k={author_name}"
        webbrowser.open_new_tab(amazon_url)

    def search_query(self):
        """
    Method to handle user input and perform search operations

    Returns:
    None
    """
         # If the program has just started, print a welcome message
        if not self.started:
            print("Welcome to Author Search! In the 'Action' prompt below, choose what you want to do")
            self.started = True
        # Ask the user for a search query
        search_string = "Type 'new' to clear previous session data, search for a new author and then type 'view' for interaction options or type 'exit' to close and save: "
        searching = input(search_string)
        # If the user types 'new', clear the previous search data
        if searching == 'new':
            self.Universe.authordetailsmap.clear()
            self.Universe.write_to_disk()
            print("Starting a new session!")
        # If the user types in a search query, add the author to the universe
        if searching != "view" and searching != "exit":
            self.last_search = self.Universe.addauth(searching)
            return None
        # If the user types 'exit', save the search data and exit the program
        if searching == 'exit':
            self.Universe.write_to_disk()
            print("Goodbye!")
            sys.exit()
        # If there was no previous search or the user types an invalid option, return an error message
        if self.last_search is None:
            print("Last search failed! Try again")
            return
        # Ask the user what they would like to do with the search result
        search_string2 = ("Enter 1 to see a network of all your author searches and their influences, "
                  "2 to see the main genres your last search writes for,"
                  "3 to open your last search's personal website, "
                  "and 4 to open the Amazon page for their books: ")
        outputnum = input(search_string2)
        # If the user types a number, perform the corresponding action
        if outputnum.isnumeric():
            outputnum = int(outputnum)
            if outputnum == 1:
                 # Draw a network graph of all authors and their influences
                self.Universe.draw_graph()
            if outputnum == 2: 
               # Show the main genres of the last search's books
               try:
                genres = self.Universe.authordetailsmap[self.last_search]["genres"]
                if genres is None:
                    print(error_msgs["Genres"])
                else: 
                    print(genres)
               except:
                   print("Program failed. Try searching for something else?")
            if outputnum == 3:
                 # Open the personal website of the last search
                try: 
                    personal_url = self.Universe.authordetailsmap[self.last_search]["website"]
                    if personal_url is None:
                        print(error_msgs["Web"])
                        return
                    try:
                        print(personal_url)
                        webbrowser.open_new_tab(personal_url)
                    except:
                        print("Can't print what's not there!")
                except: 
                     print("Program failed. Try searching for something else?")
            if outputnum == 4:
                 # Open the Amazon page for the last search's books
                try: 
                    self.openAmazon(self.last_search)
                except:
                    print("Program failed. Try searching for something else?")
    

if __name__ == "__main__":
    search = SearchAuth()
    search.Universe.read_from_disk()
    while True: 
        search.search_query()


