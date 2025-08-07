# Automated Scheduling with Cron
The project includes a sample cron file (`ledstriplight/etc/cron.d/ledstriplight`) that automatically starts and stops the LED strip systemd service at specific times.

This allows the LED strip to turn on and off automatically according to your daily routine, saving energy and providing convenient lighting automation.

## Installation steps

### 1. Copy the scheduling file
Copy the cron file to the cron.d directory:
```bash
sudo cp ledstriplight /etc/cron.d/
```

### 2. Set proper permissions
```bash
sudo chmod 644 /etc/cron.d/ledstriplight
sudo chown root:root /etc/cron.d/ledstriplight
```
