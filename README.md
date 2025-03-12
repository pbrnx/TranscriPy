# TranscriPy

## Sobre o projeto

**TranscriPy** é uma aplicação CLI (pretendo adicionar um frontend em breve, contribuições são bem-vindas!) para transcrição de áudio baseada no modelo **Whisper** da OpenAI. Ela permite que você converta arquivos de áudio em texto de forma rápida e precisa, suportando vários idiomas e formatos de saída, como **TXT** e **SRT**.

## Funcionalidades

- Suporte a múltiplos modelos Whisper (**tiny**, **base**, **small**, **medium**, **large**)
- Opção de escolha entre diferentes idiomas de transcrição
- Possibilidade de salvar a transcrição em **TXT** ou **SRT**
- Uso otimizado de **CUDA** quando disponível
- Interface interativa via **prompt_toolkit**
- Barra de progresso para acompanhamento da transcrição
- Suporte a FFmpeg para processamento de áudio

## Requisitos

Antes de rodar o **TranscriPy**, certifique-se de ter os seguintes requisitos instalados:

- **Python 3.8+ (Recomendo a 3.11)**
- **pip** atualizado
- **FFmpeg** (incluso no projeto)
- **PyTorch** (com suporte a CUDA, se disponível)
- **Whisper** da OpenAI
- **prompt_toolkit**
- **tqdm**

### Instalando dependências

Execute o arquivo .bat para instalar todas as dependências automaticamente. Para funcionar corretamente, é necessário ter o Python e o PIP funcionais.


## Como usar

1. Execute o script **TranscriPy**:

   ```bash
   python transcripy.py
   ```

2. Escolha o formato da transcrição (**TXT** ou **SRT**)
3. Selecione o modelo Whisper desejado
4. Escolha o idioma da transcrição
5. Informe o caminho do arquivo de áudio
6. Aguarde a transcrição e verifique o arquivo salvo no mesmo diretório do áudio original

## Autor

Desenvolvido por **Pedro Barone**.

