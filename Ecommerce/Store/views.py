from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from django.utils import timezone
from .models import *

from . utils import cartCookies, cartData

def Items(request):

    Data = cartData(request)
    cartItems = Data['cartItems']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request,'store/Items.html',context)
def Cart(request):
        
    Data = cartData(request)
    items = Data['items']
    order = Data['order']
    cartItems = Data['cartItems']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,"store/Cart.html",context)
def Checkout(request):

    Data = cartData(request)
    items = Data['items']
    order = Data['order']
    cartItems = Data['cartItems']


    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,"store/Checkout.html",context)


def UpdateItem(request):
    data = json.loads(request.body)
    ProductId = data['ProductId']
    Action = data['Action']

    print('Action:', Action)
    print('ProductId:', ProductId)

    customer = request.user.customer
    product = Product.objects.get(id = ProductId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)
    orderitem, created = OrderItem.objects.get_or_create(order = order, product = product)

    if Action == 'add' :
        orderitem.quantity = (orderitem.quantity + 1)
    elif Action == 'remove' :
        orderitem.quantity = (orderitem.quantity -1)

    orderitem.save()

    if orderitem.quantity <= 0 :
        orderitem.delete()

    items = order.orderitem_set.all()
    cart_data = {
        'cartItems': order.get_cart,
        'cartTotal': order.get_cart_total,
        'items': [
            {
                'product_id': item.product.id,
                'name': item.product.name,
                'quantity': item.quantity,
                'price': item.product.price,
                'total': item.get_total,
                'imageURL': item.product.imageURL,
            }
            for item in items
        ]
    }

    return JsonResponse(cart_data, safe=False)

def ProcessOrder(request):
    transcation_Id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order,create = Order.objects.get_or_create(customer = customer, complete = False)

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                pincode = data['shipping']['Pincode'],

            )
        

    else:
        print('User Logged out...')

        print('COOKIES:', request.COOKIES)

        name = data['form']['name']
        email = data['form']['email']

        cookieData = cartCookies(request)
        items = cookieData['items']

        customer, created = Customer.objects.get_or_create(email = email)
        customer.name = name
        customer.save()

        order = Order.objects.create(customer = customer, complete = True)

        for item in items:
            product = Product.objects.get(id = item['product']['id'])
            orderItem = OrderItem.objects.create(product = product, order = order,quantity = item['quantity'])

    total = float(data['form']['total'])
    order.transcation_id = transcation_Id

    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            pincode = data['shipping']['Pincode'],
            )
        
    return JsonResponse('Payment Completed', safe=False)