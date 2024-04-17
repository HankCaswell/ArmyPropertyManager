from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST)
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login
from .models import Unit, Equipment, Transaction, UserProfile, Cart,  CartItem
from .serializers import UserRegistrationSerializer, UserProfileSerializer, FileUploadSerializer, EquipmentSerializer
from .serializers import UnitSerializer
from rest_framework.generics import ListAPIView
from django.views.generic import DetailView
from rest_framework.permissions import IsAuthenticated, AllowAny
from autoHR.utils.pdf_parser import extract_text_from_pdf, parse_equipment_details, debug_parse_equipment_details
from.models import Equipment
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db import transaction
from django.utils import timezone


class UserCreate(APIView): 

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data= request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user: 
                token, _ = Token.objects.get_or_create(user=user)  
                return Response({'token': token.key}, status=HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = get_object_or_404(UserProfile, user=user)
        cart_items = CartItem.objects.filter(cart__user=user)   #.select_related('equipment')

        profile_data = UserProfileSerializer(profile).data
        cart_items_data = EquipmentSerializer([item.equipment for item in cart_items], many=True).data
        
        # Merge profile data and cart items into one response
        response_data = {
            'profile': profile_data,
            'cart_items': cart_items_data
        }

        return Response(response_data, HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, HTTP_200_OK)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)    
    
# class UserProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         profile = UserProfile.objects.get(user=request.user)
#         serializer = UserProfileSerializer(profile)
#         return Response(serializer.data, status=HTTP_200_OK)
    
#     def post(self, request, *args, **kwargs):
#         profile = UserProfile.objects.get(user=request.user)
#         serializer = UserProfileSerializer(profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=HTTP_200_OK)
#         return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request=request, username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=HTTP_400_BAD_REQUEST)

class UnitCreate (APIView):
    def post(self, request, format='json'):
        serializer = UnitSerializer(data= request.data)
        if serializer.is_valid():
            unit = serializer.save()
            if unit: 
                return Response(serializer.data, HTTP_201_CREATED)
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)
    
class CreateUnitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = UnitSerializer(data= request.data)
        if serializer.is_valid():
            unit = serializer.save()
            return Response({'unit_id': unit.id}, status =HTTP_201_CREATED)
        return Response(serializer.errors, status = HTTP_400_BAD_REQUEST)

class UnitListView(APIView):
    def get(self, request):
        queryset = Unit.objects.all()
        serializer= UnitSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

class PDFTextView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            extracted_text = extract_text_from_pdf(file)
            equipment_details = parse_equipment_details(extracted_text)
            
            # Fetch the unit instance only once using the ID provided in the request
            unit_instance = get_object_or_404(Unit, id=request.data.get('unit_id'))

            with transaction.atomic():  # Use a transaction to ensure all or none of the operations are committed
                created_count = 0
                for item in equipment_details:
                    nsn = item.get('nsn', '')
                    name = item.get('name', '')
                    lin = item.get('lin', '')
                    quantity = int(item.get('quantity', 1))  # Convert quantity to integer

                    # Handle serial numbers or create default ones if none exist
                    serial_numbers = item.get('serial_numbers', [])
                    if not serial_numbers:  # If no serial numbers, create default unique identifiers
                        serial_numbers = [f"unique_default_{i+1}" for i in range(quantity)]

                    # Adjust the quantity of serial numbers to match the quantity specified
                    while len(serial_numbers) < quantity:
                        serial_numbers.append(f"unique_default_{len(serial_numbers)+1}")

                    # Create an equipment instance for each serial number up to the quantity specified
                    for index in range(quantity):
                        serial_number = serial_numbers[index] if index < len(serial_numbers) else f"unique_default_{index+1}"
                        Equipment.objects.create(
                            nsn=nsn,
                            name=name,
                            lin=lin,
                            serial_number=serial_number,
                            quantity=1,  # Each entry represents one unit
                            unit=unit_instance
                        )
                        created_count += 1

                # Return a response indicating how many items were created
                return Response({"message": f"{created_count} equipment items created successfully."}, status=HTTP_200_OK)

        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


#Shows equipment summary for a particular unit
class EquipmentSummaryView(APIView):
    def get(self, request, *args, **kwargs):
        # Retrieve unit identifier from request query parameters
        unit_id = request.query_params.get('unit_id')
        unit_name = request.query_params.get('unit_name')

        # Build the base queryset
        queryset = Equipment.objects.all()

        # Filter queryset based on the provided unit identifier
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        elif unit_name:
            queryset = queryset.filter(unit__name=unit_name)

        if not queryset.exists():
            return Response({"error": "No equipment found for the given unit."}, status=HTTP_400_BAD_REQUEST)

        # Aggregate data by name and NSN
        equipment_summary = queryset.values(
            'name', 'nsn', 'status', 'id'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('name', 'nsn')  # Ensuring a consistent order

        return Response({
            "equipment_summary": list(equipment_summary)
        }, status=HTTP_200_OK)

#Shows equipment details for a particular piece of equipment
class EquipmentDetailView(APIView):
    def get(self, request, equipment_id):
        # Retrieve the equipment instance or return a 404 response
        equipment = get_object_or_404(Equipment, pk=equipment_id)

        # Serialize the equipment instance and return the data
        serializer = EquipmentSerializer(equipment)
        return Response(serializer.data, status=HTTP_200_OK)
    


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        equipment_id = request.data.get('equipment_id')
        quantity = int(request.data.get('quantity', 1))

        equipment = get_object_or_404(Equipment, id=equipment_id)
        if equipment.quantity < quantity or equipment.status != 'Available':
            return Response({'error': 'Insufficient quantity or equipment not available'}, status=HTTP_400_BAD_REQUEST)

        cart, created = Cart.objects.get_or_create(user=request.user)
       
        transaction = Transaction.objects.create(
            user = request.user,
            equipment = equipment,
            checkout_date = timezone.now(),
            return_date = None,
            status = 'Borrowed'
        )
        
        CartItem.objects.create(cart=cart, equipment=equipment, quantity=quantity, transaction= transaction)


        equipment.quantity -= quantity  # Decrement the stock quantity
        equipment.status = 'Borrowed'
        equipment.save()

        return Response({'status': 'added to cart'}, status=HTTP_201_CREATED)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        transaction_items = []

        with transaction.atomic():
            for item in cart.cartitem_set.all():
                Transaction.objects.create(
                    user=request.user,
                    equipment=item.equipment,
                    expected_return_date=request.data.get('expected_return_date'),
                    status='signed_out'
                )
                item.equipment.quantity -= item.quantity  # Assuming quantity management
                item.equipment.save()
                transaction_items.append(item.equipment.name)
                item.delete()

        return Response({'status': 'checkout completed', 'items': transaction_items}, status=HTTP_200_OK)


class ReturnEquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        transaction_id = request.data.get('transaction_id')
        transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
        
        transaction.return_date = timezone.now()  # Set the return date
        transaction.status = 'Returned'
        transaction.save()

        equipment = transaction.equipment
        equipment.quantity += 1  # Increment the stock quantity
        equipment.status = 'Available'
        equipment.save()

        # Optionally, remove the CartItem
        CartItem.objects.filter(transaction=transaction).delete()

        return Response({'status': 'equipment returned'}, status=HTTP_200_OK)
    
    # This worked to actually return the equipment but it did not send the transaction_id in the request of the body, when tied in to the front end, so it is commented out for now. 
# class ReturnEquipmentView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         transaction_id = request.data.get('transaction_id')
#         transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

#         if transaction.status != 'Available':
#             transaction.return_date = timezone.now()
#             transaction.status = 'Available'
#             transaction.save()

#             equipment = transaction.equipment
#             equipment.quantity += 1
#             equipment.save()

#             CartItem.objects.filter(cart__user=request.user, equipment=equipment).delete()
#             return Response({'status': 'equipment returned'}, status=HTTP_200_OK)
#         else: 
#             return Response({'error': 'Equipment already returned'}, status=HTTP_400_BAD_REQUEST)
        
class CartView(DetailView):
    model = Cart
    template_name = 'cart_detail.html'
    context_object_name = 'cart'

    def get_object(self):
        # Ensures that we return the cart for the currently logged-in user
        return Cart.objects.get(user=self.request.user)

class UserCheckedOutEquipmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        transactions = Transaction.objects.filter(user=request.user, status='signed_out')
        serializer = EquipmentSerializer([transaction.equipment for transaction in transactions], many=True)
        return Response(serializer.data, status=HTTP_200_OK)
