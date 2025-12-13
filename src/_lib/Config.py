CONFIG_PATH = "/home/pi/_config/config_autorun.txt"

class Config():
    def __init__(self, path_config_file:str):
        self.config = {}

        with open(path_config_file) as file:
            self.config_data = file.readlines()
    
        for idx, line in enumerate(self.config_data):
            self.config_data[idx] = line.strip()
            
            if self.config_data[idx][0:2] == "//" or self.config_data[idx] == "": 
                continue

            self.config[self.config_data[idx].split(": ")[0]] = self.config_data[idx].split(": ")[1]


    def __str__(self):
        string = ""
        for key in self.config.keys():
            string += f"{key}: {self.config[key]}\n"
        return string


    def get_keys(self) -> list:
        return list(self.config.keys())
    

    def get_item(self, key:str) -> str:
        return self.config[key] 
    
    def get_bool(self, key:str) -> bool:
        if key in ["True", "False","true", "false", "1", "0"]:
            if key == "True" or key == "true" or key == "1":
                return True
            else:
                return False
        else:
            return False


if __name__ == "__main__":
    config = Config(CONFIG_PATH)
    