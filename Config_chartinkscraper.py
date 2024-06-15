import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
config_file.add_section("MongoDBSettings")
# ADD SETTINGS TO SECTION
#config_file.set("MongoDBSettings", "mongodbclient", "mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsCAFile=C:/Users/Guru Prasad/AppData/Local/.certifi/cacert.pem")
config_file.set("MongoDBSettings", "mongodbclient", "mongodb://127.0.0.1:27017")
config_file.set("MongoDBSettings", "databasename", "ChartInkTradeLog")
config_file.set("MongoDBSettings", "collectionname", "14_06_2024")
config_file.set("MongoDBSettings", "deletecollectionname", "14_06_2024")

config_file.add_section("RepositorySettings")
config_file.set("RepositorySettings", "RepositoryMode", "3")  #1- stored in a JSON file, 2- stored in MongoDB NoSQL Database,3 - MySQL database
#Add kite settings
config_file.add_section("KiteSettings")
config_file.set("KiteSettings", "enctoken", "EVUQ36oEiejNsDMVtNDLBxG/xuBbaJbAKh+k5bmKFLMymu0A/BZE8h3K7X7+IhHXHhbLhrH9rxDYonIqXJ6RELGRaj9wcF5ERoquTfqLT4QUT/ojBcE22Q==")

#Add alice Blue settings
config_file.add_section("AliceBlueSettings")
config_file.set("AliceBlueSettings", "username", "")
config_file.set("AliceBlueSettings", "apikey", "")

config_file.set("AliceBlueSettings", "password", "14_06_2024")
config_file.set("AliceBlueSettings", "appsecret", "14_06_2024")

config_file.add_section("DaysPositionsSettings")
config_file.set("DaysPositionsSettings", "PositionsFilePath", "D:\FilesFromRoopesh\OptionsPakshiResampling\ChartInkScreenerScraper\DailyPositions")
# ADD NEW SECTION AND SETTINGS
config_file["Logger"]={
        "LogFilePath":"D:\FilesFromRoopesh\OptionsPakshiResampling\ChartInkScreenerScraper\log",
        "LogFileName" : "14_06_2024.log",
        "LogLevel" : "Info"
        }

config_file["ChartinkscraperSettings"]={
        "maxitemcount":"5"
}
config_file.set("ChartinkscraperSettings", "positional_maxbackdays", "15")
config_file.set("ChartinkscraperSettings", "positional_maxitemcount", "25")
config_file.set("ChartinkscraperSettings", "positional_today_maxitemcount", "10")
config_file.set("ChartinkscraperSettings", "intraday_today_maxitemcount", "5")

config_file.add_section("SLandTPSettings")
config_file.set("SLandTPSettings","sl_index_options",".15")
config_file.set("SLandTPSettings", "tp_index_options", ".3")
config_file.set("SLandTPSettings", "sl_stock_options", ".05")
config_file.set("SLandTPSettings", "tp_stock_options", ".12")
config_file.set("SLandTPSettings", "lots_multiplier", "2")

config_file.add_section("SLandTPSettingsForHegdedPositions")
config_file.set("SLandTPSettingsForHegdedPositions", "sl_index_options", ".25")
config_file.set("SLandTPSettingsForHegdedPositions", "tp_index_options", ".5")

# SAVE CONFIG FILE
with open(r"configurations.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'configurations.ini' created")

# PRINT FILE CONTENT
read_file = open("configurations.ini", "r")
content = read_file.read()
print("Content of the config file are:\n")
print(content)
read_file.flush()
read_file.close()
