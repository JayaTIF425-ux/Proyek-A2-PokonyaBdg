# -*- coding: utf-8 -*-
"""
gui/workers/scraper_worker.py - Worker thread untuk menjalankan scraper di background.
"""

from PyQt6.QtCore import QThread, pyqtSignal
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class ScraperWorker(QThread):
    """Thread untuk menjalankan scraper tanpa blocking UI."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._is_running = True
    
    def run(self):
        """Jalankan semua scraper secara berurutan."""
        try:
            sukses = []
            gagal = []
            
            scrapers = [
                ("PIHPS", self._jalankan_pihps),
                ("Yogya", self._jalankan_yogya),
                ("Borma", self._jalankan_borma),
            ]
            
            for nama, func in scrapers:
                if not self._is_running:
                    self.progress.emit("[INFO] Scraping dihentikan")
                    self.finished.emit(False, "Scraping dibatalkan oleh user")
                    return
                
                self.progress.emit(f"Memuat data dari {nama}...")
                
                try:
                    func()
                    
                    if not self._is_running:
                        self.finished.emit(False, "Scraping dibatalkan oleh user")
                        return
                    
                    sukses.append(nama)
                    self.progress.emit(f"[OK] {nama} berhasil")
                    
                except Exception as e:
                    if not self._is_running:
                        self.finished.emit(False, "Scraping dibatalkan oleh user")
                        return
                    
                    error_msg = str(e)
                    if "Expecting value" in error_msg or "JSON" in error_msg:
                        self.progress.emit(f"[SKIP] {nama}: Website tidak merespons")
                    else:
                        self.progress.emit(f"[GAGAL] {nama}: {error_msg[:80]}")
                    gagal.append(nama)
            
            # Hasil akhir
            if sukses:
                pesan = f"Berhasil: {', '.join(sukses)}"
                if gagal:
                    pesan += f"\nTerlewati: {', '.join(gagal)}"
                self.finished.emit(True, pesan)
            else:
                self.finished.emit(False, "Semua scraper gagal")
                
        except Exception as e:
            if self._is_running:
                self.finished.emit(False, f"Error: {str(e)}")
            else:
                self.finished.emit(False, "Scraping dibatalkan")
    
    def stop(self):
        """Hentikan proses scraping."""
        self._is_running = False
        self.progress.emit("[SISTEM] Menghentikan thread...")
        
        # Emit finished signal untuk menutup dialog
        self.finished.emit(False, "Scraping dibatalkan oleh user")
        
        # Terminate thread jika masih berjalan
        if self.isRunning():
            self.terminate()
            self.wait(1000)
    
    def _jalankan_pihps(self):
        if not self._is_running:
            return
        from scrapers.pihps_scraper import main
        main()
    
    def _jalankan_yogya(self):
        if not self._is_running:
            return
        from scrapers.yogya_scraper import main
        main()
    
    def _jalankan_borma(self):
        if not self._is_running:
            return
        from scrapers.borma_scraper import main
        main()