from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import get_gemini_response

@csrf_exempt  # for testing (you can secure it later)
def chat(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        if not user_message:
            return JsonResponse({"error": "No message provided"}, status=400)

        # Get Gemini’s AI response
        ai_reply = get_gemini_response(user_message)
        return JsonResponse({"response": ai_reply})

    return JsonResponse({"error": "POST request required"}, status=400)
