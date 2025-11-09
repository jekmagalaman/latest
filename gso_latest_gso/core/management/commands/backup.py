from django.core.management.base import BaseCommand
from django.conf import settings
from core.scripts.backup import backup_database, backup_media, cleanup_old_backups
import datetime
import os


class Command(BaseCommand):
    help = "Performs an automated backup of the database and media files."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Starting automated backup process...\n"))

        # Optional: Create a logs directory
        log_dir = os.path.join(settings.BASE_DIR, 'backups', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"backup_log_{datetime.datetime.now().strftime('%Y-%m-%d')}.txt")

        try:
            with open(log_file, "a", encoding="utf-8") as log:
                log.write(f"\n=== BACKUP RUN ({datetime.datetime.now()}) ===\n")

                # 1️⃣ DATABASE BACKUP
                self.stdout.write(self.style.MIGRATE_HEADING("🗄️  Step 1: Database Backup"))
                try:
                    db_backup_path = backup_database()
                    log.write(f"Database backup: {db_backup_path}\n")
                    self.stdout.write(self.style.SUCCESS("✅ Database backup completed!\n"))
                except Exception as e:
                    log.write(f"Database backup failed: {e}\n")
                    self.stderr.write(self.style.ERROR(f"❌ Database backup failed: {e}\n"))

                # 2️⃣ MEDIA BACKUP
                self.stdout.write(self.style.MIGRATE_HEADING("🖼️  Step 2: Media Files Backup"))
                try:
                    media_backup_path = backup_media()
                    if media_backup_path:
                        log.write(f"Media backup: {media_backup_path}\n")
                        self.stdout.write(self.style.SUCCESS("✅ Media backup completed!\n"))
                except Exception as e:
                    log.write(f"Media backup failed: {e}\n")
                    self.stderr.write(self.style.ERROR(f"❌ Media backup failed: {e}\n"))

                # 3️⃣ CLEANUP OLD BACKUPS
                self.stdout.write(self.style.MIGRATE_HEADING("🧹  Step 3: Cleaning Old Backups"))
                try:
                    cleanup_old_backups(days=7)
                    log.write("Old backups cleaned up (older than 7 days)\n")
                    self.stdout.write(self.style.SUCCESS("✅ Old backup cleanup completed!\n"))
                except Exception as e:
                    log.write(f"Cleanup failed: {e}\n")
                    self.stderr.write(self.style.ERROR(f"❌ Cleanup failed: {e}\n"))

                log.write("=== BACKUP COMPLETED ===\n")

            self.stdout.write(self.style.SUCCESS("🎉 Backup process finished successfully!"))
            self.stdout.write(self.style.SUCCESS(f"📝 Log saved to: {log_file}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Backup process failed: {e}"))
