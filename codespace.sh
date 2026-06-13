# using light yellow color
echo -e "\033[1;33m Initializing... \033[0m"
pip install openpyxl > /dev/null 2>&1
echo -e "\033[1;33m Downloading latest data... \033[0m"
git clone https://github.com/Kengxxiao/ArknightsGameData.git
# using light green color
echo -e "\033[1;32m Initialization complete. \033[0m"
echo -e "\033[1;33m Available servers:\033[0m zh_CN, en_US, ko_KR, ja_JP, zh_TW"
echo -e "Enter the server you want to use, press Enter to continue, Blank for zh_CN: "
read server
if [ -z "$server" ]; then
    server="zh_CN"
fi

echo -e "Current Server: \033[1;33m $server\033[0m"
python xlsxconvert.py -E -L $server
index_count=$(SERVER="$server" python - <<'PY'
from pathlib import Path
import os
import func

server = os.environ["SERVER"]
data_dir = Path('ArknightsGameData')
print(len(func.getAct(data_dir, server)) + len(func.getMainline(data_dir, server)))
PY
)
echo -e "\033[1;32m Available indexes: $index_count \033[0m"
echo -e "\033[1;32m Enter the index of the event you want to export, or type \033[1;33mall\033[0m\033[1;32m to export every index: \033[0m"

read event
if [ "$event" = "all" ]; then
    if [ "$index_count" -gt 0 ]; then
        for i in $(seq 0 $((index_count - 1))); do
            python xlsxconvert.py -e $i -i -L $server
        done
        echo -e "\033[1;32m All events exported. \033[0m"
    else
        echo -e "\033[1;31m No indexes available to export. \033[0m"
    fi
else
    python xlsxconvert.py -e $event -i -L $server
fi

# tell user how to download the file in codespace
echo -e "\033[1;32m To download the file in code space. Right click the file and select "download"  \033[0m"

