# Instaprices

Instaprices analyzes prices at instacart stores in your area based on a custom shopping list, compares them, and displays the resulting data in a chart. This is done using selenium to automate browser behavior and scrape data, and matplotlib to render visuals. Can also import shopping lists from txt files, and import/export scraped store data as json files.

## Requirements
- **python 3.10.2** (older 3.3+ versions may work, but no promises)
- most recent version of **Google Chrome** (older versions may work, but no promises)

## Installation
- Run `git clone https://github.com/richard-oden/instaprices.git` to clone the repository.
- In the instaprices directory, run `python3 -m venv venv` to create the virtual environment.
- Activate the newly created virtual environment. From the instaprices directory run the following command:
    - if using Windows PowerShell: `venv\Scripts\Activate.ps1`
    - if using Linux or Mac with bash/zsh: `venv/bin/activate`
    - (if you're still having trouble, see [this](https://docs.python.org/3/library/venv.html) and [this](https://itnext.io/a-quick-guide-on-how-to-setup-a-python-virtual-environment-windows-linux-mac-bf662c2c77d3) for help.)
- Run `pip install -r requirements.txt` to install the required packages.

Note that sometimes Chrome may get stuck with `data:,` in the address bar. When this happens, try ending any Chrome processes that are already running, then run the program again. In Windows, this can be done in the Task Manager by pressing CTRL+ALT+DEL.