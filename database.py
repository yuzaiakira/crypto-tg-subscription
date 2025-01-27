from peewee import *
from telegram import Update

import datetime
from tg_core.logger import logger
from tron import generate_deposit_address, check_tron_transaction


db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db
        
        
class User(BaseModel):
    telegram_id = IntegerField(unique=True)
    lang = CharField(default="en", max_length=3, constraints=[Check("lang IN ('en', 'fa')")])
    wallet_address = CharField(null=True)
    membership_expiry = DateTimeField(null=True)
    
    @classmethod
    def get_user(cls, telegram_id:int) -> 'User':
        """
        Retrieve or create a user by their Telegram ID.

        Args:
            telegram_id (int): The Telegram ID of the user.

        Returns:
            User: The retrieved or newly created user.
        """
        user, created = cls.get_or_create(telegram_id=telegram_id)
        return user
    
    @classmethod
    def get_wallet(cls, telegram_id:int) -> str | None:
        """
        Get user wallet address by their Telegram ID.

        Args:
            telegram_id (int): The Telegram ID of the user.

        Returns:
            str: User wallet address.
            None: If User has no wallet address.
        """
        user = cls.get_user(telegram_id=telegram_id)
        return user.wallet_address
    
    @classmethod
    def has_wallet(cls, telegram_id:int) -> bool:
        """
        check user has wallet address or not by their Telegram ID.

        Args:
            telegram_id (int): The Telegram ID of the user.

        Returns:
            bool: If User has wallet addres return True.
        """
        wallet = cls.get_wallet(telegram_id=telegram_id)
        
        if wallet:
            return True
        
        return False
    
    @classmethod
    def set_wallet_address(cls, telegram_id:int, wallet_address: str) -> None:
        """
        Set or update the user's wallet_address.

        Args:
            telegram_id (int): The Telegram ID of the user.
            wallet_address (str): The wallet address

        Raises:
            ValueError: If telegram_id or wallet_address is None.
        """
        if not telegram_id or not wallet_address:
            raise ValueError("telegram_id or wallet_address is None")

        # Use upsert to insert or update the user's language
        cls.insert(telegram_id=telegram_id, wallet_address=wallet_address).on_conflict(
            conflict_target=[cls.telegram_id],  # Correct conflict target
            update={cls.wallet_address: wallet_address}             # Update the language field
        ).execute()
          
    @classmethod
    def get_language(cls, telegram_id: int) -> str:
        """
        Retrieve the user's language by their Telegram ID.
        If the user doesn't exist, create them with the default language.

        Args:
            telegram_id (int): The Telegram ID of the user.

        Returns:
            str: The user's language code.
        """
        user = cls.get_user(telegram_id=telegram_id)

        return user.lang

    @classmethod
    def get_language_by_update(cls, update: Update) -> str:
        """
        Retrieve the user's language by their Telegram ID.
        If the user doesn't exist, create them with the default language.

        Args:
            update (Update): The Telegram Update.

        Returns:
            str: The user's language code.
        """
        return  cls.get_language(update.effective_user.id)
    
    @classmethod
    def set_language(cls, telegram_id: int, lang: str) -> None:
        """
        Set or update the user's language.

        Args:
            telegram_id (int): The Telegram ID of the user.
            lang (str): The language code to set.

        Raises:
            ValueError: If telegram_id or lang is None.
        """
        if not telegram_id or not lang:
            raise ValueError("telegram_id or lang is None")

        # Use upsert to insert or update the user's language
        cls.insert(telegram_id=telegram_id, lang=lang).on_conflict(
            conflict_target=[cls.telegram_id],  # Correct conflict target
            update={cls.lang: lang}             # Update the language field
        ).execute()
    



class Payment(BaseModel):
    user = ForeignKeyField(User, backref='payments')
    amount = FloatField()
    duration_days = IntegerField()
    deposit_address = CharField()
    created_at = DateTimeField(default=datetime.datetime.now)
    expiry = DateTimeField()
    status = CharField(default='pending')  # pending/completed/expired/canceled
    tx_hash = CharField(null=True)
    
    @classmethod
    def create_user_payment(cls, telegram_id: int, amount:float, duration_days:int) -> 'Payment':
        """
        Create a new payment for a user.

        Args:
            telegram_id (int): The Telegram ID of the user.
            amount (float): The amount of the payment.

        Returns:
            Payment: The newly created Payment object.
        """
        
        user = User.get_user(telegram_id)
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        deposit_address = generate_deposit_address()
        
        return cls.create(
        user=user,
        deposit_address=deposit_address,
        amount=amount,
        duration_days=duration_days,
        expiry=expires_at
    )

    @classmethod
    def user_has_pending_payment(cls, telegram_id: int) -> bool:
        """
        Check if the user has a pending payment.
        :param telegram_id: The Telegram ID of the user.
        :return: True if the user has a pending payment, False otherwise.
        """
        try:
            user = User.get_user(telegram_id)
            # Check for pending payments
            pending_payment = cls.select().where(
                (cls.user == user) & (cls.status == 'pending')
            ).exists()
            return pending_payment
        except DoesNotExist:
            # User does not exist
            return False
    
    @classmethod
    def cancel_all_user_orders(cls, telegram_id: int) -> bool:
        """
        Cancel all pending orders for a specific user.

        Args:
            telegram_id (int): The Telegram ID of the user.

        Returns:
            bool: True if any orders were canceled, False otherwise.
        """
        try:
            # Get the user object
            user = User.get_user(telegram_id)

            # Update all pending orders for the user to 'canceled'
            query = cls.update(status='canceled').where(
                (cls.user == user) & (cls.status == 'pending')
            )
            updated_count = query.execute()

            # Return True if any orders were canceled
            return updated_count > 0
        except DoesNotExist:
            # User does not exist
            return False
    
    @classmethod
    def check_pending_payments(cls) -> None:
        pending_payments = cls.select().where(
            (cls.status == 'pending') &
            (cls.expiry > datetime.datetime.now())
        )

        for payment in pending_payments:
            logger(f"\nChecking payment for user {payment.user.telegram_id}")
            if not payment.user.wallet_address:
                logger("No wallet address registered!")
                continue
                
            payment_made = check_tron_transaction(
                payment.user.wallet_address,
                payment.deposit_address,
                payment.amount
            )

            if payment_made:
                payment.status = 'completed'
                payment.save()
                
                user = payment.user
                if user.membership_expiry and user.membership_expiry > datetime.datetime.now():
                    new_expiry = user.membership_expiry + datetime.timedelta(days=payment.duration_days)
                else:
                    new_expiry = datetime.datetime.now() + datetime.timedelta(days=payment.duration_days)
                
                user.membership_expiry = new_expiry
                user.save()
                logger("Payment verified! Membership extended.")
            else:
                logger("Payment not received")

        # Mark expired payments
        expired = cls.update(status='expired').where(
            (cls.status == 'pending') &
            (cls.expiry <= datetime.datetime.now())
        ).execute()
        if expired:
            logger(f"\nMarked {expired} expired payments")





with db:
    db.create_tables([User, Payment])
