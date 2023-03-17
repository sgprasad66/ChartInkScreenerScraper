import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
config_file.add_section("MongoDBSettings")
# ADD SETTINGS TO SECTION
config_file.set("MongoDBSettings", "mongodbclient", "mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority")
config_file.set("MongoDBSettings", "databasename", "ChartInkTradeLog")
config_file.set("MongoDBSettings", "collectionname", "16_03_2023")
config_file.set("MongoDBSettings", "deletecollectionname", "16_03_2023")

#Add kite settings
config_file.add_section("KiteSettings")
config_file.set("KiteSettings", "enctoken", "fDMKufy4JEym5Q/teQdP7KTgmxz3MU4ppxCAHQMzrAr3ED7DQFcelKRL+5BxMwiMFuV3OpAuH0MkV2rmPIuNIgLEgf3wYzcPkwgMWLu63258AABaPFmz3g==")

#Add alice Blue settings
config_file.add_section("AliceBlueSettings")
config_file.set("AliceBlueSettings", "username", "AB067538")
config_file.set("AliceBlueSettings", "apikey", "A2oYu9unGxQeLyazBgNHz3rMsvEi2Bnvx2T0PCGJW60QNmf8HvuLtuzQdJzH9JxJmeLbHkkiNOBIdSmUOgSeRV0riIhZ9b61kDuf66tko7RFLNsvAdfyORAN382UzINg")
config_file.set("AliceBlueSettings", "password", "16_03_2023")
config_file.set("AliceBlueSettings", "appsecret", "16_03_2023")

# ADD NEW SECTION AND SETTINGS
config_file["Logger"]={
        "LogFilePath":"D:\FilesFromRoopesh\OptionsPakshiResampling\ChartInkScreenerScraper\log",
        "LogFileName" : "16_03_2023.log",
        "LogLevel" : "Info"
        }

config_file["ChartinkscraperSettings"]={
        "maxitemcount":"20"
}

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