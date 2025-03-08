from rest_framework import serializers
from core.models import PsychoTest, TestSession

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PsychoTest
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestSession
        fields = '__all__'
