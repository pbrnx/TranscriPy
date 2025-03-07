@echo off
setlocal enabledelayedexpansion

:: Diretorio do projeto
set "REPO_DIR=%~dp0TranscriPy"
set "GITHUB_URL=https://github.com/pbrnx/TranscriPy.git"

echo ========================================
echo Verificando atualizacao do TranscriPy...
echo ========================================

:: Verificar se Git esta instalado
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo Erro: Git nao esta instalado! Baixe do site: https://git-scm.com/
    exit /b
)

:: Se o repositorio nao existir, clonar do GitHub
if not exist "%REPO_DIR%" (
    echo Baixando TranscriPy pela primeira vez...
    git clone %GITHUB_URL% "%REPO_DIR%"
    cd /d "%REPO_DIR%"
) else (
    echo Verificando atualizacoes...
    cd /d "%REPO_DIR%"
    git fetch origin
    for /f %%i in ('git rev-parse HEAD') do set "LOCAL_COMMIT=%%i"
    for /f %%i in ('git rev-parse origin/main') do set "REMOTE_COMMIT=%%i"
    
    if not "!LOCAL_COMMIT!"=="!REMOTE_COMMIT!" (
        echo Atualizando para a versao mais recente...
        git pull origin main
    ) else (
        echo Ja esta atualizado!
    )
)

echo Instalando dependencias do Whisper...

:: Atualizar pip, setuptools e wheel para evitar erros de compilacao
python -m pip install --upgrade pip setuptools wheel

:: Instalar Whisper diretamente do repositorio oficial
pip install git+https://github.com/openai/whisper.git

:: Instalar Torch com suporte a CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

:: Instalar dependencias extras necessarias para o Whisper
pip install prompt_toolkit tqdm imageio-ffmpeg

:: Instalar FFmpeg para manipulacao de audio e video
pip install ffmpeg-python

echo Todas as dependencias foram instaladas com sucesso!

:: Executar automaticamente o script de transcricao
echo Iniciando TranscriPy...
python "%REPO_DIR%\transcribe.py"

pause
