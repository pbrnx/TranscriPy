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

:: Atualizar pip, setuptools e wheel apenas se necessario
pip show pip >nul 2>nul
if %errorlevel% neq 0 (
    python -m pip install --upgrade pip setuptools wheel
)

:: Verificar e instalar Whisper apenas se nao estiver instalado
pip show whisper >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando Whisper...
    pip install git+https://github.com/openai/whisper.git
) else (
    echo Whisper ja esta instalado.
)

:: Verificar e instalar Torch apenas se nao estiver instalado
pip show torch >nul 2>nul
if %errorlevel% neq 0 (
    echo Instalando Torch com suporte a CUDA 11.8...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
) else (
    echo Torch ja esta instalado.
)

:: Verificar e instalar outras dependencias apenas se necessario
for %%P in (prompt_toolkit tqdm imageio-ffmpeg ffmpeg-python) do (
    pip show %%P >nul 2>nul
    if !errorlevel! neq 0 (
        echo Instalando %%P...
        pip install %%P
    ) else (
        echo %%P ja esta instalado.
    )
)

echo Todas as dependencias foram verificadas e instaladas se necessario!

:: Executar automaticamente o script de transcricao
echo Iniciando TranscriPy...
python "%REPO_DIR%\transcribe.py"

pause
