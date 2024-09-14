import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import re
from tqdm import tqdm 

load_dotenv()
api_key = os.environ["OPENAI_API"]
client = OpenAI(api_key=api_key)

def estrai_json(stringa):
        stringa = stringa.replace("```","")
        stringa = stringa.replace("json","")
        # Trova l'indice della prima apertura e chiusura delle parentesi graffe
        start = stringa.find('{')
        end = stringa.rfind('}')
        
        if start != -1 and end != -1:
            # Estrai la sottostringa contenente il JSON
            json_str = stringa[start:end+1]
            return json_str
        else:
            return None

def inferenza(domanda, sceltemultiple):
    response = client.chat.completions.create(
        model="o1-preview",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "Sei un assistente AI specializzato nel rispondere a domande a scelta multipla per il test d'ingresso di Medicina. Il tuo compito è analizzare ogni domanda, fornire un ragionamento logico e selezionare la risposta corretta tra le opzioni fornite (da a ad e).\n\nIstruzioni:\nLeggi attentamente la domanda presentata.\nAnalizza il quesito, che può riguardare chimica, letteratura, logica matematica o fisica.\nElabora un ragionamento step-by-step per giungere alla risposta corretta.\nSeleziona la risposta più appropriata tra le opzioni disponibili (a, b, c, d, e).\nFornisci la tua risposta in formato JSON con le seguenti chiavi:\nhas_response: valore booleano (true se hai trovato una risposta, false altrimenti)\nresponse: stringa contenente la lettera associata alla risposta scelta (a, b, c, d, o e)\nSistema di punteggio:\nRisposta corretta: +1,5 punti\nNessuna risposta: 0 punti\nRisposta errata: -0,4 punti\n\nFormato della risposta:\n{ \"has_response\": true/false, \"response\": \"a\"/\"b\"/\"c\"/\"d\"/\"e\" }\nRicorda: è fondamentale fornire un ragionamento chiaro e dettagliato prima di dare la risposta finale. Se non sei sicuro della risposta, è meglio non rispondere (impostando has_response a false) piuttosto che rischiare una penalità per una risposta errata.\n"
                }
            ]
            },
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"<domanda>{domanda}</domanda>\n </sceltemultiple>{sceltemultiple}</sceltemultiple>"
                }
            ]
            }
        ]
    )
    return response.choices[0].message.content

folder_path = "./test"

medicine_test = {}

def load_test():
    for p in os.listdir(folder_path):
        file_path = f"{folder_path}/{p}"
        materia = p.split(".json")[0]
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)  # Use json.load to directly read from the file
        medicine_test[materia] = data

load_test()
somma = 0
punteggio_tot = 0
result_dictionary = {}
for k in tqdm(medicine_test.keys()):
    result_dictionary[k] = []
    for quesito in tqdm(medicine_test[k]):
        domanda = quesito['domanda']
        scmlt = quesito['sceltemultiple']
        passa = False
        response = inferenza(domanda, scmlt)
        response = estrai_json(response)
        print(response)
        result = json.loads(response)
                
        
        punteggio = 0
        if result['has_response']:
            if result['response'].lower() == 'a':
                punteggio += 1.5
            else:
                punteggio -= 0.4
        punteggio_tot+=punteggio
        result_dictionary[k].append({"materia":k, "domanda":domanda, "punteggio":punteggio})

print(punteggio_tot)

# Salviamo il dizionario
with open('output.json', 'w', encoding='utf-8') as json_file:
    json.dump(result_dictionary, json_file, indent=4)
        
