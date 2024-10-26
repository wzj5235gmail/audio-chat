apt-get update
snap install docker
systemctl start docker

tar -xzvf audio-chat.tar.gz
rm -r /var/www/html/*
sudo mv -f frontend/build/* /var/www/html

apt-get install -y nginx
cat > /etc/nginx/sites-available/default <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    root /var/www/html;

    location / {
        try_files \$uri index.html;
    }:

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }

    location /voice_generate/ {
        proxy_pass https://abfe-50-98-76-235.ngrok-free.app;
    }
}
EOF
systemctl restart nginx

cd /home/ubuntu
docker login -u wzj5235 -p WzJ264288194
docker compose up