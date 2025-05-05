# Telegram Movie Bot

Telegram bot for finding and recommending movies through simple chat interaction.

The bot is based on Telegram Messenger and uses an external movie API to search for films.  
The user sends a message with a movie title or keyword, and the bot returns relevant information.  
All interaction happens via natural chat, without complex menus or buttons.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#the-structure)
- [Author](#author)

## Features

- Finds movies by title or keywords  
- Uses external API to retrieve movie info (e.g., title, rating, plot)  
- Responds via natural chat  
- Simple architecture and easy to use  

## Installation

### Repository Cloning:

```bash
git clone https://github.com/NikolayKossov/telegram_bot.git
cd telegram_bot
```

### Installation of requirements:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Keys:

Add the following to your `.env` file:

```
BOT_TOKEN=your_telegram_bot_token (get it from BotFather)  
MOVIE_API_KEY=your_movie_api_key (e.g., from Kinopoisk)
```

### Start:

```bash
python main.py
```

## Usage

Open Telegram and start the bot using `/start`, `/movie_search`.  
Then type the name of a movie (e.g., "Terminator"), and the bot will reply with relevant results.

## The Structure

```
telegram_bot/
├── api/
├── config_data/
├── database/
├── handlers/
├── keyboards/
├── states/
├── utils/
├── .env
├── .gitignore
├── requirements.txt
├── loader.py
├── main.py
└── README.md
```

## Author

Nikolay Kossov  
https://github.com/NikolayKossov  
https://github.com/Nidvig
