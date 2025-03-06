import requests
import json
from xml.etree import ElementTree
import html
from bs4 import BeautifulSoup
import re

# Replace 'YOUR_BLOG_ID' with the actual Blog ID you want to access
BLOG_ID = '6062254512243140521'
#FIXME només podem obtenir uns 200 posts per volta, estem canviant a ma el valor de start-index a cada execució
MAX_RESULTS = 200  # Adjust the number of posts to retrieve per request

# Initialize variables
page_token = None
all_posts = []

while True:
    # Define the Blogger API URL to retrieve posts with pagination
    api_url = f'https://www.blogger.com/feeds/{BLOG_ID}/posts/default?max-results={MAX_RESULTS}&start-index=600'

    if page_token:
        api_url += f'&pageToken={page_token}'

    # Send an HTTP GET request to fetch the posts
    response = requests.get(api_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response as XML
        posts_xml = response.text

        try:
            # Parse the XML and extract post titles and content
            root = ElementTree.fromstring(posts_xml)

            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
                post_title = entry.find(".//{http://www.w3.org/2005/Atom}title").text
                print(f"Post Title: {post_title}")
                if 'Acudits en català (' in post_title:
                    print("Obtenim el post {0}".format(post_title))
                    content_element = entry.find(".//{http://www.w3.org/2005/Atom}content")
                    if content_element is not None:
                        # Use BeautifulSoup to remove HTML tags and get plain text
                        soup = BeautifulSoup(content_element.text, 'html.parser')
                        #//for br in soup.find_all("br"):
                        #    br.replace_with("\n")
                        for br in soup.find_all("br"):
                            br.replace_with("\n")
                        #post_content = soup.get_text(separator = '\n')
                        post_content = soup.get_text()
                        #post_content = re.sub(r'\n{2,}', '\n', post_content)
                        all_posts.append((post_title, post_content))
                else:
                    print("Descartem el post {0}".format(post_title))
            # Check if there are more pages
            next_link = root.find('.//{@rel=">http://a9.com/-/spec/opensearchrss/1.0/}link[@rel="next"]')
            if next_link is None:
                break
            else:
                # Extract the page token for the next page
                page_token = next_link.attrib.get('href').split('&pageToken=')[1]

        except Exception as e:
            # Code to handle the exception
            print(f"An exception occurred: {e}")

    else:
        print(f"Failed to retrieve posts. Status Code: {response.status_code}")
        break

# Save the content of each post as a text file
for post_title, post_content in all_posts:

    try:
        filename = f"{post_title}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(post_content)
            print(f"Saved content for '{post_title}' to {filename}")

    except Exception as e:
        # Code to handle the exception
        print(f"An exception occurred: {e}")