from re import I
from src.lpip.listener import PushToTalkListener
from src.context.context_database import ContextDatabase
import src.common.config


if __name__=="__main__":

    context_database = ContextDatabase()
    listener = PushToTalkListener(hf_token=src.common.config.WHISPER_API_KEY,
                                  model=src.common.config.WHISPER_MODEL)
    
    listener.set_transcription_callback(None)
    listener.start()
    