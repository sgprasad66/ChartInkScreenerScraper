import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
config_file.add_section("MongoDBSettings")
# ADD SETTINGS TO SECTION
config_file.set("MongoDBSettings", "mongodbclient", "mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority")
config_file.set("MongoDBSettings", "databasename", "ChartInkTradeLog")
config_file.set("MongoDBSettings", "collectionname", "17_04_2023")
config_file.set("MongoDBSettings", "deletecollectionname", "17_04_2023")

#Add kite settings
config_file.add_section("KiteSettings")
config_file.set("KiteSettings", "enctoken", "e+h0spdLoJMQI/LW9PnrDFKv6/FF8tLz5MkOp5NZT0QpMBifU5Y+x2eOMUaLKvP+gmF0oOHNdgkathB34y5h/uAH85nyqMdqpkcZFfXtPRJhQDc5Pj911A==")

#Add alice Blue settings
config_file.add_section("AliceBlueSettings")
config_file.set("AliceBlueSettings", "username", "AB067538")
config_file.set("AliceBlueSettings", "apikey", "Cr2dG4mpQaal3M5MMlAkSaa6ziJOXOq7JLle6IUWi8MFMy3QkKd1oXKUcW1bDfA4I733GfexzTg4GaKQXT8rrDPZg5LDn8Ll2sJRbRtdMuWUIrOtkTTi33RuLfxMQ0lc")

config_file.set("AliceBlueSettings", "password", "17_04_2023")
config_file.set("AliceBlueSettings", "appsecret", "17_04_2023")

# ADD NEW SECTION AND SETTINGS
config_file["Logger"]={
        "LogFilePath":"D:\FilesFromRoopesh\OptionsPakshiResampling\ChartInkScreenerScraper\log",
        "LogFileName" : "17_04_2023.log",
        "LogLevel" : "Info"
        }

config_file["ChartinkscraperSettings"]={
        "maxitemcount":"25"
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