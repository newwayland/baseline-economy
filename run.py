from BaselineEconomy.server import server
import sys

server.launch(open_browser=len(sys.argv) == 1)
