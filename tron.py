import base58
import os
import requests
from dotenv import load_dotenv

load_dotenv()

TEST_MODE = os.getenv("TEST_MODE", "True").lower() == "true"
TRON_NETWORK = 'https://api.nileex.io' if TEST_MODE else 'https://api.trongrid.io'
USDT_CONTRACT = os.getenv("TEST_USDT_CONTRACT") if TEST_MODE else os.getenv("USDT_CONTRACT")



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


def check_tron_transaction(sender_address, recipient_address, amount):
    
    response = requests.post(f'{TRON_NETWORK}/wallet/triggerconstantcontract',
        json={
            'contract_address': USDT_CONTRACT,
            'function_selector': 'balanceOf(address)',
            'parameter': recipient_address,
            'owner_address': sender_address
        }
    )
    
    return response.json().get('constant_result', [0])[0] >= amount * 10**6

