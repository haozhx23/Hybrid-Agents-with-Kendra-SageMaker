import requests


class WebSearcher:
    
    def __init__(self, apikey, result_count=5, lang_code='zh', search_engine='bing'):
        self.NAME = 'WebSearch'
        self.DESC = ""
        self.RapidAPIKey = apikey
        self.ReturnCount = result_count
        self.langCode = lang_code
        self.searchEngine = search_engine
        
        if self.searchEngine == 'bing':
            # ## Bing Web Search
            # ## https://rapidapi.com/microsoft-azure-org-microsoft-cognitive-services/api/bing-web-search1/
            self.apiurl = "https://bing-web-search1.p.rapidapi.com/search"
            self.headers = {
                "Accept": "application/json",
                "X-BingApis-SDK": "true",
                "X-RapidAPI-Key": self.RapidAPIKey,
                "X-RapidAPI-Host": "bing-web-search1.p.rapidapi.com"
            }
        elif self.searchEngine == 'google':
            ## google rapidapi
            ## https://rapidapi.com/herosAPI/api/google-search74
            self.apiurl = "https://google-search74.p.rapidapi.com/"
            self.headers = {
                "X-RapidAPI-Key": self.RapidAPIKey,
                "X-RapidAPI-Host": "google-search74.p.rapidapi.com"
            }
                
        
    def search(self, query: str = ""):
        query = query.strip()
        
        querystring = {"q": query,"count": self.ReturnCount,
                "mkt":"en-us","textDecorations":"false","setLang":"EN","safeSearch":"Off","textFormat":"Raw"}
        
        if self.langCode == 'zh':
            querystring = {"q": query,"count": self.ReturnCount,
                "mkt":"zh-cn","textDecorations":"false","setLang":"CN","safeSearch":"Off","textFormat":"Raw"}

        
        if self.searchEngine == 'google':
            querystring = {"query":query,"limit":self.ReturnCount,"related_keywords":"true"}
        
        
        # Requests
        response = requests.get(self.apiurl, headers=self.headers, params=querystring)
        data_list = response.json()['value']

        if len(data_list) == 0:
            return ""
        else:
            result_arr = []
            result_str = ""
            count_index = 0
            for i in range(self.ReturnCount):
                item = data_list[i]
                title = item["name"]
                description = item["description"]
                item_str = f"{title}: {description}"
                result_arr = result_arr + [item_str]

            result_str = "\n".join(result_arr)
            return result_str#, data_list
