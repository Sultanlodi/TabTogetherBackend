 # TapTogetherBackend/bills_api/views.py

import os
import base64
import json
from django.conf import settings
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser # For handling file uploads
from rest_framework.response import Response
from rest_framework.views import APIView
import google.generativeai as genai # Ensure this is installed: pip install google-generativeai
from .models import Bill, BillItem
from .serializers import BillSerializer, BillItemSerializer

# Configure the Gemini API using the key from settings.py (loaded from .env)
genai.configure(api_key=settings.GEMINI_API_KEY)

class BillUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser) # Allows for file uploads via form data (like image)

    def post(self, request, *args, **kwargs):
        # 1. Receive the image file from the request
        uploaded_file = request.FILES.get('image')

        if not uploaded_file:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Create an initial Bill record to save the image. This saves the file to MEDIA_ROOT.
        bill = Bill(uploaded_image=uploaded_file)
        bill.save()

        # 2. Prepare the image for Gemini API (read from saved file path and Base64 encode)
        try:
            with open(bill.uploaded_image.path, "rb") as image_file:
                encoded_image_string = base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            # If for some reason the file wasn't found after being saved
            return Response({"error": "Failed to read uploaded image file from storage."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # 3. Call the Gemini API
            # Use 'gemini-pro-vision' model for multimodal input (text + image)
            model = genai.GenerativeModel('gemini-pro-vision')
            prompt = """
            You are an expert at extracting information from restaurant bills/receipts.
            From the following image, extract all individual items, their quantities (if present), and their prices.
            Also, identify the subtotal, tax, and total amount.
            Return the information in a JSON format. If a quantity is not explicitly stated, assume 1.
            Example JSON structure:
            {
              "items": [
                {"description": "Burger", "quantity": 1, "price": 12.50},
                {"description": "Fries", "quantity": 2, "price": 4.00}
              ],
              "subtotal": 20.50,
              "tax": 1.50,
              "total": 22.00,
              "currency": "USD" # Or inferred currency
            }
            If any field is not found or cannot be reliably extracted, set its value to null.
            Only return the JSON object, do not include any explanatory text outside the JSON.
            """

            # Format the image for the Gemini API
            image_part = {
                "mime_type": uploaded_file.content_type, # e.g., "image/jpeg"
                "data": encoded_image_string,
            }

            # Generate content from the model
            response = model.generate_content([prompt, image_part])
            gemini_response_text = response.text.strip() # Get the text response and remove leading/trailing whitespace
            print("Gemini Raw Response:", gemini_response_text) # Good for debugging Gemini's output

            # 4. Parse Gemini's Response
            # Gemini's response might sometimes include markdown (```json ... ```)
            try:
                if gemini_response_text.startswith("```json") and gemini_response_text.endswith("```"):
                    # Remove the markdown code block delimiters
                    json_str = gemini_response_text[7:-3].strip()
                else:
                    json_str = gemini_response_text

                parsed_data = json.loads(json_str)

                # Update the Bill model with parsed data
                bill.gemini_raw_response = parsed_data
                bill.total_amount = parsed_data.get('total') # Extract total amount
                bill.is_processed = True # Mark as successfully processed
                bill.save()

                # Save individual items if available in the parsed data
                items_data = parsed_data.get('items', [])
                for item_data in items_data:
                    # Basic validation to ensure price is a number before creating
                    try:
                        price = float(item_data.get('price'))
                    except (ValueError, TypeError):
                        price = 0.0 # Default to 0 if price is invalid or missing

                    BillItem.objects.create(
                        bill=bill, # Link to the current bill
                        description=item_data.get('description', 'N/A'),
                        price=price,
                        # quantity=item_data.get('quantity', 1) # If you add quantity to BillItem model
                    )

            except json.JSONDecodeError as e:
                # Handle cases where Gemini's response is not valid JSON
                print(f"Error decoding JSON from Gemini response: {e}")
                print("Response that caused error:", gemini_response_text)
                bill.gemini_raw_response = {"error": "Failed to parse Gemini response JSON.", "raw_text": gemini_response_text}
                bill.is_processed = False # Mark as not fully processed
                bill.save()
                return Response(
                    {"message": "Bill uploaded, but Gemini response could not be fully parsed.",
                     "raw_gemini_output": gemini_response_text,
                     "bill_id": bill.id},
                    status=status.HTTP_202_ACCEPTED # Accepted but with processing issues
                )

            # 5. Return a successful response with the bill data
            serializer = BillSerializer(bill)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Catch any other unexpected errors from Gemini API or other logic
            print(f"Error during Gemini API call or bill processing: {e}")
            bill.is_processed = False
            bill.gemini_raw_response = {"error": str(e), "message": "An unexpected error occurred during processing."}
            bill.save()
            return Response({"error": f"Failed to process bill: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BillDetailView(APIView):
    def get(self, request, pk, *args, **kwargs):
        try:
            bill = Bill.objects.get(pk=pk)
            serializer = BillSerializer(bill)
            return Response(serializer.data)
        except Bill.DoesNotExist:
            return Response({"error": "Bill not found."}, status=status.HTTP_404_NOT_FOUND)

    # You could add PUT/PATCH for updating bill details or splitting assignments here later
    # def put(self, request, pk, *args, **kwargs):
    #     # Logic to update bill or split details
    #     pass