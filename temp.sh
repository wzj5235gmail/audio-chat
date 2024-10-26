cd frontend
npm run build
cd ..
tar -czvf audio-chat.tar.gz frontend\build
scp -i "C:\Users\Administrator\Downloads\aws241017.pem" audio-chat.tar.gz ubuntu@54.177.147.104:/home/ubuntu/audio-chat.tar.gz










tar -xzvf audio-chat.tar.gz
rm -r /var/www/html/*
sudo mv -f frontend/build/* /var/www/html


