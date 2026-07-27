from rest_framework import serializers
from .models import Document, DocumentMetadata
from apps.accounts.serializers import UserSerializer
from apps.common.utils import validate_pdf_file


class DocumentMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentMetadata
        fields = [
            'company_names', 'dates', 'effective_date', 'expiration_date',
            'contract_duration', 'governing_law', 'jurisdiction',
            'contract_parties', 'total_clauses_extracted'
        ]


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only=True)
    metadata = DocumentMetadataSerializer(read_only=True)
    formatted_size = serializers.CharField(read_only=True)
    risk_summary = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'file_size', 'formatted_size', 'page_count',
            'uploaded_by', 'status', 'created_at', 'updated_at', 'metadata',
            'risk_summary'
        ]
        read_only_fields = ['id', 'file_size', 'page_count', 'uploaded_by', 'status', 'created_at', 'updated_at']

    def get_risk_summary(self, obj):
        if hasattr(obj, 'risk_analysis'):
            return {
                'overall_risk_score': obj.risk_analysis.overall_risk_score,
                'risk_level': obj.risk_analysis.risk_level,
                'high_risk_count': obj.risk_analysis.high_risk_count,
            }
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(validators=[validate_pdf_file])

    class Meta:
        model = Document
        fields = ['title', 'file']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        file_obj = validated_data['file']
        
        if not validated_data.get('title'):
            validated_data['title'] = file_obj.name
            
        doc = Document.objects.create(
            title=validated_data['title'],
            file=file_obj,
            file_size=file_obj.size,
            uploaded_by=user,
            status=Document.Status.UPLOADED
        )
        return doc
