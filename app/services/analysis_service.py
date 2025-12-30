import os
import base64
import traceback

def encode_image(image_path):
    """Encodes an image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

from app.services.fish_data import calculate_weight
import json

def analyze_with_gemini(image_path, api_key, fish_length=None):
    """Analyzes an image using Google Gemini (via google-genai SDK)."""
    try:
        from google import genai
    except ImportError:
        return "Error: google-genai is not installed. Please run: pip install google-genai"

    client = genai.Client(api_key=api_key)

    print(f"Analyzing {image_path} with Gemini...")
    
    length_info = f" The estimated length of the fish is {fish_length}cm." if fish_length else ""

    try:
        import PIL.Image
        img = PIL.Image.open(image_path)
        
        prompt = (
            "이 이미지를 분석하여 어종을 식별해 주세요. 대부분의 이미지는 한국 어시장에서 흔히 볼 수 있는 어종입니다. "
            f"{length_info} "
            "결과를 다음 키를 가진 JSON 객체로 반환해 주세요: "
            "'scientific_name'(학명, string), 'seafoodType'(어종, string), 'marketPrice'(원 단위 예상 싯가, integer), 'estimatedWeight'(kg 단위 예상 무게, number). "
            "싯가와 무게는 주어진 길이와 어종의 일반적인 특성을 바탕으로 추정해 주세요. "
            "JSON 형식만 반환하세요."
        )

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, img],
            config={
                'response_mime_type': 'application/json'
            }
        )
        
        result_text = response.text
        
        # Post-process for scientific weight calculation
        try:
            data = json.loads(result_text)
            scientific_name = data.get("scientific_name")
            
            if fish_length and scientific_name:
                calc_weight = calculate_weight(scientific_name, float(fish_length))
                # Update the estimated weight with our scientific calculation
                data["estimatedWeight"] = round(calc_weight, 2)
                
                # Update text representation if needed, but we return string currently.
                # The caller (fish.py) re-parses JSON. So we should return the updated JSON string.
                return json.dumps(data, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to calculate scientific weight: {e}")
        
        return result_text
    except Exception as e:
        return f"Gemini Error: {e}"

def analyze_with_gpt(image_path, api_key, fish_length=None):
    """Analyzes an image using OpenAI GPT-4o."""
    try:
        from openai import OpenAI
    except ImportError:
        return "Error: openai is not installed. Please run: pip install openai"

    client = OpenAI(api_key=api_key)
    
    base64_image = encode_image(image_path)
    
    length_info = f" The estimated length of the fish is {fish_length}cm." if fish_length else ""

    print(f"Analyzing {image_path} with GPT-4o...")

    prompt = (
        "이 이미지를 분석하여 어종을 식별해 주세요. 대부분의 이미지는 한국 어시장에서 흔히 볼 수 있는 어종입니다. "
        f"{length_info} "
        "결과를 다음 키를 가진 JSON 객체로 반환해 주세요: "
        "'scientific_name'(학명, string), 'seafoodType'(어종, string), 'marketPrice'(원 단위 예상 싯가, integer), 'estimatedWeight'(kg 단위 예상 무게, number). "
        "싯가와 무게는 주어진 길이와 어종의 일반적인 특성을 바탕으로 추정해 주세요."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=300,
        )
        result_text = response.choices[0].message.content
        
        # Post-process for scientific weight calculation
        try:
            data = json.loads(result_text)
            scientific_name = data.get("scientific_name")
            
            if fish_length and scientific_name:
                calc_weight = calculate_weight(scientific_name, float(fish_length))
                data["estimatedWeight"] = round(calc_weight, 2)
                return json.dumps(data, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to calculate scientific weight: {e}")

        return result_text
    except Exception as e:
        return f"GPT Error: {e}\n{traceback.format_exc()}"
