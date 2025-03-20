import os
import openai
from pydub import AudioSegment
import moviepy.editor as mp
from app.core.config import settings
from app.services.openai_client import client

def extract_audio_from_video(video_path):
    """영상 파일에서 오디오 추출"""
    audio_path = video_path.replace(os.path.splitext(video_path)[1], ".wav")
    video = mp.VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return audio_path

def get_audio_duration(audio_path):
    """오디오 파일의 길이(초)를 반환"""
    audio = AudioSegment.from_file(audio_path)
    return len(audio) / 1000  # 밀리초를 초로 변환

def transcribe_audio(file_path):
    """
    오디오 또는 영상 파일을 텍스트로 변환
    
    Args:
        file_path: 오디오 또는 영상 파일 경로
        
    Returns:
        dict: {"text": 변환된 텍스트, "duration": 파일 길이(초)}
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 영상 파일인 경우 오디오 추출
    audio_path = file_path
    if file_ext in ['.mp4', '.avi', '.mov', '.webm']:
        audio_path = extract_audio_from_video(file_path)
    
    # 오디오 파일 길이 확인
    duration = get_audio_duration(audio_path)
    
    # OpenAI Whisper API를 사용하여 변환
    with open(audio_path, "rb") as audio_file:
        try:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            transcription_text = transcript.text
        except Exception as e:
            print(f"OpenAI API 오류: {str(e)}")
            raise
    
    # 임시 오디오 파일 삭제 (영상 파일에서 추출한 경우)
    if audio_path != file_path and os.path.exists(audio_path):
        os.unlink(audio_path)
    
    return {
        "text": transcription_text,
        "duration": int(duration)
    } 