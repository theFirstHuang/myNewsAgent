#!/bin/bash
# Setup cron job for LLM News Digest Agent

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Python executable (use virtual environment if exists)
if [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
elif [ -f "$PROJECT_DIR/env/bin/python" ]; then
    PYTHON_BIN="$PROJECT_DIR/env/bin/python"
else
    PYTHON_BIN="python3"
fi

# Script to run
RUN_SCRIPT="$SCRIPT_DIR/run_digest.py"

# Log file
LOG_FILE="$PROJECT_DIR/logs/cron.log"

echo "===================================="
echo "LLM News Digest - Cron Setup"
echo "===================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Python executable: $PYTHON_BIN"
echo "Run script:        $RUN_SCRIPT"
echo "Log file:          $LOG_FILE"
echo ""

# Ask for schedule
echo "Select schedule frequency:"
echo "  1) Daily at 9:00 AM"
echo "  2) Weekly on Monday at 9:00 AM"
echo "  3) Custom cron expression"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        CRON_SCHEDULE="0 9 * * *"
        SCHEDULE_DESC="Daily at 9:00 AM"
        ;;
    2)
        CRON_SCHEDULE="0 9 * * 1"
        SCHEDULE_DESC="Weekly on Monday at 9:00 AM"
        ;;
    3)
        read -p "Enter cron expression (e.g., '0 9 * * 1'): " CRON_SCHEDULE
        SCHEDULE_DESC="Custom: $CRON_SCHEDULE"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

# Build cron command
CRON_CMD="cd $PROJECT_DIR && $PYTHON_BIN $RUN_SCRIPT >> $LOG_FILE 2>&1"

# Create cron entry
CRON_ENTRY="$CRON_SCHEDULE $CRON_CMD"

echo ""
echo "Cron entry to add:"
echo "$CRON_ENTRY"
echo ""
read -p "Add this cron job? (y/n): " confirm

if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

    echo ""
    echo "✅ Cron job added successfully!"
    echo ""
    echo "Schedule: $SCHEDULE_DESC"
    echo ""
    echo "To view your cron jobs:"
    echo "  crontab -l"
    echo ""
    echo "To remove this cron job:"
    echo "  crontab -e"
    echo "  (then delete the line containing 'run_digest.py')"
    echo ""
else
    echo "Cancelled."
fi
