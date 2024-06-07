from ast import arg
from itertools import count
import re
import argparse
from pathlib import Path
import os
import func
import json

prRe = r"^(?:\[(?P<prop>\w+).*?\])?(?P<content>.*)$"
pmRe = r"(?:(?P<attr>\w+)\s*=\s*(?P<value>\".+?\"|\'.+?\'|[\d\.]+|\w+),?\s{,3})"
characters = []
codes = []
characterFlag = False
commentFlag = False
infoFlag = False



def reader(story):
    
    if isinstance(story,func.Story) or isinstance(story,func.ExtraStory):
        with open(story.storyTxt, encoding='utf-8') as txtFile:
            rawstorytext = txtFile.read()
        storydict = {}
        storydict['lang'] = story.lang
        storydict['eventid'] = story.eventid
        storydict['eventName'] = story.eventName
        storydict['entryType'] = story.entryType
        storydict['storyCode'] = story.storyCode
        storydict['avgTag'] = story.avgTag
        storydict['storyName'] = story.storyName
        counter = 0
        COUNTER_FLAG = True
        if story.storyInfo:
            with open(story.storyInfo, encoding='utf-8') as txtFile:
                storydict['storyInfo'] = txtFile.read()
        elif getattr(story,'rawStoryInfo',None):
            storydict['storyInfo'] = story.rawStoryInfo
        else:
            storydict['storyInfo'] = ''
    if isinstance(story, str):
        rawstorytext = story
        storydict = {}
        COUNTER_FLAG = False

    OPTIONTRACE = True
    rawstorylist = rawstorytext.split('\n')
    storylines = len(rawstorylist)
    rawlist = []
    currentOptions = {}
    usedOptions = {}
    multiline_buffer = []
    last_multiline = None
    characterStack = {}
    crt_char = None

    for (index, line) in enumerate(rawstorylist):
        d = {}
        d['id'] = index
        if '//' in line:
            d['prop'] = 'Comment'
            d['attributes'] = {}
            d['attributes']['value'] = line.lstrip('//')
            continue
        prop,content = re.match(prRe, line).group('prop','content')
        d['prop'] = prop
        d['attributes'] = {}
        parameters = re.findall(pmRe, line)
        if prop == 'name' or prop == '' or prop == None:
            prop = 'name'
            d['prop'] = 'name'
            d['attributes']['content'] = content
            if COUNTER_FLAG:
                counter += len(content.split()) if story.lang == 'en_US' else len(content)
        

            


        if len(parameters):
            for (attr, value) in parameters:
                try:
                    value = float(value)
                except ValueError:
                    if value[0] == '"' or value[0] == "'":
                        value = value[1:-1]
                d['attributes'][attr] = value
                if attr == 'image':
                    imgtype = prop.lower()
                    if imgtype == "backgroundtween":
                        imgtype = "background"
                    elif imgtype == 'showitem':
                        imgtype = 'item'
        
        if prop == 'multiline':
            d['attributes']['content'] = content
            multiline_buffer.append(content)
            if COUNTER_FLAG:
                counter += len(content.split()) if story.lang == 'en_US' else len(content)
            last_multiline = d
            if d['attributes'].get('end') == 'true':
                joined_line = ''.join(multiline_buffer)
                multiline_buffer = []
                d['attributes']['joined'] = joined_line


        if prop.lower() == 'decision':
            d['targetLine'] = {}
            options = d['attributes']['options'].split(';')
            if COUNTER_FLAG:
                for option in options:
                    counter += len(content.split()) if story.lang == 'en_US' else len(content)
            values = [f"option{value}" for value in d['attributes']['values'].split(';')]
            if OPTIONTRACE:
                for idx,value in enumerate(values[:len(options)]):
                    currentOptions[value] = {'option':options[idx], 'Decision':index}
                    d['targetLine'][value] = ''

        if prop.lower() == 'predicate':
            if not d['attributes'].get('references'):
                d['attributes']['references'] = ';'.join([i.lstrip('option') for i in usedOptions.keys()])
            if OPTIONTRACE:
                try:
                    for ref in d['attributes']['references'].split(';'):
                        if f'option{ref}' in currentOptions:
                            dec = currentOptions[f'option{ref}']['Decision']
                            rawlist[dec]['targetLine'][f'option{ref}'] = f'line{index}'
                            del currentOptions[f'option{ref}']
                            usedOptions[f'option{ref}'] = f'line{index}'
                            d['endOfOpt'] = False
                        else:
                            lastPredicate = int(usedOptions[f'option{ref}'].lstrip('line'))
                            rawlist[lastPredicate]['targetLine'] = f'line{index}'
                            d['endOfOpt'] = True
                            del usedOptions[f'option{ref}']
                except:
                    print(f'Disable Optiontrace From Line {index}!')
                    OPTIONTRACE = False

        if prop.lower() == 'character' or prop.lower() == 'charslot':
            if not d['attributes'].get('name'):
                characterStack = {}
                crt_char = None
            else:
                if d['attributes'].get('name'):
                    if d['attributes'].get('slot'):
                        characterStack[d['attributes']['slot']] = d['attributes']['name']
                    else:
                        characterStack['1'] = d['attributes']['name']
                
                if d['attributes'].get('name2'):
                    characterStack['2'] = d['attributes']['name2']


                if d['attributes'].get('focus'):
                    if not type(d['attributes'].get('focus')) == str:
                        focus = str(int(d['attributes']['focus']))
                    else:
                        focus = d['attributes']['focus']
                    if not focus.lower() == 'none':
                        crt_char = characterStack.get(focus)
                elif len(characterStack) == 1:
                    crt_char = list(characterStack.values())[0]

        if prop.lower() == 'name':
            if d['attributes'].get('name') and crt_char:
                    d['figure_art'] = crt_char



        if d['attributes'].get('text'):
            if COUNTER_FLAG:
                counter += len(content.split()) if story.lang == 'en_US' else len(content)
        
        
        rawlist.append(d)

    storydict['storyList'] = rawlist
    storydict['OPTIONTRACE'] = OPTIONTRACE
    if COUNTER_FLAG:
        return storydict, counter
    else:
        return storydict


if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--all',action='store_true',help="Update all json file or not")
    parser.add_argument('-o', '--offline', action='store_true', help="Offline mode, disable git update.")

    args = parser.parse_args()

    UPDATE_ALL = args.all

    OFFLINE = args.offline
    
    if not OFFLINE:
        import subprocess
        import time
        import urllib.request
        subprocess.run('git config --global user.email "050644zf@outlook.com"',shell=True)
        subprocess.run('git config --global user.name "Nightsky"', shell=True)
        if not Path('ArknightsStoryJson').is_dir():
            subprocess.run('git clone https://github.com/050644zf/ArknightsStoryJson.git', shell=True)

    with open('ArknightsStoryJson/log.json', encoding='utf-8') as logFile:
        logData = json.load(logFile)

    
    if not UPDATE_ALL and not OFFLINE:
        with urllib.request.urlopen('https://api.github.com/repos/Kengxxiao/ArknightsGameData/commits') as f:
            content = f.read()
        content = json.loads(content)
        latest = content[0]["commit"]["author"]["date"]
        latest_CN = time.mktime(time.strptime(latest,"%Y-%m-%dT%H:%M:%SZ"))

        with urllib.request.urlopen('https://api.github.com/repos/Kengxxiao/ArknightsGameData_YoStar/commits') as f:
            content = f.read()
        content = json.loads(content)        
        latest = content[0]["commit"]["author"]["date"]
        latest_global = time.mktime(time.strptime(latest,"%Y-%m-%dT%H:%M:%SZ"))

        latest = max(latest_CN,latest_global)

        if latest>logData["latestCommitTime"]:
            logData["latestCommitTime"] = latest
            with open('ArknightsStoryJson/log.json','w', encoding='utf-8') as logFile:
                json.dump(logData,logFile)
        else:
            print("No new commit detected from ArknightsGameData, skip the update.")
            exit()


    # if not Path('ArknightsGameData').is_dir():
    #     subprocess.run('git clone https://github.com/Kengxxiao/ArknightsGameData.git', shell=True)

    # else:
    #     os.chdir('ArknightsGameData')
    #     subprocess.run('git fetch', shell=True)
    #     subprocess.run('git pull', shell=True)
    
    #     os.chdir('..')

    langs = ['zh_CN']
    langs += [i.stem for i in Path('ArknightsGameData_YoStar').iterdir() if i.is_dir() and not '.' in i.name]
    
    jsonDataPath = Path('ArknightsStoryJson')

    for lang in langs:

        dataPath = Path('ArknightsGameData') if lang == 'zh_CN' else Path(f'ArknightsGameData_YoStar')

        print(f'Server: {lang}')
        
        # load characters data
        with open(dataPath/ f'{lang}/gamedata/excel/character_table.json', encoding='utf-8') as jsonFile:
            characterData = json.load(jsonFile)
        
        with open(dataPath/f'{lang}/gamedata/excel/uniequip_table.json', encoding='utf-8') as jsonFile:
            equipData = json.load(jsonFile)
            equipDict = equipData['equipDict']

        with open(dataPath/f'{lang}/gamedata/excel/handbook_info_table.json', encoding='utf-8') as jsonFile:
            handbookData = json.load(jsonFile)['handbookDict']

        with open(dataPath/f'{lang}/gamedata/excel/char_patch_table.json', encoding='utf-8') as jsonFile:
            amiyaFile = json.load(jsonFile)
            amiyaData = amiyaFile['patchChars']
            amiyas = amiyaFile['infos']['char_002_amiya']['tmplIds']
            

        # legacy file, keep it for safety
        charDict = {}

        for cid in characterData:
            if cid.split('_')[0] == 'char':
                cidx = cid.split('_')[1]
                cin = cid.split('_')[2]
                charDict[cin] = {'name':characterData[cid]['name'],'id':cidx}

        
        # new file, use this for future
        charInfo = handbookData

        get_properties = ['name','rarity','profession','nationId', 'displayNumber', 'appellation', 'itemUsage', 'itemDesc']

        for cid in characterData:
            # if characterData[cid]['isNotObtainable']:
            #     continue
            if cid == 'char_002_amiya':
                for amiya in amiyas:
                    charInfo[amiya] = charInfo[cid].copy()
                    charInfo[amiya]['charID'] = amiya
                    if amiya == cid:
                        for prop in get_properties:
                                charInfo[cid][prop] = characterData[cid][prop]
                    else:
                        for prop in get_properties:
                            charInfo[amiya][prop] = amiyaData[amiya][prop]
                    stories = []
                    for story in charInfo[amiya]['storyTextAudio']:
                        if not story['stories'][0].get('patchIdList'):
                            stories.append(story)
                        elif amiya in story['stories'][0]['patchIdList']:
                            stories.append(story)
                    
                    charInfo[amiya]['storyTextAudio'] = stories
                    charInfo[amiya]['equips'] = []

            else:
                try:
                    for prop in get_properties:
                        charInfo[cid][prop] = characterData[cid][prop]
                    charInfo[cid]['equips'] = []
                except KeyError:
                    continue


        for char, equips in equipData['charEquip'].items():
            for equip_id in equips:
                try:
                    charInfo[char]['equips'].append(equipDict[equip_id])
                except KeyError:
                    continue
            
        


        events = func.getEvents(dataPath, lang)
        with open(f'ArknightsStoryJson/{lang}/storyinfo.json',encoding='utf-8') as jsonFile:
            storyInfo = json.load(jsonFile)

        with open(f'ArknightsStoryJson/{lang}/wordcount.json',encoding='utf-8') as jsonFile:
            wordCount = json.load(jsonFile)

        with open(f'ArknightsStoryJson/{lang}/extrastory.json',encoding='utf-8') as jsonFile:
            extraInfo = json.load(jsonFile)
        
        for event in events:
            if not wordCount.get(event.eventid):
                wordCount[event.eventid] = {}

            for story in event:
                storyPath = Path(story.storyTxt)
                jsonPath = jsonDataPath/storyPath.relative_to(dataPath).parent/Path(str(storyPath.stem)+'.json')
                if jsonPath.exists() and not UPDATE_ALL:
                    continue


                jsonPath.parent.mkdir(exist_ok=True, parents=True)
                try:
                    storyJson,counter = reader(story)
                    storyInfo[str(story.f)] = storyJson['storyInfo']
                except FileNotFoundError:
                    continue

                
                with open(jsonPath, 'w', encoding='utf-8') as jsonFile:
                    json.dump(storyJson,jsonFile, indent=4, ensure_ascii=False)
                    print(f'File {jsonPath} exported!')
                
                wordCount[event.eventid][str(story.f)] = counter

        try:
            extra_list = func.getExtraAvg(dataPath, lang)
            extraInfo["extra"] = []
            for extra in extra_list:
                storyPath = Path(extra.storyTxt)
                jsonPath = jsonDataPath/storyPath.relative_to(dataPath).parent/Path(str(storyPath.stem)+'.json')

                jsonPath.parent.mkdir(exist_ok=True, parents=True)
                try:
                    storyJson,counter = reader(extra)
                    storyInfo[str(extra.f)] = storyJson['storyInfo']
                except FileNotFoundError:
                    continue

                with open(jsonPath, 'w', encoding='utf-8') as jsonFile:
                    json.dump(storyJson,jsonFile, indent=4, ensure_ascii=False)
                    print(f'File {jsonPath} exported!')

                extraInfo["extra"].append({
                    "storyName": extra.storyName,
                    "storyTxt": extra.f,
                })
            
        except:
            print('No extra story found!')








        with open(f'ArknightsStoryJson/{lang}/chardict.json','w',encoding='utf-8') as jsonFile:
            json.dump(charDict, jsonFile, indent=4, ensure_ascii=False)
            print(f'Character Data exported!')

        with open(f'ArknightsStoryJson/{lang}/charinfo.json','w',encoding='utf-8') as jsonFile:
            json.dump(charInfo, jsonFile, indent=4, ensure_ascii=False)
            print(f'Character Info Data exported!')

        with open(f'ArknightsStoryJson/{lang}/storyinfo.json','w',encoding='utf-8') as jsonFile:
            json.dump(storyInfo, jsonFile, indent=4, ensure_ascii=False)
            print(f'StoryInfo Data exported!')

        with open(f'ArknightsStoryJson/{lang}/wordcount.json','w',encoding='utf-8') as jsonFile:
            json.dump(wordCount, jsonFile, indent=4, ensure_ascii=False)
            print(f'WordCount Data exported!')

        with open(f'ArknightsStoryJson/{lang}/extrastory.json','w',encoding='utf-8') as jsonFile:
            json.dump(extraInfo, jsonFile, indent=4, ensure_ascii=False)
            print(f'ExtraStory Data exported!')


    
    
    if not OFFLINE:
        os.chdir('ArknightsStoryJson')
        subprocess.run('git fetch', shell=True)
        subprocess.run('git pull', shell=True)
        subprocess.run('git add -A', shell=True)
        subprocess.run(f'git commit -m {time.strftime("%Y%m%d")}', shell=True)
        print(f'Commit {time.strftime("%Y%m%d")} has created!')
        os.chdir('..')

    print('Update Success!')


    
                

