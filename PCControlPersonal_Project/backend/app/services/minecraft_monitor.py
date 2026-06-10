import logging
import os
import re
import time
import threading
from .notify_service import telegram_notify

logger = logging.getLogger("minecraft-monitor")

LATEST_LOG = "/opt/minecraft/server/logs/latest.log"

class MinecraftMonitor:
    def __init__(self, log_path=LATEST_LOG):
        self.log_path = log_path
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, name="MinecraftMonitorThread", daemon=True)
        self.thread.start()
        logger.info("Minecraft Monitor Thread started tracking log: %s", self.log_path)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=3)
            logger.info("Minecraft Monitor Thread stopped")

    def _run_loop(self):
        # Wait for log file to exist
        while self.running and not os.path.exists(self.log_path):
            time.sleep(5)
            
        if not self.running:
            return

        # Open file and seek to the end
        try:
            with open(self.log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, os.SEEK_END)
                
                logger.info("Seeked to the end of latest.log, starting monitoring...")
                
                while self.running:
                    line = f.readline()
                    if not line:
                        # No new line, sleep a bit
                        time.sleep(1.0)
                        
                        # In case log file got rotated / truncated, reset file pointer
                        if os.path.exists(self.log_path):
                            try:
                                current_size = os.path.getsize(self.log_path)
                                if current_size < f.tell():
                                    logger.info("latest.log was truncated or rotated, resetting reader")
                                    f.seek(0, os.SEEK_SET)
                            except Exception:
                                pass
                        continue
                    
                    self._parse_line(line.strip())
        except Exception as e:
            logger.error("Error in Minecraft Monitor loop: %s", e)
            # Restart after delay if crashed
            if self.running:
                time.sleep(5)
                self._run_loop()

    def _parse_line(self, line: str):
        # Example lines:
        # [21:30:11] [Server thread/INFO]: Horis joined the game
        # [21:30:20] [Server thread/INFO]: Horis left the game
        # [21:31:00] [Server thread/INFO]: Horis has made the advancement [A Terrible Fortress]
        
        # Only parse INFO lines
        if "[Server thread/INFO]" not in line:
            return
            
        # Parse join
        m_join = re.search(r'\[\d{2}:\d{2}:\d{2}\]\s+\[Server\s+thread/INFO\]:\s+(\w+)\s+joined\s+the\s+game', line)
        if m_join:
            player = m_join.group(1)
            msg = f"🟩 **{player} зашел на сервер Minecraft!** 🎮"
            logger.info("Player join detected: %s", player)
            telegram_notify(msg)
            return

        # Parse leave
        m_leave = re.search(r'\[\d{2}:\d{2}:\d{2}\]\s+\[Server\s+thread/INFO\]:\s+(\w+)\s+left\s+the\s+game', line)
        if m_leave:
            player = m_leave.group(1)
            msg = f"🟥 **{player} вышел с сервера Minecraft.** 👋"
            logger.info("Player leave detected: %s", player)
            telegram_notify(msg)
            return

        # Parse advancement
        m_adv = re.search(r'\[\d{2}:\d{2}:\d{2}\]\s+\[Server\s+thread/INFO\]:\s+(\w+)\s+has\s+made\s+the\s+advancement\s+\[(.*?)\]', line)
        if m_adv:
            player = m_adv.group(1)
            adv = m_adv.group(2)
            msg = f"🏆 **{player} получил достижение: [{adv}]!** 🎉"
            logger.info("Player advancement detected: %s -> %s", player, adv)
            telegram_notify(msg)
            return

        # Parse challenge
        m_ch = re.search(r'\[\d{2}:\d{2}:\d{2}\]\s+\[Server\s+thread/INFO\]:\s+(\w+)\s+has\s+completed\s+the\s+challenge\s+\[(.*?)\]', line)
        if m_ch:
            player = m_ch.group(1)
            ch = m_ch.group(2)
            msg = f"🏆 **{player} выполнил испытание: [{ch}]!** 🔥"
            logger.info("Player challenge detected: %s -> %s", player, ch)
            telegram_notify(msg)
            return

# Global instance
monitor = MinecraftMonitor()
