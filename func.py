from pathlib import Path
import json


actTablePath = Path('gamedata/excel/activity_table.json')
stgTablePath = Path('gamedata/excel/stage_table.json')
zoneTablePath = Path('gamedata/excel/zone_table.json')
mainStoryPath = Path('gamedata/story/obt/main')
reviewPath = Path('gamedata/excel/story_review_table.json')
metaPath = Path('gamedata/excel/story_review_meta_table.json')

def getFile(p:Path): #获取p路径下所有文件路径
    return [x for x in p.iterdir() if not x.is_dir()]

def getFolder(p:Path):
    return [x for x in p.iterdir() if x.is_dir()]

def getLang(flds:list):
    return [x.stem for x in flds]

def getEvents(data_dir:Path, lang:str):
    with open(data_dir/lang/reviewPath, encoding='utf-8') as reviewFile:
        review = json.load(reviewFile)
    
    events = []
    for event in list(review):
        events.append(Event(data_dir, lang, event))
    
    return events

def getRecords(data_dir:Path, lang:str):
    events = getEvents(data_dir, lang)
    records = []
    for event in events:
        if 'story' in event.eventid:
            records.append(event)
    
    return records

def getMainline(data_dir:Path, lang:str):
    events = getEvents(data_dir, lang)
    records = []
    for event in events:
        if event.entryType == "MAINLINE":
            records.append(event)
    
    return records

def getAct(data_dir:Path, lang:str):
    events = getEvents(data_dir, lang)
    records = []
    for event in events:
        if "ACTIVITY" in event.entryType:
            records.append(event)
    
    return records

def getExtraAvg(data_dir:Path, lang:str):
    with open(data_dir/lang/metaPath, encoding='utf-8') as metaFile:
        meta = json.load(metaFile)
    
    extra_list = []
    extra_avgs = meta['actArchiveResData']['avgs']
    for extra in extra_avgs:
        extrainfo = extra_avgs[extra]
        story = ExtraStory(data_dir, lang, extrainfo)

        extra_list.append(story)

    return extra_list



class Event():
    """
    Basic class of ak event
    """

    def __init__(self, data_dir:Path, lang:str, eventid:str):
        self.root_dir = data_dir/lang
        self.lang = lang
        self.eventid = eventid
        with open(data_dir/lang/reviewPath, encoding='utf-8') as reviewFile:
            self.review = json.load(reviewFile)[eventid]
        self.entryType = self.review['entryType']
        self.name = self.review['name']
        self.storyList = self.review['infoUnlockDatas']


    def __getitem__(self, idx):
        return Story(self, self.storyList[idx])

    def __len__(self):
        return len(self.storyList)

class Story():
    """
    Class of indivisual story
    """
    def __init__(self, event:Event, storyData:dict):
        self.root_dir = event.root_dir
        self.lang = event.lang
        self.eventid = event.eventid
        self.eventName = event.name
        self.entryType = event.entryType
        self.storyData = storyData
        self.storyCode = storyData['storyCode']
        self.avgTag = storyData['avgTag'] if storyData['avgTag'] else ''
        self.storyName = storyData['storyName']
        self.storyInfo = self.root_dir/'gamedata/story/[uc]{}.txt'.format(storyData['storyInfo'])
        self.storyTxt = self.root_dir/'gamedata/story/{}.txt'.format(storyData['storyTxt'])
        self.f = storyData['storyTxt']

class ExtraStory():
    """
    Class of extra story
    """
    root_dir = ''
    lang = ''
    eventid = ''
    eventName = ''
    entryType = 'EXTRA'
    storyCode = ''
    avgTag = ''
    storyName = ''
    storyInfo = ''
    storyTxt = ''
    f = ''
    def __init__(self,root_dir, lang:str, extrainfo):
        self.root_dir = root_dir/lang
        self.lang = lang
        self.storyName = extrainfo['desc']
        if extrainfo["breifPath"]:
            self.storyInfo = self.root_dir/f'gamedata/story/[uc]{extrainfo["breifPath"]}.txt'
        elif extrainfo["rawBrief"]:
            self.storyInfo = None
            self.rawStoryInfo = extrainfo["rawBrief"]
        self.storyTxt = self.root_dir/f'gamedata/story/{extrainfo["contentPath"]}.txt'
        self.f = extrainfo["contentPath"]
