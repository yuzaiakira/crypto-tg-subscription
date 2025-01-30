from logger import logger
import base58
import os
import requests
import datetime
from dotenv import load_dotenv

load_dotenv()

TEST_MODE: bool = os.getenv("TEST_MODE", "True").lower() == "true"
TRONGRID_API_KEY: str = os.getenv("TRONGRID_API_KEY")

# jst token for testnet 
TOKEN_DECIMALS: int = 18 if TEST_MODE else 6

TRON_NETWORK: str = 'https://nile.trongrid.io/' if TEST_MODE else 'https://api.trongrid.io'
USDT_CONTRACT: str = os.getenv("TEST_USDT_CONTRACT") if TEST_MODE else os.getenv("USDT_CONTRACT")



def validate_tron_wallet_address(wallet_address: str) -> bool:
    """
    Validate a TRON wallet address.

    Args:
        address (str): The TRON wallet address to validate.

    Returns:
        bool: True if the address is valid, False otherwise.
    """
    # Check if the address starts with 'T' and is 34 characters long
    if not (wallet_address.startswith('T') and len(wallet_address) == 34):
        return False

    try:
        # Decode the Base58 address
        decoded = base58.b58decode_check(wallet_address)
        
        # Ensure the decoded address is 21 bytes long (1 byte prefix + 20 bytes address)
        if len(decoded) != 21:
            return False

        # The first byte should be 0x41 (prefix for TRON addresses)
        if decoded[0] != 0x41:
            return False

        return True
    except (ValueError, Exception):
        # Handle invalid Base58 or checksum errors
        return False
    
    
def generate_deposit_address()->str:
    """
    creagenerate wallet addresste for deposit  
   
    Returns:
        str: Wallet address
    """
    
    return os.getenv("WALLET")


def check_tron_transaction(sender_address:str, recipient_address:str, amount:float, timestamp: datetime.timedelta) -> str|bool:
    """
    Checks for a TRON transaction from a specified sender to a recipient with a given amount and timestamp.

    This function queries the TRON network to verify if a transaction of a specified amount 
    (in TRC20 tokens) has occurred from the sender's address to the recipient's address 
    after a specified timestamp. It returns the transaction ID if a valid transaction is found, 
    or False if no valid transaction exists or if an error occurs during the request.

    Parameters:
    - sender_address (str): The address of the sender in the TRON network.
    - recipient_address (str): The address of the recipient in the TRON network.
    - amount (float): The amount of TRC20 tokens to check for in the transaction.
    - timestamp (datetime.timedelta): The minimum timestamp (as a timedelta) after which the transaction should have occurred.

    Returns:
    - str | bool: The transaction ID of the valid transaction if found, otherwise False.

    Raises:
    - requests.exceptions.RequestException: If there is an issue with the network request to the TRON API.

    Logs:
    - Logs the process of checking the transaction, including the amount, sender, recipient, 
      and any errors encountered during the request.
    """
    
    logger.info(f"checking {amount} from {sender_address} to {recipient_address}")
    
    required_amount = int(amount * 10**TOKEN_DECIMALS)  
    min_timestamp = timestamp.timestamp() * 1000
    logger.info(f'min_timestamp {min_timestamp}')

    headers = {"TRON-PRO-API-KEY": TRONGRID_API_KEY}
    url = f"{TRON_NETWORK}/v1/accounts/{recipient_address}/transactions/trc20"
    
    params = {
        "contract_address": USDT_CONTRACT,
        "from": sender_address,
        "to": recipient_address,
        "min_timestamp": min_timestamp,
        "only_confirmed": "true",
        "order_by": "block_timestamp,desc",
        "limit": 1
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logger.info(str(response.json()))
        transactions = response.json().get("data", [])
        logger.info(f"Found {len(transactions)} transactions to check")
        for tx in transactions:
            tx_amount = int(tx.get("value", 0))
            tx_time = tx.get("block_timestamp", 0)
            
            if tx_amount == required_amount and tx_time >= min_timestamp:
                logger.info(f"Valid transaction found: {tx['transaction_id']}")
                return tx['transaction_id']

        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Transaction check failed: {str(e)}")
        return False

