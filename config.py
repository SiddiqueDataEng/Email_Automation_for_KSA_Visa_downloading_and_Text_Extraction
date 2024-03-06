import json
import os

class Config:
    CONFIG_FILE = 'config.json'
    
    def __init__(self):
        self.defaults = {
            'email': 'sattiofficerwp@gmail.com',
            'password': 'lmigfxajjaafxbie',
            'from_email': 'no-reply@mofa.gov.sa',
            'subject_filter': 'Saudi eVisa',
            'save_path': r'\\COUNTER3\Shared Data\Visa_Slips_Automated',
            'check_interval': 60  # seconds
        }
        self.load()
    
    def load(self):
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as f:
                loaded = json.load(f)
                self.__dict__.update(loaded)
        else:
            self.__dict__.update(self.defaults)
            self.save()
    
    def save(self):
        config_data = {k: v for k, v in self.__dict__.items() 
                      if k not in ['defaults', 'CONFIG_FILE']}
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def update(self, data):
        self.__dict__.update(data)
        self.save()
    
    def get_all(self):
        return {k: v for k, v in self.__dict__.items() 
                if k not in ['defaults', 'CONFIG_FILE']}
