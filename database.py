from peewee import *
from telegram import Update

import datetime
from logger import logger
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
        
        if created:
            logger.info(f"create new usser: {telegram_id}")
            
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
        
        logger.info(f"{telegram_id} update wallet address to {wallet_address}")
          
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
        
        logger.info(f"{telegram_id} change languge to {lang}")
    
    @classmethod
    def has_membership(cls, telegram_id:int) -> bool:
        """
        Check if a user with the given Telegram ID has an active membership.

        A user is considered to have an active membership if their `membership_expiry`
        field is set and the expiry date is in the future.

        Args:
            telegram_id (int): The Telegram ID of the user to check.

        Returns:
            bool: True if the user has an active membership, False otherwise.
        """
        try:
            user = cls.get_user(telegram_id=telegram_id)
            
            if user.membership_expiry and user.membership_expiry > datetime.now():
                return True
            return False
        
        except DoesNotExist:
            return False


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
        
        logger.info(f"create payment order for {telegram_id}")
        
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

            logger.info(f'{telegram_id} cancel all order')

            return updated_count > 0
        except DoesNotExist:
            return False
    
    @classmethod
    def check_user_payments(cls, telegram_id: int) -> bool:
        """
        Process pending payments for a specific user and update membership accordingly.

        Args:
            telegram_id (int): Telegram ID of the user to process payments for

        Returns:
            bool: True if at least one payment was successfully processed, False otherwise
        """
        user = User.get_user(telegram_id)
        
        any_payment_successful = False
        now = datetime.datetime.now(datetime.timezone.utc)
        
        processed_count = 0
        expired_count = 0
        errors = 0
        
        try:
            pending_payments = cls.select().where(
                (cls.user == user) &
                (cls.status == 'pending') &
                (cls.expiry > now)
            ).order_by(cls.expiry.asc())  # Process oldest first
            
            expired_count = cls.mark_expired_payments(now, telegram_id)
            
            if expired_count:
                logger.info(f"Marked {expired_count} expired payments for user {telegram_id}")

            if not pending_payments:
                logger.info(f"No pending payments to process for: {telegram_id}")
                return any_payment_successful
            
            for payment in pending_payments:
                logger.info(f"Processing payment {payment.id} for user {telegram_id}")
                try:
                    with cls._meta.database.atomic():
                        result = cls._process_single_payment(payment, now)
                        processed_count += 1 if result else 0
                except Exception as e:
                    errors += 1
                    logger.error(f"Failed processing payment {payment.id}: {str(e)}")
                    continue
            
        except DatabaseError as e:
            logger.critical(f"Database error during payment processing: {str(e)}")
        
        logger.info(
            f"Payment processing complete. for: {telegram_id}"
            f"Success: {processed_count}, "
            f"Expired: {expired_count}, "
            f"Errors: {errors}"
        )
        return any_payment_successful
        
    @classmethod
    def check_pending_payments(cls) -> None:
        """s
        Process all pending payments and update membership statuses.
        
        Includes error handling, transaction management, and detailed logging.
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        processed_count = 0
        expired_count = 0
        errors = 0

        try:
            # Get pending payments in chronological order
            pending_payments = cls.select().where(
                (cls.status == 'pending') &
                (cls.expiry > now)
            ).order_by(cls.expiry.asc())
            
            expired_count = cls.mark_expired_payments(now)
            
            if not pending_payments:
                logger.info("No pending payments to process")
                return

            logger.info(f"Processing {len(pending_payments)} pending payments")

            for payment in pending_payments:
                try:
                    with cls._meta.database.atomic():
                        result = cls._process_single_payment(payment, now)
                        processed_count += 1 if result else 0
                except Exception as e:
                    errors += 1
                    logger.error(f"Failed processing payment {payment.id}: {str(e)}")
                    continue
            
        except DatabaseError as e:
            logger.critical(f"Database error during payment processing: {str(e)}")
            return

        logger.info(
            f"Payment processing complete. "
            f"Success: {processed_count}, "
            f"Expired: {expired_count}, "
            f"Errors: {errors}"
        )

    @classmethod
    def _process_single_payment(cls, payment: 'Payment', now: datetime.datetime) -> bool:
        """
        Process a single payment and return success status
        
        Parameters:
            payment (Payment): The payment object to be processed.
            now (datetime.datetime): The current date and time used for membership expiry calculations.

        Returns:
            bool: True if the payment was successfully processed, 
                  False otherwise.
        """
        logger.info(
            f"Processing payment {payment.id} for user {payment.user.telegram_id}"
        )

        if not payment.user.wallet_address:
            logger.warning(
                f"Skipping payment {payment.id} - no wallet address for user "
                f"{payment.user.telegram_id}"
            )
            return False

        try:
            payment_made = check_tron_transaction(
                payment.user.wallet_address,
                payment.deposit_address,
                payment.amount
            )
        except Exception as e:
            logger.error(
                f"Transaction check failed for payment {payment.id}: {str(e)}"
            )
            return False

        if not payment_made:
            logger.info(f"Payment {payment.id} not yet received")
            return False

        # Update payment status
        payment.status = 'completed'
        payment.save()

        # Calculate membership extension
        user = payment.user
        current_expiry = user.membership_expiry or now
        if current_expiry < now:
            current_expiry = now

        new_expiry = current_expiry + datetime.timedelta(
            days=payment.duration_days
        )
        user.membership_expiry = new_expiry
        user.save()

        logger.info(
            f"Payment {payment.id} completed. "
            f"New membership expiry: {new_expiry.isoformat()}"
        )
        return True

    @classmethod
    def mark_expired_payments(cls, now: datetime.datetime, telegram_id: int) -> int:
        """
        Mark expired payments and return count of affected rows
        
        Parameters:
            now (datetime.datetime): The current date and time used to etermine if payments are expired.
            
            telegram_id (int, optional): The Telegram ID of the user whose payments should be marked. 
                                         If None, all expired payments will be marked.

        Returns:
            int: The count of payments that were marked as expired.
        
        """
        where = (cls.status == 'pending') & (cls.expiry <= now)
        if telegram_id:
            where &= (cls.user.telegram_id == telegram_id)
            
        expired_count = cls.update(status='expired').where(where).execute()
        
        if expired_count > 0:
            logger.info(f"Marked {expired_count} payments as expired")
            
        return expired_count


with db:
    db.create_tables([User, Payment])
