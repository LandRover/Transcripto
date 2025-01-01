# Transcripto: Transcribe and Summarize Podcasts

<center>
   ![Transcripto Logo](static/images/logo.png)
</center>

**Transcripto** is an open-source tool designed to summarize podcast episodes into concise, actionable insights using AI. By distilling hours of audio into key takeaways, Transcripto makes it easy to share or review podcast content quickly and effectively. It's perfect for personal productivity, content creators, or organizations looking to streamline information sharing.

---

## Key Features

- **AI Summarization**: Generate a detailed summary of podcast content in just 6 bullet points with key insights.
- **Input Options**: Supports podcasts from YouTube, Spotify, Apple Podcasts, or raw MP3 files.
- **Customizable Models**: Choose between multiple transcription and summarization engines (e.g., OpenAI's GPT, Whisper, etc.).
- **Text-to-Speech (TTS)**: Convert summarized content into speech for easy consumption.
- **Telegram Bot Support**: Use the tool as a Telegram bot for added convenience.

---

## Supported Sources

- **YouTube**
- **Spotify**
- **Apple Podcasts**
- **Raw MP3 files**

---

## Installation

1. Clone the repository:
   ```bash
   $ git clone https://github.com/LandRover/Transcripto.git
   ```

2. Install dependencies:
   ```bash
   $ pip install -r requirements.txt
   ```

3. Set up the OpenAI API key:
   ```bash
   $ export OPENAI_API_KEY="your_api_key_here"
   ```

---

## Usage

### Command Line Interface (CLI)

Run the main script to process an audio file or URL:

```bash
$ python -m transcripto --url "http://example.com/audio.mp3" --summarize
```

**Available Arguments:**

- `--url` (Required): URL or local path of the MP3 file.
- `--summarize`: Generates a summary of the transcription.
- `--tts`: Generates a text-to-speech output of the summary.
- `--output-dir`: Specify the directory to save output files (default: `./output`).
- `--log-level`: Set the logging level (e.g., DEBUG, INFO).
- `--telegram-bot`: Run Transcripto as a Telegram bot.

### Telegram Bot Mode

Start the bot by running:
```bash
$ python -m transcripto --telegram-bot
```
Provide the Telegram Bot Token via the environment variable in .env file:
```bash
$ export TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
```

---

## Running with Docker

### Build the Docker Image

To build the Docker image, run:
```bash
$ make docker_build
```

### Run the Project in a Docker Container

To start the project in a Docker container:
```bash
$ make docker_run
```

This command:
- Runs the container in detached mode.
- Maps the local `output` directory to the container's `/app/output` directory.
- Maps the local `.env` file to the container's `/app/.env` file.
- Enables GPU support (modify or remove `--gpus` flag if not using GPU).
- Passes environment variables from the `.env` file, make sure all secrets are configured.
- Runs in Telegram bot mode.


### Using Docker Compose

If you prefer using Docker Compose, you can start the application with:
```bash
$ make docker_up
```
Ensure your `docker-compose.yml` is configured properly to match your environment.

---

## .env Configuration

Below is an example of a `.env` file:

```env
OPENAI_API_KEY="your_openai_api_key"
TELEGRAM_BOT_NAME=demo_bot
TELEGRAM_BOT_TOKEN=abcd
TELEGRAM_BOT_ALLOWED_USERS=1234,5678
```

### Variables:

- **`OPENAI_API_KEY`**: Your OpenAI API key for transcription and summarization.
- **`TELEGRAM_BOT_NAME`**: The name of your Telegram bot.
- **`TELEGRAM_BOT_TOKEN`**: The authentication token for your Telegram bot.
- **`TELEGRAM_BOT_ALLOWED_USERS`**: Comma-separated Telegram user IDs allowed to interact with the bot.

Ensure this file is placed in the root directory of the project or mapped correctly in Docker.
Use `.env.sample` as referance.

---

## Example Workflow

1. **Input Source**:
   Provide a podcast URL or raw MP3 file.

2. **Transcription**:
   Transcripts are generated using AI models like Whisper.

3. **Summarization**:
   Condenses the transcript into a 6-point summary with actionable insights.

4. **Output Options**:
   - Save the transcription and summary as text files.
   - Convert the summary to speech using TTS engines.

---


## Dependencies

Install dependencies with:
```bash
$ pip install -r requirements.txt
```

---

## Development

### Run Tests
To ensure everything is working correctly:
```bash
$ pytest
```

---

## License

Transcripto is licensed under the MIT License. See `LICENSE` for more details.
