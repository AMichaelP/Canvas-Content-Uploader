import configparser
from pathlib import Path

from canvas_content_uploader.root_components.MasterGui import MasterGui

config_path = Path('config.ini')
assert config_path.is_file()

config = configparser.ConfigParser()
config.read(config_path)

CANVAS_URL = config['DEFAULT']['canvas_url']
WINDOW_TITLE = config['DEFAULT']['window_title']
ICON_PATH = config['DEFAULT']['icon_path']


def main():
    g = MasterGui(canvas_url=CANVAS_URL, title=WINDOW_TITLE, icon_path=ICON_PATH)
    g.run()


if __name__ == '__main__':
    main()
