from rest_framework import serializers

class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    device = serializers.CharField(max_length=50)
    issue = serializers.CharField(max_length=50)
    message = serializers.CharField()