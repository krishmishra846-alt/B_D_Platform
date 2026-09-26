from immudb import ImmudbClient

class LedgerVault:
    def __init__(self):
        try:
            self.client = ImmudbClient("127.0.0.1:3322")
            self.client.login("immudb", "immudb")
            print("Connected to immudb Zero-Trust Ledger.")
        except Exception as e:
            print(f"Warning: Could not connect to immudb. Is the .exe running? Error: {e}")
            self.client = None

    def secure_store_donor(self, donor_uuid: str, encrypted_id: str, photo_hash: str, consent_timestamp: str):
        """Stores the Sensitive Audit Payload into the Merkle-Tree Ledger."""
        if not self.client:
            return False
            
        payload = f"ENC_ID:{encrypted_id}|PHOTO_HASH:{photo_hash}|CONSENT_TIME:{consent_timestamp}"
        
        # safeSet() writes the record and verifies the cryptographic proof
        try:
            self.client.safeSet(f"audit_donor_{donor_uuid}".encode('utf-8'), payload.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Ledger Write Failed: {e}")
            return False

# Instantiate the vault
vault = LedgerVault()