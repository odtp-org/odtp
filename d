import torch

import gradio as gr
import yt_dlp as youtube_dl
from transformers import pipeline
from transformers.pipelines.audio_utils import ffmpeg_read
import openai

from elevenlabslib import *

import tempfile
import os
import io


def transcribe(audio, audiofile, model):
    device = 0 if torch.cuda.is_available() else "cpu"

    MODEL_NAME = f"openai/whisper-{model}"
    BATCH_SIZE = 8
    pipe = pipeline(
        task="automatic-speech-recognition",
        model=MODEL_NAME,
        chunk_length_s=30, #Whisper se dise
        device=device,
    )

    # if audio is None:
    #     raise gr.Error("No audio file submitted! Please upload or record an audio file before submitting your request.")
    # elif audiofile is None:
    #     raise gr.Error("No audio file submitted! Please upload or record an audio file before submitting your request.")
    

    if audiofile is not None: 
        file = audiofile
    else:
        file = audio

    print(file)
    
    transcript_text = pipe(file, batch_size=BATCH_SIZE, generate_kwargs={"task": "transcribe"}, return_timestamps=False)["text"]

    return  transcript_text


def chatGPTrespuesta(entrevistador, entrevistado, objetivo, orden, openai_key, transcript_text):

    system_template= f"""
Actúa siguiendo estas directrices. 
Tu eres: {entrevistador}.
Ahora mismo estas haciendo una entrevista a {entrevistado}.
Tu objetivo en la entrevista es {objetivo}. 
Como experto, por favor {orden}. 
Dame el objetivo en formato lista markdown con negrita en los puntos importantes. 
    """
    openai.api_key = openai_key
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_template},
            {"role": "user", "content": transcript_text}
        ]
    )
    respuesta = completion.choices[0].message.content

    return respuesta


def generateAudio(respuesta, elabs_key):

    user = ElevenLabsUser(elabs_key)
    premadeVoice = user.get_voices_by_name("Rachel")[0]
    playbackOptions = PlaybackOptions(runInBackground=False)
    generationOptions = GenerationOptions(model_id="eleven_multilingual_v1", stability=0.3, similarity_boost=0.7, style=0.6, #eleven_english_v2
                                        use_speaker_boost=True)
    audioData, historyID = premadeVoice.generate_audio_v2(respuesta, generationOptions)                 
    #generationData = premadeVoice.generate_play_audio_v2(text, PlaybackOptions(runInBackground=False), GenerationOptions(stability=0.4))

    filename = "output.wav"
    #Save them to disk, in ogg format (can be any format supported by SoundFile)
    save_audio_bytes(audioData, filename, outputFormat="wav")

    return filename


def transcriptionResponseAudio(entrevistador, entrevistado, objetivo, orden, openai_key, elabs_key, audio, audiofile, model):

    transcript_text = transcribe(audio, audiofile, model)
    respuesta = chatGPTrespuesta(entrevistador, entrevistado, objetivo, orden, openai_key, transcript_text)
    filename = generateAudio(respuesta, elabs_key)

    return  transcript_text, respuesta, filename

def analysis(transcript):  
    return "TODO"

def preparar():
    return "TODO"

#############################################################

transcribeI = gr.Interface(
    fn=transcribe,
    inputs=[
        gr.Audio(source="microphone", type="filepath", optional=True),
        gr.File(label="Upload Files", file_count="multiple"),
        gr.Radio(["tiny", "base", "small", "medium", "large", "large-v1", "large-v2"], label="Models", default="large-v2"),
    ],
    outputs=[
        gr.Markdown()],
    layout="horizontal",
    theme="huggingface",
    title="Campus Gutemberg",
    description=(
        "Asistente Demo AI para entrevistas \n"
        "1. Add preliminary info about who I am \n"
        "2. Add info about the interviewed \n"
        "3. Add your goal in the interview \n"
        "4. Any other comment or command \n"
    ),
    allow_flagging="never",
    #examples=[[None, "COSER-4004-01-00_5m.wav", "large-v2"]]
)

analysisI = gr.Interface(
    fn=transcribe,
    inputs=[
        gr.Audio(source="microphone", type="filepath", optional=True),
        gr.File(label="Upload Files", file_count="multiple"),
        gr.Radio(["tiny", "base", "small", "medium", "large", "large-v1", "large-v2"], label="Models", default="large-v2"),
    ],
    outputs=[
        gr.Markdown()],
    layout="horizontal",
    theme="huggingface",
    title="Campus Gutemberg",
    description=(
        "Asistente Demo AI para entrevistas \n"
        "1. Add preliminary info about who I am \n"
        "2. Add info about the interviewed \n"
        "3. Add your goal in the interview \n"
        "4. Any other comment or command \n"
    ),
    allow_flagging="never",
    #examples=[[None, "COSER-4004-01-00_5m.wav", "large-v2"]]
)

preparacionI = gr.Interface(
    fn=transcribe,
    inputs=[
        gr.Audio(source="microphone", type="filepath", optional=True),
        gr.File(label="Upload Files", file_count="multiple"),
        gr.Radio(["tiny", "base", "small", "medium", "large", "large-v1", "large-v2"], label="Models", default="large-v2"),
    ],
    outputs=[
        gr.Markdown()],
    layout="horizontal",
    theme="huggingface",
    title="Campus Gutemberg",
    description=(
        "Asistente Demo AI para entrevistas \n"
        "1. Add preliminary info about who I am \n"
        "2. Add info about the interviewed \n"
        "3. Add your goal in the interview \n"
        "4. Any other comment or command \n"
    ),
    allow_flagging="never",
    #examples=[[None, "COSER-4004-01-00_5m.wav", "large-v2"]]
)

transAsesorAudioI = gr.Interface(
    fn=transcriptionResponseAudio,
    inputs=[
        gr.Textbox("Entrevistador famoso de ciencia. Estilo Carl Sagan.", label="Info about what do you want me to be.",max_lines=10),
        gr.Textbox("Estás hablando con Hedy Lamarr, una actriz e inventora estadounidense nacida en Austria-Hungría. Al comienzo de la Segunda Guerra Mundial, ella y el compositor vanguardista George Antheil desarrollaron un sistema de guía por radio para los torpedos aliados que utilizaba tecnología de espectro ensanchado y salto de frecuencia para contrarrestar la amenaza de interferencia por parte de las potencias del Eje.", label="Info about who I am talking to.",max_lines=10),
        gr.Textbox("Quiero hacer una entrevista orientada a niños.", label="What are the goals of this interview?",max_lines=10),
        gr.Textbox("Propón preguntas como un asesor. Dame directrices sobre como guiar la entrevista hacía mi objetivo.", label="What do you want me to do?",max_lines=10),
        gr.Textbox("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", label="OpenAI Token", type="password", max_lines=1),
        gr.Textbox("69ef96c22e555c9966468216fc317573", label="ELabs Token", type="password", max_lines=1),
        gr.Audio(source="microphone", type="filepath", optional=True),
        gr.File(label="Upload Files", file_count="multiple"),
        gr.Radio(["tiny", "base", "small", "medium", "large", "large-v1", "large-v2"], label="Models", default="transcribe"),
    ],
    outputs=[
        "text",
        gr.Markdown(),
        gr.Audio(type="filepath")],
    layout="horizontal",
    theme="huggingface",
    title="Campus Gutemberg",
    description=(
        "Asistente Demo AI para entrevistas \n"
        "1. Add preliminary info about who I am \n"
        "2. Add info about the interviewed \n"
        "3. Add your goal in the interview \n"
        "4. Any other comment or command \n"
    ),
    allow_flagging="never",
)

demo = gr.Blocks()

with demo:
    gr.Markdown("# Hola Pepsicola")
    gr.TabbedInterface([transcribeI, analysisI, preparacionI, transAsesorAudioI], ["Transcripción", "Análisis", "Preparación", "Asistente de entrevistas (audio)"])

demo.launch(enable_queue=True)