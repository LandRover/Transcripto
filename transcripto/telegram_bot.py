from transcripto.handlers.tts_handler import process_tts
from transcripto.handlers.transcription_handler import process_transcription
from transcripto.handlers.summarization_handler import process_summarization
from transcripto.handlers.download_handler import process_download
import logging
from telegram import Update
from telegram.ext import filters, CommandHandler, MessageHandler, Application, ContextTypes
from config import TEMP_DIR

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'I can summuraize a raw mp3, podcast, youtube video or a spotify podcast when sending a valid url\n/help - Get help information'
    )


# Define a function to handle messages starting with 'https://'
async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    transcription_engine = "wisper"
    summarization_engine = "openai"
    summarization_model = "gpt-4o-mini"
    url = update.message.text

    status_update_message = await update.message.reply_text(f"Downloading {url}")
    
    try:
        file_title, audio_local_path, audio_metadata = process_download(url)
    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=status_update_message.chat_id,
            message_id=status_update_message.message_id,
            text=f"{e}"
        )
        return None

    # status update
    await context.bot.edit_message_text(
        chat_id=status_update_message.chat_id,
        message_id=status_update_message.message_id,
        text=f"Download Completed, Starting Transcription using {transcription_engine} engine."
    )

    logging.info(f"Metadata extracted from {audio_local_path}: {audio_metadata}")

    
    transcription_text = process_transcription(
        audio_local_path,
        TEMP_DIR,
        file_title,
        "mp3",
        transcription_engine,
        language="en-US",
    )

    # status update
    await context.bot.edit_message_text(
        chat_id=status_update_message.chat_id,
        message_id=status_update_message.message_id,
        text=f"Transcription Completed, Summerizing using {summarization_engine} engine based on {summarization_model} model..."
    )

    summary_text = process_summarization(
        transcription_text,
        file_title,
        summarization_engine,
        summarization_model,
    )

    # status update
    await context.bot.edit_message_text(
        chat_id=status_update_message.chat_id,
        message_id=status_update_message.message_id,
        text=f"{summary_text}"
    )


async def start_loop_bot(API_TOKEN) -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler('help', help_cmd))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^https://"), url_handler))

    # Start polling for updates
    await application.run_polling()

