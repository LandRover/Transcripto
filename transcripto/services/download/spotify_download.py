import logging
import io
import os
from dataclasses import dataclass
import shutil
import subprocess
from pathlib import Path
from .download_base import DownloadBase
from transcripto.utils.file import extract_filename_from_url
from yt_dlp.downloader.http import HttpFD
from yt_dlp.YoutubeDL import YoutubeDL
from transcripto.services.podcast_providers.spotify.spotify_api import SpotifyAPI


class SpotifyDownload(DownloadBase):
    DECRYPTION_KEY_EPISODE = (
        b"\xde\xad\xbe\xef\xde\xad\xbe\xef\xde\xad\xbe\xef\xde\xad\xbe\xef" # deadbeefdeadbeefdeadbeefdeadbeef
    )
    URL_RE = r"(episode)/(\w{22})"
    TEMP_FILE_STRUCTURE = "{file_id}_{encryption_state}.{ext}"

    def __init__(self):
        self.spotify_api = SpotifyAPI()
        self.ffmpeg_path = shutil.which("ffmpeg")
        self._set_subprocess_additional_args()


    def _set_subprocess_additional_args(self):
        if False:
            self.subprocess_additional_args = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
            }
        else:
            self.subprocess_additional_args = {}


    def get_episode_id(self, url):
        filename = extract_filename_from_url(url)

        return filename


    def __remove_temp_path(self):
        if self.temp_path.exists():
            logging.debug(f'Cleaning up "{self.temp_path}"')
            shutil.rmtree(self.temp_path)
    

    def download(self, url: str, temp_path: Path):
        # Create an in-memory buffer
        buffer = io.BytesIO()

        self.temp_path = temp_path
        self.__remove_temp_path()
        
        logging.info(f"SpotifyDownload Starting download {url}...")
        spotify_url = self.spotify_api.extract_media_from_url(url)

        episode_metadata = self.spotify_api.get_episode_metadata(spotify_url.id)
        audio_url = episode_metadata.episode_audio_url
        
        temp_file_encrypted = self.__get_temp_filepath(spotify_url.id, "encrypted", "m4a")
        temp_file_decrypted = self.__get_temp_filepath(spotify_url.id, "decrypted", "mp3")
      
        logging.debug(f'Downloading to "{temp_file_encrypted}"')
        self.download_audio_url(audio_url, temp_file_encrypted)

        decrpytion_key = self.DECRYPTION_KEY_EPISODE.hex()
        self.decrypt(decrpytion_key, temp_file_encrypted, temp_file_decrypted)

        # Read the file into the buffer
        with open(temp_file_decrypted, 'rb') as f:
            buffer.write(f.read())

        # Delete the temporary file
        os.remove(temp_file_encrypted)
        os.remove(temp_file_decrypted)

        buffer.seek(0)
        mp3_bytes = buffer.read()
        
        return mp3_bytes


    def __get_temp_filepath(self, episode_id: str, encryption_state: str, file_extension: str) -> Path:
        temp_filename = self.TEMP_FILE_STRUCTURE.format(file_id=episode_id, encryption_state=encryption_state, ext=file_extension)
        temp_path_rel = (self.temp_path / temp_filename)

        return temp_path_rel
    

    def download_audio_url(self, audio_url: str, input_path: Path) -> None:
        input_path.parent.mkdir(parents=True, exist_ok=True)

        with YoutubeDL(
            {
                "quiet": True,
                "no_warnings": True,
                "noprogress": False,
            }
        ) as ydl:
            http_downloader = HttpFD(ydl, ydl.params)
            http_downloader.download(str(input_path), {
                "url": audio_url,
            })


    def decrypt(
        self,
        decryption_key: bytes | str,
        encrypted_path: Path,
        decrypted_path: Path,
    ):
        self.__decrypt_widevine_ffmpeg(
            decryption_key,
            encrypted_path,
            decrypted_path,
        )


    def __decrypt_widevine_ffmpeg(
        self,
        decryption_key: str,
        encrypted_path: Path,
        decrypted_path: Path,
    ):
        subprocess.run(
            [
                self.ffmpeg_path,
                "-loglevel",
                "error",
                "-y",
                "-decryption_key",
                decryption_key,
                "-i",
                encrypted_path,
                "-vn",
                "-acodec",
                "libmp3lame",
                "-q:a",
                "2",
                decrypted_path,
            ],
            check=True,
            **self.subprocess_additional_args,
        )
