import re
import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from data.DataQueries import DataQueries
from progressbar import progressbar

class KeepTradeCutSpider(scrapy.Spider):
    name = "KeepTradeCut"
    start_urls = [
        "https://keeptradecut.com/fantasy-rankings",
    ]

    def refresh_ktc_rankings(self):
        process = CrawlerProcess(get_project_settings())
        process.crawl(KeepTradeCutSpider)
        process.start()

    def parse(self, response):
        db = DataQueries()

        db.clear_ktc_data()

        # Locate the script tag containing 'playersArray'
        script_content = response.xpath("//script[contains(text(), 'playersArray')]/text()").get()

        if script_content:
            # extract the playersArray definition using regex
            match = re.search(r"var playersArray.*;", script_content, re.DOTALL)

            if match:
                # extract and parse the JSON data
                player_data_statement = match.group(0).split(';')[0]
                players_data = player_data_statement.split('=')[1].strip().rstrip(';')
                players = json.loads(players_data)

                for player in progressbar(players):
                    player_name = player["playerName"].split(' ')

                    db.insert_ktc_data(player['playerID'], player_name[0].replace('\'', ''), player_name[1], player['position'],
                                       player['oneQBValues']['rank'], player['superflexValues']['rank'], json.dumps(player).replace('\'', ''))
