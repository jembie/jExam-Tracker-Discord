# jExam Webpage Monitor
This script monitors the jExam webpage for changes and sends notifications via Discord webhooks.

## Requirements
- Python 3.6+
- Selenium
- chromedriver in `PATH`
- Discord webhook `URL`
- Python dotenv
- Python discord_webhook

## Installation
1. Clone the repository.
2. Install the required packages using `pip install -r requirements.txt` 
3. Create a `.env` file and add the following contents:

```env
PAYLOARD_URL=<YOUR DISCORD WEBHOOK URL>
CHROME_PATH=<YOUR PATH TO CHROMEDRIVER> #Default for project is set to "/user/bin/chromedriver"
```

4. Run the script using `python track_site.py`
