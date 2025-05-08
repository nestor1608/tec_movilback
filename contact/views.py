from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from .serializers import ContactSerializer
import requests
from django.conf import settings

class ContactFormView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data["name"]
            email = serializer.validated_data["email"]
            message = serializer.validated_data["message"]

            # Enviar correo
            send_mail(
                subject=f"Nuevo mensaje de {name}",
                message=f"Email: {email}\n\n{message}",
                from_email=None,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            # Enviar WhatsApp usando CallMeBot
            try:
                whatsapp_msg = f"Nuevo mensaje en la web:\nDe: {name}\nEmail: {email}\nMensaje: {message}"
                whatsapp_url = f"https://api.callmebot.com/whatsapp.php?phone={settings.CLIENT_WHATSAPP_PHONE}&text={requests.utils.quote(whatsapp_msg)}&apikey={settings.CALLMEBOT_API_KEY}"
                requests.get(whatsapp_url)
            except Exception as e:
                print("Error enviando WhatsApp:", e)

            return Response({"message": "Mensaje enviado correctamente"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
