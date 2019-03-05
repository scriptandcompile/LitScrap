from bs4 import BeautifulSoup
import urllib
import LiteroticaStoryPage



class LiteroticaMemberPage():
    """
    A Literotica member page.
    Allows for downloading, parsing, getting story pages, and saving.
    """
    
    # Stuff an id in between these two lines to get a valid member URL request.
    # Still have to check to see if the member page is valid by downloading it.
    __memberSubmissionBase = "http://www.literotica.com/stories/memberpage.php?uid="
    __memberSubmissionEnding = """&page=submissions"""

    # Story series row match
    __storySeriesTitleClass = {"class" : "ser-ttl"}
    __storySeriesTitleTag = "tr"

    # Story row match
    __storyTitleClass = {"class" : "root-story r-ott"}
    __storyTitleTag = "tr"

    # Story row match within Series
    __storySeriesIndividualTitleClass = {"class" : "sl"}
    __storySeriesIndividualTitleTag = "tr"
     
    # __save* items are used when saving member pages to disk.
    # Member page header for saving to disk.
    __saveHeader = """<html>\r\n<title>{MemberPageTitle}</title>\r\n<body>\r\n"""

    # Member page series title line for saving to disk.
    __saveSeriesTitleEntry = """<br><strong>{SeriesTitle}</strong><br>\r\n"""    
    
    # Member page individual story line for saving to disk.
    __saveIndividualStoryEntry = """<a href="{StoryLink}">{StoryTitle}</a> - {StorySecondaryLine} - {StoryCategory}<br>\r\n"""
    
    # Member page series story line for saving to disk.
    # Making it the same as individual story lines currently but
    # offers some future options to change this.
    __saveSeriesStoryEntry = __saveIndividualStoryEntry

    # Member page foot for saving to disk.
    __saveFooter = """</body>\r\n</html>\r\n"""

    def __init__(self, memberID):
        self.__html = None
        self.__soup = None
        self.__seriesIsParsed = False
        self.__singleStoriesIsParsed = False
        self.__isLoaded = False
        self.__isValidMemberPage = False

        self.MemberPageURL = LiteroticaMemberPage.FormMemberPageURL(memberID)
        self.MemberID = memberID
        self.SeriesStories = []
        self.IndividualStories = []

    def IsValidMemberPage(self):
        return self.__isValidMemberPage

    def IsLoaded(self):
        return self.__isLoaded

    def IsParsed(self):
        return self.IsSeriesParsed() and self.IsSingleStoriesParsed()

    def IsSeriesParsed(self):
        return self.__seriesIsParsed

    def IsSingleStoriesParsed(self):
        return self.__singleStoriesIsParsed

    def DownloadMemberPage(self):
        try:
            urlStream = urllib.urlopen(self.MemberPageURL)
            self.__html = urlStream.read()
            self.__soup = BeautifulSoup(self.__html)
        except:
            return False

        self.__isLoaded = True

        if "Literotica.com - error" in self.__soup.title.string:
            return False
        
        self.__isValidMemberPage = True
        
        try:
            self.ParseAllStories()
        except:
            return False

        return self.IsParsed()

    def ParseAllStories(self):
        try:
            self.ParseSingleStories()
            self.__singleStoriesIsParsed = True

            self.ParseSeriesStories()
            self.__seriesIsParsed = True

        except:
            return False

        return True

    def ParseSingleStories(self):
        SingleStoryResults = self.__soup.findAll(LiteroticaMemberPage.__storyTitleTag,attrs=LiteroticaMemberPage.__storyTitleClass)
        self.IndividualStories = self.__ParseStoryResultForStoryLines(SingleStoryResults)
        return

    def __GetSeriesTitleBlocks(self):
        seriesStoryTitleBlocks = self.__soup.findAll(LiteroticaMemberPage.__storySeriesTitleTag,attrs= LiteroticaMemberPage.__storySeriesTitleClass)
        return seriesStoryTitleBlocks

    def SeriesTitles(self):
        seriesStoryTitleBlocks = self.__GetSeriesTitleBlocks()
        seriesTitles = []
        for storiesSeries in seriesStoryTitleBlocks:
            seriesTitle = storiesSeries.text
            seriesTitles += seriesTitle

        return seriesTitles

    def __ParseSeriesStoriesFromTitleBlocks(self, storiesSeriesBlock):
        rowSibling = storiesSeriesBlock.nextSibling
        thisSeriesStories = []

        # get the next rows on until we no longer have rows or
        # we find a row that is not a series story class
        while rowSibling != None and rowSibling.name == "tr" and rowSibling.attrs["class"] == LiteroticaMemberPage.__storySeriesIndividualTitleClass["class"]:
            thisSeriesStories += self.__ParseStoryResultForStoryLines([rowSibling])
            rowSibling = rowSibling.nextSibling

        return thisSeriesStories

    def ParseSeriesStories(self):
        seriesStoryTitleBlocks = self.__GetSeriesTitleBlocks()
        allSeriesStories = []
        for storiesSeriesBlock in seriesStoryTitleBlocks:
            seriesTitle = storiesSeriesBlock.text
            
            thisSeriesStories = self.__ParseSeriesStoriesFromTitleBlocks(storiesSeriesBlock)

            for story in thisSeriesStories:
                story.SeriesTitle = seriesTitle
        
            allSeriesStories += [(seriesTitle,thisSeriesStories)]

        self.SeriesStories = allSeriesStories
        return 

    def CreateMemberPage(self, contentDirectory):
        try:
            memberFileName = "member_"+str(self.MemberID)+ ".html"
            memberFilePath = contentDirectory + "\\memberPages\\" + memberFileName
            file = open(memberFilePath,"w+")
        except:
            return None

        return file

    def HasStories(self):
        if len(self.SeriesStories) != 0 or len(self.IndividualStories) != 0:
            return True
        else:
            return False

    def WriteToDisk(self, contentDirectory):
        if not self.IsLoaded() or not self.IsParsed() or not self.IsValidMemberPage():
            return False
        try:
            with self.CreateMemberPage(contentDirectory) as file:
                file.write(self.__saveHeader.replace("{MemberPageTitle}" ,"Member #"+str(self.MemberID)))

                for storyEntry in self.IndividualStories:
                    self.__WriteIndividualStoryLine(file,storyEntry)


                for seriesEntry in self.SeriesStories:
                    self.__WriteSeriesTitleLine(file, seriesEntry[0])
                    for seriesIndividualStory in seriesEntry[1]:
                        self.__WriteSeriesStoryLine(file, seriesIndividualStory)

                file.write(self.__saveFooter)
        except:
            return False

        return True

    def __WriteSeriesTitleLine(self, file, seriesTitle):
        entryLine = self.__saveSeriesTitleEntry
        entryLine = entryLine.replace("{SeriesTitle}",seriesTitle)
        file.write(entryLine.encode("utf-8"))

    def __WriteIndividualStoryLine(self, file, storyEntry):
        entryLine = self.__saveIndividualStoryEntry
        entryLine = entryLine.replace("{StoryLink}",storyEntry.RelativePath())
        entryLine = entryLine.replace("{StoryTitle}",storyEntry.Title)
        entryLine = entryLine.replace("{StorySecondaryLine}",storyEntry.SecondaryLine)
        entryLine = entryLine.replace("{StoryCategory}",storyEntry.Category)
        file.write(entryLine.encode("utf-8"))
        return

    def __WriteSeriesStoryLine(self, file,storyEntry):
        entryLine = self.__saveSeriesStoryEntry
        entryLine = entryLine.replace("{StoryLink}",storyEntry.RelativePath())
        entryLine = entryLine.replace("{StoryTitle}",storyEntry.Title)
        entryLine = entryLine.replace("{StorySecondaryLine}",storyEntry.SecondaryLine)
        entryLine = entryLine.replace("{StoryCategory}",storyEntry.Category)
        file.write(entryLine.encode("utf-8"))
        return

    @staticmethod
    def FormMemberPageURL(memberID):
        return LiteroticaMemberPage.__memberSubmissionBase + str(memberID) + LiteroticaMemberPage.__memberSubmissionEnding

    
    def __ParseStoryResultForStoryLines(self, storyResults):
        stories = []
        
        for result in storyResults:
            storyFileName = ""
            storyWebLink = ""
            storyTitle = ""

            subElements = result.findAll('td')

            if len(subElements) == 0:
                continue

            storyPage = LiteroticaStoryPage.LiteroticaStoryPage()
            storyPage.URL = subElements[0].find("a")["href"]
            if "showstory.php?id=" in storyPage.URL:
                storyPage.FileName = storyPage.URL.split("showstory.php?id=")[1] + ".html"
            else:
                storyPage.FileName = storyPage.URL.split("/")[-1] + ".html"
            storyPage.MemberID = self.MemberID
            storyTitleLine = subElements[0].text
            if u"\xa0" in storyTitleLine:
                storyTitleLine = storyTitleLine.split(u"\xa0")[0]
                storyTitleLine = storyTitleLine.replace("//","")
                storyTitleLine.strip()

            storyPage.Title = storyTitleLine
            storyPage.Category = subElements[2].find("a").find("span").text
            storyPage.SecondaryLine = subElements[1].text
            storyPage.Date = subElements[3].text
            stories.append(storyPage)

        return stories
