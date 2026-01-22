# using light yellow color
echo -e "\033[1;33m Initializing... \033[0m"
pip install openpyxl > /dev/null 2>&1
# using light green color
echo -e "\033[1;32m Initialization complete. \033[0m"
echo -e "\033[1;33m Available servers:\033[0m zh_CN, en_US, ko_KR, ja_JP, zh_TW"
echo -e "Enter the server you want to use, press Enter to continue, Blank for zh_CN: "
read server
echo -e "\033[1;33m Downloading latest data... \033[0m"
if [ -z "$server" ]; then
    server="zh_CN"
    git clone https://github.com/Kengxxiao/ArknightsGameData.git
else
    server=$server
    # only pull the $server folder from Kengxxiao/ArknightsGameData_YoStar
    git clone --depth 1 --filter=blob:none --sparse https://github.com/Kengxxiao/ArknightsGameData_YoStar.git
    cd ArknightsGameData_YoStar
    git sparse-checkout init --cone
    git sparse-checkout set $server
    cd ..
    mv ArknightsGameData_YoStar/$server ArknightsGameData
fi

echo -e "Current Server: \033[1;33m $server\033[0m"
python xlsxconvert.py -E -L $server
echo -e "\033[1;32m Enter the index of the event you want to export: \033[0m"

read event
python xlsxconvert.py -e $event -i -L $server

# tell user how to download the file in codespace
echo -e "\033[1;32m To download the file in code space. Right click the file and select "download"  \033[0m"

