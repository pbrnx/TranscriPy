import whisper
import torch
import os
import sys
from tqdm import tqdm
from prompt_toolkit.shortcuts import radiolist_dialog

# Função para obter o caminho base do projeto
def get_project_path():
    if getattr(sys, 'frozen', False):  # Se for um executável PyInstaller
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))  # Se for um script Python

# Definir caminhos dentro do projeto
project_path = get_project_path()
whisper_assets_path = os.path.join(project_path, "whisper_assets")

# Configura os arquivos de assets manualmente
gpt2_path = os.path.join(whisper_assets_path, "gpt2.tiktoken")
mel_filters_path = os.path.join(whisper_assets_path, "mel_filters.npz")
multilingual_path = os.path.join(whisper_assets_path, "multilingual.tiktoken")

# Verifica se os arquivos existem antes de rodar
if not all(os.path.exists(path) for path in [gpt2_path, mel_filters_path, multilingual_path]):
    print("Erro: Os arquivos de assets do Whisper não foram encontrados na pasta local.")
    exit()

# Forçar o Whisper a usar os assets locais sobrescrevendo os caminhos internos
whisper.audio.MEL_FILTERS_PATH = mel_filters_path
whisper.tokenizer.GPT2_TOKENIZER_PATH = gpt2_path
whisper.tokenizer.MULTILINGUAL_TOKENIZER_PATH = multilingual_path

# Definir variáveis de ambiente explicitamente
os.environ["WHISPER_ASSETS"] = whisper_assets_path
os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Evita warnings

# Imprimir caminho para depuração
print(f"Usando whisper_assets em: {whisper_assets_path}")

# Detectar automaticamente se CUDA está disponível
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Usando dispositivo: {device}")

# Caminho do FFmpeg local
ffmpeg_path = os.path.join(project_path, "ffmpeg_bin", "ffmpeg.exe")
if not os.path.exists(ffmpeg_path):
    print("Erro: FFmpeg não encontrado no diretório do projeto.")
    exit()
os.environ["PATH"] = f"{os.path.dirname(ffmpeg_path)};{os.environ['PATH']}"
print(f"Usando FFmpeg personalizado: {ffmpeg_path}")

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
        # Obter o diretório do arquivo e nome base sem extensão
        audio_dir = os.path.dirname(audio_path)
        nome_base = os.path.splitext(os.path.basename(audio_path))[0]

        # Definir o caminho de saída no mesmo diretório do áudio
        saida_path = os.path.join(audio_dir, f"{nome_base}.{formato}")

        # Transcrever o áudio
        result = transcrever_com_progresso(model, audio_path, idioma_escolhido)

        # Salvar o arquivo no formato correto
        if formato == "srt":
            whisper.utils.get_writer("srt", audio_dir)(result, saida_path)
        else:
            with open(saida_path, "w", encoding="utf-8") as f:
                f.write(result["text"])

        print(f"\nTranscrição salva em: {saida_path}")

    except Exception as e:
        print(f"Erro ao transcrever o arquivo: {e}")
