# ЧЕКЕР ПИРОВ

В папке `checker` находится Python-скрипт для массовой проверки состояния пиров.  
1. В файл `peers.txt` закидываем PeerID ваших нод (например, `QmUJ56hG1pxfwFeR7MX...`).  
2. Запускаем скрипт

---

# АВТО-РЕСТАРТ НОДЫ

1. **Заменяем** файл `run_rl_swarm.sh` в папке с нодой на файл из папки `runner` любым удобным способом.

2. **Редактируем** `run_rl_swarm.sh`:
   ```
   nano run_rl_swarm.sh
   ```
   - В самом начале файла изменяем параметры ноды на нужные.  
     По умолчанию установлено:  
     ```
     Math, 0.5B
     ```
     Это подходит для CPU-ноды.  
   - Чтобы сохранить изменения и выйти из редактора `nano`:
     - Нажать `CTRL + O` (сохранить)
     - Нажать `Enter`
     - Нажать `CTRL + X` (выйти)

3. **Даем права на исполнение**:
   ```
   chmod +x run_rl_swarm.sh
   ```

4. **Запускаем ноду вручную** (чтобы проверить, что всё правильно настроено и создать необходимые файлы):
   ```
   ./run_rl_swarm.sh
   ```

5. После полного запуска **останавливаем** процесс:
   - Нажать `CTRL + C`

6. **Создаем системный сервис** для авто-перезапуска ноды. Выполняем команду:
   ```
   sudo tee /etc/systemd/system/rl_swarm.service > /dev/null <<'EOF'
   [Unit]
   Description=RL-Swarm training (GSM8K) – venv
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   WorkingDirectory=/root/rl-swarm
   ExecStart=/usr/bin/env bash -c 'source /root/rl-swarm/.venv/bin/activate && exec /root/rl-swarm/run_rl_swarm.sh'
   Restart=always
   SuccessExitStatus=0
   RestartSec=10s
   StartLimitIntervalSec=5min
   StartLimitBurst=10
   KillMode=process
   TimeoutStopSec=30
   StandardOutput=journal
   StandardError=journal

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

7. **Перезагружаем демон systemd** и включаем наш сервис:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable --now rl_swarm.service
   ```

После этого нода будет запускаться в фоне и автоматически перезапускаться при падении.

---

## Просмотр логов

Чтобы следить за логами сервера в режиме реального времени, выполните:
```
sudo journalctl -u rl_swarm.service -f
```
