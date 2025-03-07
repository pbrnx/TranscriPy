@echo off
setlocal enabledelayedexpansion

:: Diretório do projeto
set "REPO_DIR=%~dp0TranscriPy"
set "GITHUB_URL=https://github.com/pbrnx/TranscriPy.git"

:: Ocultar saída dos comandos
set SILENT_OUTPUT=^>nul 2^>nul

echo Verificando atualizacao do TranscriPy...

:: Verificar se Git esta instalado
where git %SILENT_OUTPUT%
if %errorlevel% neq 0 (
    echo Erro: Git nao esta instalado! Baixe do site: https://git-scm.com/
    exit /b
)

:: Se o repositório não existir, clonar do GitHub
if not exist "%REPO_DIR%" (
    echo Baixando TranscriPy pela primeira vez...
    git clone %GITHUB_URL% "%REPO_DIR%" %SILENT_OUTPUT%
    cd /d "%REPO_DIR%"
) else (
    cd /d "%REPO_DIR%"
    git fetch origin %SILENT_OUTPUT%
    
    :: Identificar a branch principal (main ou master)
    for /f %%b in ('git branch -r ^| findstr /r "origin/main origin/master"') do set "BRANCH=%%b"
    if "%BRANCH%"=="" (
        echo Nenhuma atualizacao encontrada.
    ) else (
        for /f %%i in ('git rev-parse HEAD') do set "LOCAL_COMMIT=%%i"
        for /f %%i in ('git rev-parse %BRANCH%') do set "REMOTE_COMMIT=%%i"

        if not "!LOCAL_COMMIT!"=="!REMOTE_COMMIT!" (
            echo Atualizando para a versao mais recente...
            git pull origin %BRANCH% %SILENT_OUTPUT%
        ) else (
            echo Codigo ja esta atualizado.
        )
    )
)

:: Instalar dependencias apenas se necessario
echo Verificando dependencias...

pip show whisper %SILENT_OUTPUT%
if %errorlevel% neq 0 pip install git+https://github.com/openai/whisper.git %SILENT_OUTPUT%

pip show torch %SILENT_OUTPUT%
if %errorlevel% neq 0 pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 %SILENT_OUTPUT%

for %%P in (prompt_toolkit tqdm imageio-ffmpeg ffmpeg-python) do (
    pip show %%P %SILENT_OUTPUT%
    if !errorlevel! neq 0 pip install %%P %SILENT_OUTPUT%
)

:: Executar TranscriPy em um novo terminal
echo Iniciando TranscriPy...
start cmd /k python "%REPO_DIR%\transcribe.py"

exit
