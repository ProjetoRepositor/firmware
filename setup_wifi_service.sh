sudo cp wifi_config.service /etc/systemd/system/wifi_config.service

sudo systemctl daemon-reload

sudo systemctl start wifi_config
sudo systemctl enable wifi_config
