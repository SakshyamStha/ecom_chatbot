from django.shortcuts import render
from .models import *

def shop(request):
    products=Product.objects.all()
    context={'products':products}
    return render(request,'shop/shop.html',context)

def cart(request):
    context={}
    return render(request,'shop/cart.html',context)

def checkout(request):
    context={}
    return render(request,'shop/checkout.html',context)

def categories(request):
    context={}
    return render(request,'shop/categories.html',context)

def login(request):
    context={}
    return render(request,'shop/login.html',context)

def aboutus(request):
    context={}
    return render(request,'shop/aboutus.html',context)

def contactus(request):
    context={}
    return render(request,'shop/contactus.html',context)



# for the chatbot

from django.http import JsonResponse
from .naive_bayes_chatbot import generate_response  # Import your chatbot function

def chatbot_view(request):
    user_message = request.GET.get('message', '')  # Capture the user’s message from a GET request
    if user_message:
        bot_response = generate_response(user_message)  # Generate chatbot response
    else:
        bot_response = "ramrari bol"

    return JsonResponse({'response': bot_response})  # Return JSON response to the frontend


def chatbot_page(request):
    context={}
    return render(request, 'shop/chatbot.html',context)
