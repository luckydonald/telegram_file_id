# tg_file_id

Parse and construct Telegram `file_id`s and `unique_file_id`s.
Even generate a `unique_file_id` from a `file_id`.

### Examples below
- [Install](#install)
- [Parse `file_id`s](#parse-file-id-s)
- [Parse `file_unique_id`s](#parse-file-unique-id-s)
- [Convert `file_id`s to `file_unique_id`s](#convert-file-id-s-to-file-unique-id-s)

### Install
```bash
pip install tg-file-id
```

### Parse `file_id`s

```py
from tg_file_id.file_id import FileId

file_id = FileId.from_file_id('CAACAgIAAxkBAAIEol9yQhBqFnT4HXldAh31a-hYXuDIAAIECwACAoujAAFFn1sl9AABHbkbBA')
```

Now the `file_id` variable is an object like this: 
```py
DocumentFileId(
    file_id='CAACAgIAAxkBAAIEol9yQhBqFnT4HXldAh31a-hYXuDIAAIECwACAoujAAFFn1sl9AABHbkbBA',
    type_id=8,
    type_generic='document',
    type_detailed='sticker',
    dc_id=2,
    id=46033261910035204,
    access_hash=-5107925353769492667,
    version=4,
    sub_version=27,
)

```

### Parse `file_unique_id`s
```py
from tg_file_id.file_unique_id import FileUniqueId

unique_id = FileUniqueId.from_unique_id('AgADBAsAAgKLowAB')
```
Now the `unique_id` variable is an object like this:
```py
FileUniqueId(
    unique_id='AgADBAsAAgKLowAB',
    type_id=2,
    id=46033261910035204
)
```


### Convert `file_id`s to `file_unique_id`s
```py
from tg_file_id.file_id import FileId
from tg_file_id.file_unique_id import FileUniqueId

file_id = FileId.from_file_id('CAACAgIAAxkBAAIEol9yQhBqFnT4HXldAh31a-hYXuDIAAIECwACAoujAAFFn1sl9AABHbkbBA')
unique_id = FileUniqueId.from_file_id(file_id)
calculated_file_unique_id = unique_id.to_unique_id()
```

Now `calculated_file_unique_id` is
```py
'AgADBAsAAgKLowAB'
```
