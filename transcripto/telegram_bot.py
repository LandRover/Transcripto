from transcripto.handlers.tts_handler import process_tts
from transcripto.handlers.transcription_handler import process_transcription
from transcripto.handlers.summarization_handler import process_summarization
from transcripto.handlers.download_handler import process_download
import logging
from telegram import Update
from telegram.ext import filters, CommandHandler, MessageHandler, Application, ContextTypes
from config import TEMP_DIR

# Telegram message limit is 4096 characters
TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def split_message(text: str, max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH) -> list[str]:
    """Split a long message into chunks that fit within Telegram's message limit."""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by paragraphs first (double newlines)
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(paragraph) + 2 > max_length:
            # If current chunk has content, save it
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            
            # If the paragraph itself is too long, split by lines
            if len(paragraph) > max_length:
                lines = paragraph.split('\n')
                for line in lines:
                    if len(current_chunk) + len(line) + 1 > max_length:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                        # If single line is too long, force split
                        if len(line) > max_length:
                            for i in range(0, len(line), max_length):
                                chunks.append(line[i:i + max_length])
                        else:
                            current_chunk = line
                    else:
                        current_chunk += ("\n" if current_chunk else "") + line
            else:
                current_chunk = paragraph
        else:
            current_chunk += ("\n\n" if current_chunk else "") + paragraph
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'I can summuraize a raw mp3, podcast, youtube video or a spotify podcast when sending a valid url\n/help - Get help information'
    )


# Define a function to handle messages starting with 'https://'
async def url_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    transcription_engine = "wisper"
    summarization_engine = "vertex"
    summarization_model = "gemini-3-pro-preview"
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

    # Split summary into chunks if it exceeds Telegram's message limit
    summary_chunks = split_message(summary_text)
    
    # Update the first message with the first chunk
    await context.bot.edit_message_text(
        chat_id=status_update_message.chat_id,
        message_id=status_update_message.message_id,
        text=summary_chunks[0]
    )
    
    # Send remaining chunks as new messages
    for chunk in summary_chunks[1:]:
        await update.message.reply_text(chunk)


async def start_loop_bot(API_TOKEN) -> None:
    application = Application.builder().token(API_TOKEN).build()

    # Register command and message handlers
    application.add_handler(CommandHandler('help', help_cmd))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^https://"), url_handler))

    # Start polling for updates
    await application.run_polling()

