sudo cp main_config.service /etc/systemd/system/main_config.service

sudo systemctl daemon-reload

sudo systemctl start main_config
sudo systemctl enable main_config
