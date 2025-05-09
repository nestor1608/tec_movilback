# views.py
from django.shortcuts import render
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
            phone = serializer.validated_data["phone"]
            device = serializer.validated_data["device"]
            issue = serializer.validated_data["issue"]
            message = serializer.validated_data["message"]

            # Enviar correo
            email_message = f"""
            Nuevo mensaje de contacto:
            
            Nombre: {name}
            Email: {email}
            Teléfono: {phone}
            Dispositivo: {device}
            Problema: {issue}
            
            Mensaje:
            {message}
            """

            send_mail(
                subject=f"Nuevo mensaje de contacto de {name}",
                message=email_message,
                from_email=None,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
            )

            # Enviar WhatsApp usando CallMeBot
            try:
                whatsapp_msg = f"""
                Nuevo mensaje en la web:
                Nombre: {name}
                Email: {email}
                Teléfono: {phone}
                Dispositivo: {device}
                Problema: {issue}
                
                Mensaje: {message}
                """
                whatsapp_url = f"https://api.callmebot.com/whatsapp.php?phone={settings.CLIENT_WHATSAPP_PHONE}&text={requests.utils.quote(whatsapp_msg)}&apikey={settings.CALLMEBOT_API_KEY}"
                requests.get(whatsapp_url)
            except Exception as e:
                print("Error enviando WhatsApp:", e)

            return Response({"message": "Mensaje enviado correctamente"}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)