# How ASTR Parse Raw Story Text

## Arknights Raw Story Text

The Arknights raw story text are constructed by lines containing the following parts:

```
[prop(attr1=value1, attr2=value2, ...)] content
```

Those `prop` and `attr` are case-insensitve. Sometimes the `prop` can be ignored, left only `name` attribute in it:

```
[name="..."] content
```

or ignore the name too:

```
content
```

in the case above, ASTR will convert them into:

```
[name(name="...")] content
[name(name="")] content
```

So for every story line, the `reader` funtion in `jsonconvert.py` will parse them into:

```jsonc
{
    "id": 1,     // the original line index in raw file
    "prop": "...",
    "attributes": {
        "name": "...",  
        "content": "...",
        "attr1": "value1",
        "attr2": "value2"
        // ...
    }
}
```

## Wordcount Rule

To get accurate wordcount, ASTR won't use the size of raw file as wordcount. Instead, ASTR will only count valid strings in the following attributes:

- all `content` & `text` attributes
- `option` attribute in `decision` prop with semicolomn removed

Note that `name` attribute are shown in ASTR but won't be counted, since the `name` are mostly duplicated.

For CN&JP&KR servers, the wordcount or character count, are simply the length of strings. While for EN server, the wordcount are computed by counting the size of string array splited by space.
