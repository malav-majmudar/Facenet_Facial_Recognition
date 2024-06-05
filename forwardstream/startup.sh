#!/bin/bash
sleep 5 
#check internet connectivity and setting up access point if needed
wifi=$(iwgetid -r)

echo "$wifi"

if [ -n "$wifi" ]; then
    echo "There is a WiFi Connection..."
else
    echo "There are no WiFi Connections, starting access point"
    sudo wifi-connect
fi



#run forward stream file
cd forwardstream/
nohup python forward.py &
sleep 5

#tunnel
cloudflared --url http://127.0.0.1:8002 > output.txt 2>&1 &
python find.py
sleep 5


#run malav file
cd ../Facenet_Facial_Recognition/
nohup python main.py &
sleep 15


#run driver code
cd ../driver/
python visage-driver.py


exit 0