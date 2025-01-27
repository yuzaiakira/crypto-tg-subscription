translations = {
    'en': {
        'start': "Hello {name} Welcome to TCP bot \nFor see our plans: /plan",
        'lang': {
            'name': "English",
            'set': "Language set to English.",
            'reply_set': "you selected Language to English.", 
            'invalid': "Invalid language selection!",
        },
        'plans':{
            'description': "plese select your membership palan from below btn",
            'invalid_plan': "your plan is invalid",
            'pay':"Please send `{amount}` USDT to the following address within 1 hour:\n`{send_address}`\n"\
                "Make sure to send exactly `{amount}` USDT (TRC20 network) from this address:\n{user_address}\n" \
                "We'll automatically detect your transaction once confirmed (usually 15-20 minutes).\n" \
                "You can check status with /check command.",
                
            'pending': "you have pending order!! \n"\
                       "Before proceeding, please complete the payment for your current order or cancel it if you no longer wish to proceed. \n"\
                        "/order - Cancel Order",
                        
            'plans_list': ["$10 for 1 montamounth",
                           "$29 for 3 month",
                           "$100 for 12 month",
                      ]
        },
        'wallet': {
            'notic': "please set your wallet by /wallet",
            'get': "Please enter your wallet address:",
            'change': "your wallet address is: `{wallet}` \n"\
                       "for set new wallet address, please enter your wallet address\n"\
                       "or you can /cancel",
            'success': "Your wallet address has been saved!\n{wallet}",
            'invalid': "Invalid wallet address. Please try again.",
            'cancel': "The operation has been canceled."
            
        },
        'order': {
            'canceling': "All your pending orders have been successfully canceled.",
            'accept': "Your payment has been accepted, and your membership has been extended until {date}.\nThank you for your trust and support!",
            'unable': """We were unable to process your payment at this time. Please ensure:

    - Your wallet has sufficient funds.
    - The correct amount was sent to the deposit address.
    - The transaction was completed successfully.

If you believe this is an error, please contact our support team for assistance.

Thank you for your patience!
            """,
            'no_order': "you have no payment."
        }
    },
}

translations['fa'] = translations['en']

subscription_plan = {
    'plan_0': {
        'amount': 10,
        'duration_days': 30
        },
    'plan_1': {
        'amount': 29,
        'duration_days': 90
        },
    'plan_2': {
        'amount': 100,
        'duration_days': 365
        }
}
