name: V18.7 Phoenix Relay

on:
  workflow_dispatch:
  schedule:
    - cron: '55 5,11,17,23 * * *'

jobs:
  launch-phoenix:
    runs-on: ubuntu-latest
    timeout-minutes: 360

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          # 🚨 REMOVED 'webdriver-manager' to fix the error
          pip install selenium 

      - name: Run V18.7 Phoenix
        env:
          PYTHONUNBUFFERED: 1 
          INSTA_SESSION: ${{ secrets.INSTA_SESSION }}
          TARGET_THREAD_ID: ${{ secrets.TARGET_THREAD_ID }}
          MESSAGES: ${{ secrets.MESSAGES }}
        run: python main.py

      - name: Upload Logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: phoenix-logs
          path: message_log.txt
