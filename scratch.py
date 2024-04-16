from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Unit, Equipment
from .utils.pdf_parser import parse_pdf  # Import the utility function

class UploadHandReceiptView(APIView):
    def post(self, request, unit_id):
        unit = get_object_or_404(Unit, pk=unit_id)
        file = request.FILES.get('file')
        
        if not file:
            return Response({'error': 'No file provided.'}, status=400)
        
        equipment_details = parse_pdf(file)
        
        # Create Equipment instances based on the parsed data
        for detail in equipment_details:
            Equipment.objects.create(unit=unit, **detail)
            
        return Response({'status': 'success'})
    
import fitz  # PyMuPDF

def parse_pdf(file_stream):
    """
    Parses the given PDF file stream and extracts equipment details.
    
    :param file_stream: A file-like object for the PDF.
    :return: A list of dictionaries, each containing details of an equipment item.
    """
    doc = fitz.open(stream=file_stream, filetype="pdf")
    equipment_details = []
    
    for page in doc:
        text = page.get_text()
        # Implement your custom parsing logic here
        # For example, split the text into lines and parse each line
        for line in text.split('\n'):
            # Example parsing logic; adjust based on your PDF format
            details = line.split()
            if details:
                equipment_details.append({
                    'name': details[0],
                    'serial_number': details[1],
                    # Add more fields as per your requirement
                })
                
    return equipment_details