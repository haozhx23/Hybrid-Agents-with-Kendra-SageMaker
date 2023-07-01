import requests


class WebSearcher:
    
    def __init__(self, apikey, result_count=5, lang_code='zh'):
        self.NAME = 'WebSearch'
        self.DESC = ""
        self.RapidAPIKey = apikey
        self.ReturnCount = result_count
        self.langCode = lang_code
        
        ## google rapidapi
        ## https://rapidapi.com/herosAPI/api/google-search74
        self.apiurl = "https://google-search74.p.rapidapi.com/"
        self.headers = {
                "X-RapidAPI-Key": self.RapidAPIKey,
                "X-RapidAPI-Host": "google-search74.p.rapidapi.com"
        }

        
    def search(self, query: str = ""):
        query = query.strip()
        

        querystring = {"query":query,"limit":self.ReturnCount,"related_keywords":"true"}
        
        
        # Requests
        response = requests.get(self.apiurl, headers=self.headers, params=querystring)
        data_list = response.json()['results']


        if len(data_list) == 0:
            return ""
        else:
            result_arr = []
            result_str = ""
            count_index = 0
            for i in range(self.ReturnCount):
                item = data_list[i]
                title = item["title"]
                description = item["description"]
                url = item["url"]
                item_str = f"{title}: {description} # {url} #"
                result_arr = result_arr + [item_str]


            result_str = "\n".join(result_arr)
            return result_str
