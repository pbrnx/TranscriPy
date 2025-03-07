import whisper
import torch
import imageio_ffmpeg as ffmpeg
import os
from tqdm import tqdm
from prompt_toolkit.shortcuts import radiolist_dialog

# Detectar automaticamente se CUDA está disponível
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")

# Opção para escolher o tipo de transcrição
formato = radiolist_dialog(
    title="Escolha o formato da transcrição",
    text="Selecione uma opção:",
    values=[("txt", "Texto direto"), ("srt", "Arquivo .srt")],
).run()

if not formato:
    print("Nenhuma opção selecionada. Encerrando.")
    exit()

# Opção para escolher o modelo
modelos = ["tiny", "base", "small", "medium", "large"]
modelo_escolhido = radiolist_dialog(
    title="Escolha o modelo Whisper",
    text="Selecione um modelo para a transcrição:",
    values=[(m, m.capitalize()) for m in modelos],
).run()

if not modelo_escolhido:
    print("Nenhum modelo selecionado. Encerrando.")
    exit()

# Opção para escolher o idioma da transcrição
idiomas = {"en": "Inglês", "es": "Espanhol", "pt": "Português"}
idioma_escolhido = radiolist_dialog(
    title="Escolha o idioma da transcrição",
    text="Selecione o idioma para a transcrição:",
    values=list(idiomas.items()),
).run()

if not idioma_escolhido:
    print("Nenhum idioma selecionado. Encerrando.")
    exit()

# Carregar o modelo Whisper
model = whisper.load_model(modelo_escolhido, device=device)

# Usar FFmpeg interno do Python
ffmpeg_path = ffmpeg.get_ffmpeg_exe()
print(f"Usando FFmpeg interno: {ffmpeg_path}")

# Função para transcrever com progresso
def transcrever_com_progresso(model, audio_path, idioma):
    """
    Função para transcrever áudio e exibir barra de progresso real.
    """
    print("\nTranscrevendo o áudio...\n")

    # Carregar o áudio
    audio = whisper.load_audio(audio_path)
    duration = len(audio) / whisper.audio.SAMPLE_RATE  # Duração total em segundos

    # Criar barra de progresso
    with tqdm(total=100, desc="Transcrevendo", bar_format="{l_bar}{bar}| {n:.0f}%") as pbar:
        # Dividir áudio em segmentos e transcrever
        result = model.transcribe(audio_path, language=idioma, verbose=False)

        # Atualizar barra de progresso manualmente
        for segment in result["segments"]:
            percent_complete = (segment["start"] / duration) * 100
            pbar.n = int(percent_complete)
            pbar.refresh()

    return result

# Loop principal para processar vários arquivos sem fechar o programa
while True:
    # Solicitar caminho do arquivo de áudio
    while True:
        audio_path = input("\nCaminho do arquivo de áudio (ou 'sair' para encerrar): ").strip().strip('"')
        if audio_path.lower() == "sair":
            print("Encerrando o programa.")
            exit()
        if os.path.exists(audio_path):
            break
        print("Erro: O arquivo especificado não existe. Tente novamente.")

    try:
        # Obter nome do arquivo sem extensão
        nome_base = os.path.splitext(os.path.basename(audio_path))[0]
        saida_path = f"{nome_base}.{formato}"

        # Transcrever o áudio
        result = transcrever_com_progresso(model, audio_path, idioma_escolhido)

        # Salvar o arquivo no formato correto
        if formato == "srt":
            whisper.utils.get_writer("srt", ".")(result, saida_path)
        else:
            with open(saida_path, "w", encoding="utf-8") as f:
                f.write(result["text"])

        print(f"\n Transcrição salva em {saida_path}")

    except Exception as e:
        print(f" Erro ao transcrever o arquivo: {e}")

