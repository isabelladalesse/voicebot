language = 'pt'

from IPython.display import Audio, display, Javascript
from google.colab import output
from base64 import b64decode


# função que grava o audio em javascript
RECORD = """
const sleep = time => new Promise(resolve => setTimeout(resolve,time))
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader()
  reader.onloadend = e => resolve(e.srcElement.result)
  reader.readAsDataURL(blob)
})
var record = time => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true})
  recorder = new MediaRecorder(stream)
  chunks = []
  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.start()
  await sleep(time)
  recorder.onstop = async ()=>{
    blob = new Blob(chunks)
    text = await b2text(blob)
    resolve(text)
  }
  recorder.stop()
})
"""

# função que grava o audio em python (chama a gravação em javascript)
def record(sec=5): # parâmetro: qntd de seg gravado com padrão 5
  display(Javascript(RECORD)) # interpreta o código javascript
  js_result = output.eval_js(f'record({sec * 1000})') # chama o código javascript com o parâmetro seg
  audio = b64decode(js_result.split(",")[1]) # pega o resultado (gravação) do código javascript, que vem codificado em base64, e decodifica
  file_name = 'request_audio.wav' # salva a gravação
  with open(file_name, 'wb') as f:
    f.write(audio) # abre e escreve o audio
  return file_name # retorna o caminho do arquivo

print("Diga alguma coisa!")
record_file = record() # chama a função
display(Audio(record_file))

! pip install git+https://github.com/openai/whisper.git -q

import whisper

model = whisper.load_model("small")
result = model.transcribe(record_file, fp16=False, language = 'pt')
transcription = result["text"]
print(transcription)

from google import genai

client = genai.Client(api_key="SUA_API_KEY_AQUI")

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        {
            "role": "user",
            "parts": [{"text": transcription}]
        }
    ]
)

print(response.text)

! pip install gTTS click>=8.2.1

from gtts import gTTS

gtts_object = gTTS(text=response.text, lang=language, slow=False)
response_audio="response_audio.wav"
gtts_object.save(response_audio)
display(Audio(response_audio, autoplay=True))
