#!/usr/bin/env python3
"""Test email configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.notifiers import EmailSender
from src.utils.logger import setup_logger


def main():
    print("=" * 60)
    print("📧 Email Configuration Test")
    print("=" * 60)
    print()

    try:
        # Load config
        print("Loading configuration...")
        config = Config("config.yaml")

        # Setup logging
        setup_logger(level="INFO")

        # Create sender
        sender = EmailSender(config)

        print(f"SMTP Server: {sender.smtp_server}:{sender.smtp_port}")
        print(f"Sender:      {sender.sender_email}")
        print(f"Recipient:   {sender.recipient_email}")
        print()

        # Send test email
        print("Sending test email...")
        success = sender.send_test_email()

        if success:
            print("\n✅ Success! Check your email inbox.")
        else:
            print("\n❌ Failed to send email. Check the error above.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
