from ebooklib import epub
from pathlib import Path
from jsonconvert import reader
from typing import Iterable

import json
import re

import func

EPUB_CHAPTER_TEMPLATE = """<html>
  <head>
    <meta charset="UTF-8" />
    <title>{story.storyCode} {story.storyName} {story.avgTag}</title>
  </head>
  <body>
    {lines}
  </body>
</html>"""

DOCTOR = "Doctor"

EPUB_NAME_TEMPLATE = '<p id="{index}"><strong>{name}</strong>&emsp;{content}</p>'

EPUB_BRANCH_TEMPLATE = '<li><a href="#{index}">{option}</a></li>'


def parseContent(content: str, doctor=DOCTOR) -> str:
    color_re = re.compile(r"<color=([\w#]+)>(.+?)<\/color>", re.MULTILINE)
    nbsp_sub_before = re.compile(r"(\s+)(<\/?\w+>)", re.MULTILINE)
    nbsp_sub_after = re.compile(r"(<\/?\w+>)(\s+)", re.MULTILINE)
    content = content.replace("{@nickname}", doctor)
    content = re.sub(r"(?:\r\n|\r|\n|\\n|\\r)", "<br>", content)
    content = color_re.sub(r'<span style="color:\1">\2</span>', content)
    content = nbsp_sub_before.sub(r"&nbsp;\2", content)
    content = nbsp_sub_after.sub(r"\1&nbsp;", content)
    return content


def parseHTML(story_json):
    lines = []
    rawlist = story_json["storyList"]
    for lidx, line in enumerate(rawlist):
        index = line["id"]
        prop: str = line["prop"].lower()
        attrs = line["attributes"]

        if prop == "name":
            lines.append(
                EPUB_NAME_TEMPLATE.format(
                    index=f'line{index}',
                    name=attrs.get('name',''), content=parseContent(attrs.get("content", ""))
                )
            )
        
        if prop == 'multiline':
            lines.append(
                EPUB_NAME_TEMPLATE.format(
                    index=f'line{index}',
                    name=attrs.get('name',''), content=parseContent(attrs.get("content", ""))
                )
            )
        
        if prop == 'decision':
            options = attrs['options'].split(';')
            values = attrs['values'].split(';')
            targetLines = line['targetLine']
            options_html = []
            for i in range(min(len(values),len(options))):
                options_html.append(EPUB_BRANCH_TEMPLATE.format(index=targetLines.get(f'option{values[i]}',f'{index+1}'), option=options[i]))
            lines.append(
                '<p id="line{index}">\n<ol>\n{options}\n</ol>\n</p>'.format(index=index, options='\n'.join(options_html))
            )
        
        if prop == 'predicate':
            if line.get('endOfOpt'):
                lines.append('<p id="line{index}">---End of Options---</p>'.format(index=index))
            else:
                lines.append('<p id="line{index}">---{option}---</p>'.format(index=index,option=attrs['references'].replace(';', '&')))

        if prop == 'subtitle':
            lines.append('<br/><p id="line{index}">{content}</p><br/>'.format(index=index, content=parseContent(attrs.get('text', ''))))

        if prop == 'sticker':
            lines.append('<br/><p id="line{index}"><strong>{content}</strong></p>'.format(index=index, content=parseContent(attrs.get('text', ''))))

        if prop == 'stickerclear':
            lines.append('<br/>')

        if prop == 'image':
            lines.append('<p id="line{index}">{content}</p>'.format(index=index, content=attrs.get('image', '')))


    return lines
        



DATA_PATH = Path(r"D:\zf-py\ArknightsStoryJson")

lang = "zh_CN"
epub_lang = lang.replace("_", "-")
event_id = "act40side"
event: Iterable[func.Story] = func.Event(DATA_PATH, lang, event_id)

file_name = f"{event.eventid}_{event.name}.epub"

book = epub.EpubBook()
book.set_identifier(f"{event.eventid} {lang}")
book.set_title(event.name)
book.set_language(epub_lang)
book.add_author("HyperGryph")

chapters = []
for idx, story in enumerate(event):
    chapter = epub.EpubHtml(
        title=f"{story.storyCode} {story.storyName} {story.avgTag}",
        file_name=f"{story.storyCode}_{story.storyName}_{story.avgTag}.xhtml",
        lang=epub_lang,
    )
    with open(story.storyTxt.with_suffix(".json"), encoding="utf-8") as f:
        story_json = json.load(f)

    lines = parseHTML(story_json)
    chapter.content = EPUB_CHAPTER_TEMPLATE.format(story=story, lines="\n".join(lines))
    with open(f'htmls/{chapter.file_name}', 'w', encoding='utf-8') as f:
        f.write(chapter.content)
    book.add_item(chapter)
    chapters.append(chapter)

book.toc = chapters
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

style = '''
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
}

h2 {
     text-align: left;
     text-transform: uppercase;
     font-weight: 200;     
}

ol {
        list-style-type: none;
}

ol > li:first-child {
        margin-top: 0.3em;
}


nav[epub|type~='toc'] > ol > li > ol  {
    list-style-type:square;
}


nav[epub|type~='toc'] > ol > li > ol > li {
        margin-top: 0.3em;
}

'''

# add css file
nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
book.add_item(nav_css)

book.spine = ["nav"] + chapters

epub.write_epub(file_name, book, {})
