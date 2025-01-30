import datetime

from database import Payment, DatabaseError
from config import translations as __
from logger import logger

async def background_processing(app):
    logger.info("background_processing method")
    now = datetime.datetime.now(datetime.timezone.utc)
    processed_count = 0
    expired_count = 0
    errors = 0
    
    try:
        expired_count = Payment.mark_expired_payments(now, None)
        
        # Get pending payments in chronological order
        pending_payments = Payment.select().where(
            (Payment.status == 'pending') &
            (Payment.expiry > now)
        ).order_by(Payment.expiry.asc())
        
        if not pending_payments:
            logger.info("No pending payments to process")
            return

        logger.info(f"Processing {len(pending_payments)} pending payments on bg")

        for payment in pending_payments:
            try:
                result = Payment.process_single_payment(payment, now)
                if result:
                    processed_count += 1 
                    user = payment.user
                    text = __[user.lang]['order']['accept'].format(date=user.get_membership_expiry.date())
                    logger.info(f"user:{user} text:{text}")
                    await app.bot.send_message(
                            chat_id=user.telegram_id,
                            text=text
                        )
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
    