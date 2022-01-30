# Instaprices

Instaprices analyzes prices at instacart stores in your area based on a custom shopping list, compares them, and displays the resulting data as a series of charts. This is done using selenium to automate browser behavior and scrape data, and matplotlib to render visuals. Potentially may also include csv export further down the line.

## Instructions
First, you should have Chrome installed. Next, you'll need to install the pip packages listed in requirements.txt. From the project root, this can be done by running `pip install -r requirements.txt`. Then run main.py. 

Note that sometimes Chrome may get stuck with `data:,` in the address bar. When this happens, try ending any Chrome processes that are already running, then run the program again. In Windows, this can be done in the Task Manager by pressing CTRL+ALT+DEL.