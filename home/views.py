from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
import requests
from bs4 import BeautifulSoup
import json

# Load the trained pipeline
pipeline_mnb = joblib.load('pipeline_mnb.pkl')

@csrf_exempt
def predict_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data['text']
            prediction = pipeline_mnb.predict([text])
            return JsonResponse({'prediction': prediction[0]})

        except Exception as e:
            return JsonResponse({'error': str(e)})

@csrf_exempt
def scrape_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data['text']

            # Web scraping logic
            url = "https://www.whois.com/whois/" + text
            response = requests.get(url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                df_block = soup.find('div', class_='df-block')

                if df_block:
                    heading = df_block.find('div', class_='df-heading').text.strip()
                    df_rows = df_block.find_all('div', class_='df-row')
                    scraped_data = {}

                    for df_row in df_rows:
                        label = df_row.find('div', class_='df-label').text.strip()
                        value = df_row.find('div', class_='df-value').text.strip()
                        scraped_data[label] = value

                    return JsonResponse({'scraped_data': scraped_data})

                else:
                    return JsonResponse({'error': "No df-block found in the HTML content."})

            else:
                return JsonResponse({'error': f"Failed to retrieve the web page. Status code: {response.status_code}"})

        except Exception as e:
            return JsonResponse({'error': str(e)})

def index(request):    
    return HttpResponse('<h1>Hello World</h1>') 

