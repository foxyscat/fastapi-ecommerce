from fastapi import  Request
import iyzipay

async def   payment(buyer:dict,address:dict,basket_items:list[dict]):
    options = {
    'api_key': 'sandbox',
    'secret_key': 'sandbox',
    'base_url': 'sandbox-api.iyzipay.com'
    }
    sum = 0
    if len(basket_items) > 1:
        for i in range(len(basket_items)):
            sum = sum + basket_items[i]['price']
            print(sum)
    elif len(basket_items) == 1:
        sum = sum + basket_items[0]['price']
        print(sum)
    
    request = {
    'locale': 'tr',
    'conversationId': '123456789',
    'price': sum,
    'paidPrice': sum,
    'currency': 'TRY',
    'installment': '1',
    'basketId': 'B67832',
    'paymentGroup': 'PRODUCT',
    "callbackUrl": "http://localhost:8000/payment",
    "enabledInstallments": ['2', '3', '6', '9'],
    'buyer': buyer,
    'shippingAddress': address,
    'billingAddress': address,
    'basketItems': basket_items
    }
    checkout_form_result = iyzipay.CheckoutFormInitialize().create(request, options)
    return checkout_form_result.read().decode('utf-8')

            