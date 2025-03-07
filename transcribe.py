import whisper
import torch
import imageio_ffmpeg as ffmpeg
import os
from prompt_toolkit.shortcuts import radiolist_dialog

# Verifica se o dispositivo é CUDA e define o dispositivo a ser usado
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")


formato = radiolist_dialog(
    title="Escolha o formato da transcrição",
    text="Selecione uma opção:",
    values=[
        ("txt", "Texto direto"),
        ("srt", "Arquivo .srt")
  ],
).run()

if not formato:
    print("Nenhuma opção selecionada. Encerrando.")
    exit()


modelos = ["tiny", "base", "small", "medium", "large"]
modelo_escolhido = radiolist_dialog(
    title="Escolha o modelo Whisper",
    text="Selecione um modelo para a transcrição:",
    values=[(m, m.capitalize()) for m in modelos],
).run()

if not modelo_escolhido:
    print("Nenhum modelo selecionado. Encerrando.")
    exit()


model = whisper.load_model(modelo_escolhido, device=device)


ffmpeg_path = ffmpeg.get_ffmpeg_exe()
print(f"Usando FFmpeg interno: {ffmpeg_path}")


while True:
    audio_path = input("Caminho do arquivo de áudio: ").strip().strip('"')
    if os.path.exists(audio_path):
        break
    print("Erro: O arquivo especificado não existe. Tente novamente.")


try:
    result = model.transcribe(audio_path)
    saida_path = f"transcricao.{formato}"

    if formato == "srt":
        writer = whisper.utils.get_writer("srt", ".")
        writer(result, saida_path)
    else:
        with open(saida_path, "w", encoding="utf-8") as f:
            f.write(result["text"])

    print(f"Transcrição salva em {saida_path}")
except Exception as e:
    print(f"Erro ao transcrever o arquivo: {e}")
