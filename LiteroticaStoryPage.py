from bs4 import BeautifulSoup
import urllib

class LiteroticaStoryPage():
    """Literotica Story Page"""

    __saveHeader = """<html>\r\n<title>{Title}</title>\r\n<body>\r\n"""

    __saveMemberLine = '<h1><a href="..\\memberPages\\member_{MemberID}.html">member #{MemberID}</a></h1><br>\r\n'

    __saveFooter = """</body>\r\n</html>"""

    def __init__(self):
        self.Title = None
        self.MemberID = 0
        self.FileName = None
        self.URL = None
        self.Category = None
        self.Title = None
        self.SecondaryLine = None
        self.Text = None
        
        self.__SavePath = None

        self.__isSeries = False
        self.__isSingleStory = False
        self.__isDownloaded = False
        self.__isParsed = False
        self.__PageCount = 0
    
    def DownloadAllPages(self):
        urlStream = urllib.urlopen(self.URL+"?page=1")
        html = urlStream.read()
        soup = BeautifulSoup(html)
        try:
            pageblock = soup.findAll("span",attrs={"class" :"b-pager-caption-t r-d45"})
            self.__PageCount = int(pageblock[0].contents[1].replace(" Pages:",""))
        except:
            return False

        storyText = soup.find("div",attrs={"class": "b-story-body-x x-r15"}).prettify() + "\r\n"
        if self.__PageCount != 1:
            for pageNum in xrange(2,self.__PageCount+1):
                urlStream = urllib.urlopen(self.URL+"?page="+str(pageNum))
                html = urlStream.read()
                soup = BeautifulSoup(html)
                storyText += soup.find("div",attrs={"class": "b-story-body-x x-r15"}).prettify() +"\r\n"
        self.Text = unicode(storyText,"utf-8")
        
        return True

    
    def WriteToDisk(self, contentDirectory):
        try:
            with self.CreateStoryPage(contentDirectory) as file:

                self.__WriteStoryPageHeader(file)
                self.__WriteStoryPageMemberLine(file)
                self.__WriteStoryPageText(file)
                self.__WriteStoryPageFooter(file)
        except:
            return False

        return True

    def __WriteStoryPageText(self,file):
        file.write(self.Text.encode("utf-8"))
        return

    def __WriteStoryPageFooter(self, file):
        file.write(self.__saveFooter)
        return

    def __WriteStoryPageMemberLine(self, file):
        memberLine = self.__saveMemberLine.replace("{MemberID}",str(self.MemberID))
        file.write(memberLine.encode("utf-8"))
        return

    def __WriteStoryPageHeader(self, file):
        storyPageHeader = self.__saveHeader.replace("{Title}", self.Title)
        file.write(storyPageHeader.encode("utf-8"))
        return

    def CreateStoryPage(self, contentDirectory):
        try:
            storyFilePath = contentDirectory + "\\storyPages\\" + self.FileName 
            file = open(storyFilePath,"w+")
        except:
            return None

        return file

    def RelativePath(self):
        return "../storyPages/" + self.FileName

    


