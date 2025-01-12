import ffmpeg
import torch
import os
import whisper
import deep_translator
import argparse
import sys
import signal
from gooey import Gooey, GooeyParser
from datetime import datetime, timedelta
try:
    from subtitler_util import VERSION, TEMP_DIR, DIR_DELIM
    from subtitler_util.constants import SUPPORTED_TRANSLATORS, TRANSCRIPTION_SUPPORTED_LANGS, TRANSLATION_SUPPORTED_LANGS, TRANSCRIPTION_SUPPORTED_MODELS, GUI_MENU
except ModuleNotFoundError:
    from __init__ import VERSION, TEMP_DIR, DIR_DELIM
    from constants import SUPPORTED_TRANSLATORS, TRANSCRIPTION_SUPPORTED_LANGS, TRANSLATION_SUPPORTED_LANGS, GUI_MENU

## temp fix/workaround for gui issue in windows
if os.name =='nt':
    scripts_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    if not os.path.exists(scripts_dir+DIR_DELIM+"subtitler"):
        import shutil
        shutil.copy(scripts_dir+DIR_DELIM+"subtitler.exe",scripts_dir+DIR_DELIM+"subtitler")

def signal_handler(*args):
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def gen_wav_file(vid_file: str, file_map: dict):
    output_audio_file = TEMP_DIR+DIR_DELIM+( ".".join(vid_file.split(DIR_DELIM)[-1].split(".")[:-1]) )+".wav"
    file_map[output_audio_file] = vid_file
    os.makedirs(TEMP_DIR,mode=0o777, exist_ok=True)
    input_stream = ffmpeg.input(vid_file)
    output_stream = ffmpeg.output(input_stream.audio,output_audio_file,acodec="pcm_s16le",ar="44100",ac="2")
    output_stream.run(overwrite_output=True, quiet=True)
    print(f"generated wav file for {vid_file} in {TEMP_DIR}")
    return output_audio_file

def cleanup():
    for f in os.listdir(TEMP_DIR):
        os.remove(TEMP_DIR+DIR_DELIM+f)
    print("clean up done.")

def init_model(model_size: str):
    def load_model_pref():
        if model_size is not None:
            return model_size
        elif os.path.exists(".model_pref"):
            with open(".model_pref") as f:
                return f.readline()
        else:
            return None
    def save_model_pref():
        with open(".model_pref","w") as f:
            f.write(model_size)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if load_model_pref() is not None:
        print(f"loading whisper's '{load_model_pref()}' model")
        return whisper.load_model(load_model_pref(),device=device)
    else:
        model_sizes = ["turbo","large-v3","large-v2","large","medium","small","base","tiny"]
        for model_size in model_sizes:
            try:
                model = whisper.load_model(model_size,device=device)
                print(f"model {model_size} loaded successfully.")
                save_model_pref()
                return model
            except torch.cuda.OutOfMemoryError:
                continue
            except Exception as e:
                print(f"failed to load model {model_size}")
                print(e)
        return None

def detect_lang(model: whisper.model, audio_file: str):
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)
    spectrogram = whisper.log_mel_spectrogram(audio).to(model.device)
    _, p = model.detect_language(spectrogram)
    return max(p, key=p.get)

def transcribe_audio(model: whisper.model, audio_file: str, language: str):
    
    def format_timestamp(time_in_seconds):
        dt_obj = datetime.strptime("00:00:00.000", '%H:%M:%S.%f')
        delta_seconds = timedelta(seconds=time_in_seconds)
        dt_obj += delta_seconds
        return dt_obj.strftime("%H:%M:%S,%f")[:-3]
    
    def post_process_result_for_srt(result):
        new_result = {}
        for seg in result["segments"]:
            seg_id = seg["id"] + 1
            new_result[seg_id] = {}
            new_result[seg_id]["start_time"] = format_timestamp(seg["start"])
            new_result[seg_id]["end_time"] = format_timestamp(seg["end"])
            new_result[seg_id]["text"] = seg["text"].strip()
        return new_result
    
    language = language.lower()
    if language not in TRANSCRIPTION_SUPPORTED_LANGS:
        raise Exception("Cannot Transcribe! Unsupported Language. See Readme for list of supported languages.")
    audio= whisper.load_audio(audio_file)
    result = model.transcribe(audio,language=language,task="transcribe")
    return post_process_result_for_srt(result)

def translate_transcribed_result(transcribed_result, transcribed_language, target_language,translator="google", api_key=None):

    def init_translator(translator, transcribed_language, target_language, api_key):
        if translator not in SUPPORTED_TRANSLATORS:
            raise Exception("Unsupported Translator Service Provided. Please request translations from one of the the supported service providers. (see config for complete list.)")
        if translator == "google":
            translator = deep_translator.GoogleTranslator(source=transcribed_language, target=target_language)
        else:
            if api_key is None:
                raise Exception("API_KEY is necessary to access Deepl translation service. Please register for free and get an API-Key at https://www.deepl.com/en/your-account/keys.")
            if translator == "deepl":
                translator = deep_translator.DeeplTranslator(api_key=api_key, source=transcribed_language, target=target_language)
            elif translator == "yandex":
                translator = deep_translator.YandexTranslator(api_key=api_key, source=transcribed_language, target=target_language)
            elif translator == "microsoft":
                translator = deep_translator.MicrosoftTranslator(api_key=api_key, target=target_language)
            elif translator == "chatgpt":
                translator = deep_translator.ChatGptTranslator(api_key=api_key, target=target_language)
            elif translator == "libre-translate":
                translator = deep_translator.LibreTranslator(api_key=api_key, source=transcribed_language, target=target_language, base_url='https://libretranslate.com/')
        return translator

    translator = init_translator(translator, transcribed_language, target_language, api_key)
    translated_result = {}
    translation_cache = []
    for id, transcribed_obj in transcribed_result.items():
        translated_result[id] = {}
        translated_result[id]["start_time"] = transcribed_obj["start_time"]
        translated_result[id]["end_time"] = transcribed_obj["end_time"]
        translation_cache.append(transcribed_obj["text"])
    translated_results_cache = translator.translate_batch(translation_cache)
    for id, result_obj in translated_result.items():
        temp = translated_results_cache.pop(0) 
        if temp is not None:
            result_obj["text"] = temp
        else:
            result_obj["text"] = "."
    return translated_result

def save_result_as_srt(result: dict, target_language: str, video_file_name: str):

    def get_lang_iso_code(lang):
        if lang in TRANSCRIPTION_SUPPORTED_LANGS:
            return TRANSCRIPTION_SUPPORTED_LANGS[lang]
        elif lang in TRANSLATION_SUPPORTED_LANGS:
            return TRANSLATION_SUPPORTED_LANGS[lang]
    
    target_language = target_language.lower()
    srt_file_name = ".".join(video_file_name.split(".")[:-1])+"."+get_lang_iso_code(target_language)+".srt"
    if os.name == 'nt':
        with open(srt_file_name,"w", encoding='utf-8', errors='replace') as f:
            for id, result_obj in result.items():
                f.write(str(id)+"\n")
                f.write(str(result_obj["start_time"])+" --> "+str(result_obj["end_time"])+"\n")
                f.write(result_obj["text"].encode('utf-8','replace').decode('utf-8'))
                f.write("\n\n")
        return srt_file_name
    else:
        with open(srt_file_name,"w") as f:
            for id, result_obj in result.items():
                f.write(str(id)+"\n")
                f.write(str(result_obj["start_time"])+" --> "+str(result_obj["end_time"])+"\n")
                f.write(result_obj["text"])
                f.write("\n\n")
        return srt_file_name

def check_if_file_is_video(file):
    try:
        probe_result = ffmpeg.probe(file)
        if "streams" in probe_result:
            for stream in probe_result["streams"]:
                if stream["codec_type"] == "video":
                    return True
        print(f"No video stream(s) were found in File: {file}. Skipping it.")
        return False
    except Exception as e:
        print(f"Error probing file: {file}")
        print(e)

def find_vid_files_in_dir(target_dir):
    files_list = []
    for cwd, dirs, files, in os.walk(target_dir):
        [files_list.append(cwd+DIR_DELIM+afile) for afile in files if check_if_file_is_video(cwd+DIR_DELIM+afile)]
    return files_list

def subtitle(vid_file_map: dict, audio_files: list, video_language: str, translation_languages: list, translation_service: str="google", translation_service_api_key: str = None, model_size: str = None, mode: str=None):
    
    def print_and_update_progress(update_progress=False):
        nonlocal current_step
        if mode == 'gui':
            print(f"progress: {current_step}/{total_steps}")
            if update_progress:
                current_step += 1

    total_steps = 2
    current_step = 1
    print_and_update_progress()
    model = init_model(model_size)
    print_and_update_progress(update_progress=True)
    print("Done.")
    total_steps += (len(audio_files)*2) + (len(audio_files)*len(translation_languages)*2)
    print_and_update_progress()
    for  audio_file in audio_files:
        print(f"Transcribing video: {vid_file_map[audio_file]} in {video_language}")
        r=transcribe_audio(model, audio_file, video_language)
        print("Done.\nSaving...")
        print_and_update_progress(update_progress=True)
        saved_file = save_result_as_srt(r,video_language,vid_file_map[audio_file])
        print(f"Done. Saved transcribed result as srt file: {saved_file}")
        print_and_update_progress(update_progress=True)
        for translation_lang in translation_languages:
            print(f"\tTranslating subtitles to another language: {translation_lang}")
            r2=translate_transcribed_result(r,video_language,translation_lang,translator=translation_service, api_key=translation_service_api_key)
            print(f"\tDone.\n\tSaving...")
            print_and_update_progress(update_progress=True)
            saved_file = save_result_as_srt(r2,translation_lang,vid_file_map[audio_file])
            print(f"\tDone. Saved translated result as srt file: {saved_file}")
            print_and_update_progress(update_progress=True)
        

def process_args(args):
    if args.translation_languages is None:
        args.translation_languages = []
    vid_file_map= {}
    audio_files = []
    if args.video_files is None:
        for f in find_vid_files_in_dir(args.video_dir):
            audio_files.append(gen_wav_file(f,vid_file_map))
    elif args.video_dir is None:
        for f in [f for f in args.video_files if check_if_file_is_video(f)]:
            audio_files.append(gen_wav_file(f,vid_file_map))
    subtitle(vid_file_map,audio_files,args.video_language,args.translation_languages, translation_service=args.translation_service, translation_service_api_key=args.translation_service_api_key, model_size=args.model_size, mode=args.mode)
    cleanup()

def cli():
    parser = argparse.ArgumentParser(description="Transcribe and Translate subtitles for videos in any language.",prog="Subtitler", epilog="Subtitler Copyright (C) 2024 Anupam Kumar <https://anupamkumar.me>. \nThis program comes with ABSOLUTELY NO WARRANTY.\nThis is free software, and you are welcome to redistribute it under certain conditions; \nGoto https://raw.githubusercontent.com/anupamkumar/subtitler/master/LICENSE for details.")
    parser.add_argument("mode",help="enter mode as cli to run cli. not entering a mode will attempt to run the gui")
    parser.add_argument("-v","--version", help="show version and exit", action='version', version=VERSION)
    ip_files_group = parser.add_mutually_exclusive_group(required=True)
    ip_files_group.add_argument("--video_files", help="full path to the video file you want to generate subtitles for",type=str, action='append')
    ip_files_group.add_argument("--video_dir", help="full path to directory where your video files may be",type=str)
    transcribe_group = parser.add_argument_group("Transcription Configuration")
    transcribe_group.add_argument("--video_language",help="Provide the language of the video(s). Set it to 'unknown' if you don't know and want AI to guess the language.(WARNING! This may be a bad-idea because the AI may make a mistake with language detection)",choices=TRANSCRIPTION_SUPPORTED_LANGS.keys(), required=True)
    transcribe_group.add_argument("--force_language_autodetect",help="force language detection for all videos even if you provide 'video language' parameter", action="store_true")
    transcribe_group.add_argument("--model_size",help="Force specific whisper model size.", choices=TRANSCRIPTION_SUPPORTED_MODELS)
    translation_group = parser.add_argument_group("Translation Configuration")
    translation_group.add_argument("--translation_languages",help="select all the languages you want to also translate the subtitles to.",choices=TRANSLATION_SUPPORTED_LANGS.keys(), nargs="*")
    translation_group.add_argument("--translation_service", help="pick a translation service.",choices=SUPPORTED_TRANSLATORS, default="google")
    translation_group.add_argument("--translation_service_api_key", help="not required for Google. But required for all other services.")
    args = parser.parse_args()
    print(f"Run Configuration: {args}\n")
    process_args(args)

@Gooey(clear_before_run=True,
       progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
       hide_progress_msg=True,
       progress_expr="current / total * 100",
       timing_options={'show_time_remaining': False, 'hide_time_remaining_on_complete': False},
       show_restart_button=False,
       optional_cols=1,
       program_name="Subtitler "+VERSION,
       menu=GUI_MENU)
def gui():
    parser = GooeyParser(description="Transcribe and Translate subtitles for videos in any language.")
    file_input_group = parser.add_argument_group("Input Configuration")
    ip_files_group = file_input_group.add_mutually_exclusive_group(required=True)
    ip_files_group.add_argument("--video_files", help="full path to the video file you want to generate subtitles for",widget='MultiFileChooser', nargs="+")
    ip_files_group.add_argument("--video_dir", help="full path to directory where your video files may be",widget='DirChooser')
    transcribe_group = parser.add_argument_group("Transcription Configuration")
    transcribe_group.add_argument("--video_language",help="Provide the language of the video(s). Set it to 'unknown' if you don't know and want AI to guess the language.(WARNING! This may be a bad-idea because the AI may make a mistake with language detection)",widget="FilterableDropdown",choices=TRANSCRIPTION_SUPPORTED_LANGS.keys(), required=True)
    transcribe_group.add_argument("--force_language_autodetect",help="force language detection for all videos even if you provide 'video language' parameter", widget="BlockCheckbox", action="store_true")
    transcribe_group.add_argument("--model_size",help="Force specific whisper model size.", choices=TRANSCRIPTION_SUPPORTED_MODELS)
    translation_group = parser.add_argument_group("Translation Configuration")
    translation_group.add_argument("--translation_languages",help="select all the languages you want to also translate the subtitles to.",widget="Listbox",choices=TRANSLATION_SUPPORTED_LANGS.keys(), nargs="*", gooey_options={'height':200})
    translation_group.add_argument("--translation_service", help="pick a translation service.",choices=SUPPORTED_TRANSLATORS, widget="Dropdown", default="google")
    translation_group.add_argument("--translation_service_api_key", help="not required for Google. But required for all other services.")
    args = parser.parse_args()
    args.mode = 'gui'
    print(f"Run Configuration: {args}\n")
    process_args(args)
    sys.exit(0)
    
def main():
    if 'cli' in sys.argv:
        cli()
    else:
        gui()


if __name__ == "__main__":
    main()
