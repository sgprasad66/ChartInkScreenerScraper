import configparser

# CREATE OBJECT
config_file = configparser.ConfigParser()

# ADD SECTION
config_file.add_section("MongoDBSettings")
# ADD SETTINGS TO SECTION
config_file.set("MongoDBSettings", "mongodbclient", "mongodb+srv://TradingUser:Akshara66*@cluster0.tosvjw6.mongodb.net/?retryWrites=true&w=majority")
config_file.set("MongoDBSettings", "databasename", "ChartInkTradeLog")
config_file.set("MongoDBSettings", "collectionname", "19_01_2024")
config_file.set("MongoDBSettings", "deletecollectionname", "19_01_2024")

#Add kite settings
config_file.add_section("KiteSettings")
config_file.set("KiteSettings", "enctoken", "EW0RjVsm6JAIXzwzU2y1+mDD+zTdfx3DQ3Y67inTTNlXz+8IfPkBl0j5fbQeJfWWspH0uzL3MSD+GQmcNEsCwHzUKwOiGzY0D+kBxboN2lhGpUN5HddYYw==")

#Add alice Blue settings
config_file.add_section("AliceBlueSettings")
config_file.set("AliceBlueSettings", "username", "AB067538")
config_file.set("AliceBlueSettings", "apikey", "Cr2dG4mpQaal3M5MMlAkSaa6ziJOXOq7JLle6IUWi8MFMy3QkKd1oXKUcW1bDfA4I733GfexzTg4GaKQXT8rrDPZg5LDn8Ll2sJRbRtdMuWUIrOtkTTi33RuLfxMQ0lc")

config_file.set("AliceBlueSettings", "password", "19_01_2024")
config_file.set("AliceBlueSettings", "appsecret", "19_01_2024")

# ADD NEW SECTION AND SETTINGS
config_file["Logger"]={
        "LogFilePath":"D:\FilesFromRoopesh\OptionsPakshiResampling\ChartInkScreenerScraper\log",
        "LogFileName" : "19_01_2024.log",
        "LogLevel" : "Info"
        }

config_file["ChartinkscraperSettings"]={
        "maxitemcount":"15"
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