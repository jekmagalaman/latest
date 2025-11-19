from rest_framework import serializers
from apps.gso_migration.models import MigrationUpload

class MigrationUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MigrationUpload
        fields = '__all__'

class MigrationUploadCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MigrationUpload
        fields = [
            'file',
            'migration_type',
            'target_unit',
            'uploaded_by',
            'processed',
            'result_message',
        ]
        read_only_fields = ['uploaded_by', 'processed', 'result_message']
