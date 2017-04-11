import os
from bitcoin import SelectParams
from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
from blocktrail import connection
from blocktrail.wallet import Wallet
from mnemonic.mnemonic import Mnemonic
from pycoin.key.BIP32Node import BIP32Node


class APIClient(object):
    def __init__(self, api_key, api_secret, network='BTC', testnet=False, api_version='v1', api_endpoint=None, debug=False):
        """
        :param str      api_key:        the API_KEY to use for authentication
        :param str      api_secret:     the API_SECRET to use for authentication
        :param str      network:        the crypto network to consume (eg BTC, LTC, etc)
        :param bool     testnet:        testnet network yes/no
        :param str      api_version:    the version of the API to consume
        :param str      api_endpoint:   overwrite the endpoint used
                                         this will cause the :network, :testnet and :api_version to be ignored!
        :param bool     debug:          print debug information when requests fail
        """

        self.testnet = testnet

        SelectParams('testnet' if self.testnet else 'mainnet')

        if api_endpoint is None:
            network = ("t" if testnet else "") + network.upper()
            api_endpoint = os.environ.get('BLOCKTRAIL_SDK_API_ENDPOINT', "https://api.blocktrail.com")
            api_endpoint = "%s/%s/%s" % (api_endpoint, api_version, network)

        self.client = connection.RestClient(api_endpoint=api_endpoint, api_key=api_key, api_secret=api_secret, debug=debug)

    def address(self, address):
        """
        get a single address

        :param str      address:        the address hash
        :rtype: dict
        """
        response = self.client.get("/address/%s" % (address, ))

        return response.json()

    def address_transactions(self, address, page=1, limit=20, sort_dir='asc'):
        """
        get all transactions for an address (paginated)

        :param str      address:        the address hash
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of transactions per page, can be between 1 and 200
        :param str      address:        sorted ASC or DESC (on time)
        :rtype: dict
        """

        response = self.client.get("/address/%s/transactions" % (address, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def address_unconfirmed_transactions(self, address, page=1, limit=20, sort_dir='asc'):
        """
        get all unconfirmed transactions for an address (paginated)

        :param str      address:        the address hash
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:       sorted ASC or DESC (on time)
        :rtype: dict
        """
        response = self.client.get("/address/%s/unconfirmed-transactions" % (address, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def address_unspent_outputs(self, address, page=1, limit=20, sort_dir='asc'):
        """
        get all inspent outputs for an address (paginated)

        :param str      address:        the address hash
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:       sorted ASC or DESC (on time)
        :rtype: dict
        """
        response = self.client.get("/address/%s/unspent-outputs" % (address, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def verify_address(self, address, signature):
        """
        verify ownership of an address

        :param str      address:        the address hash
        :param str      signature:      signature generated with PK with message being the :address
        :rtype: dict
        """
        response = self.client.post("/address/%s/verify" % (address, ), data={'signature': signature}, auth=True)

        return response.json()

    def all_blocks(self, page=1, limit=20, sort_dir='asc'):
        """
        get all blocks (paginated)

        :param int      page:            pagination page, starting at 1
        :param int      limit:           the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:        sorted ASC or DESC (on time)
        :rtype: dict
        """

        response = self.client.get("/all-blocks", params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def block_latest(self):
        """
        get the latest block

        :rtype: dict
        """
        response = self.client.get("/block/latest")

        return response.json()

    def block(self, block):
        """
        get a block

        :param str|int  block:           the block hash or block height
        :rtype: dict
        """

        response = self.client.get("/block/%s" % (block, ))

        return response.json()

    def block_transactions(self, block, page=1, limit=20, sort_dir='asc'):
        """
        get all transactions for a block (paginated)

        :param str|int  block:           the block hash or block height
        :param int      page:            pagination page, starting at 1
        :param int      limit:           the amount of transactions per page, can be between 1 and 200
        :param str      sort_dir:        sorted ASC or DESC (on time)
        :rtype: dict
        """

        response = self.client.get("/block/%s/transactions" % (block, ), params={'page': page, 'limit': limit, 'sort_dir': sort_dir})

        return response.json()

    def transaction(self, txhash):
        """
        get a single transaction

        :param str      txhash:          the transaction hash
        :rtype: dict
        """

        response = self.client.get("/transaction/%s" % (txhash, ))

        return response.json()

    def all_webhooks(self, page=1, limit=20):
        """
        get all webhooks (paginated)

        :param int      page:            pagination page, starting at 1
        :param int      limit:           the amount of webhooks per page, can be between 1 and 200
        :rtype: dict
        """

        response = self.client.get("/webhooks", params={'page': page, 'limit': limit})

        return response.json()

    def webhook(self, identifier):
        """
        get a webhook by it's identifier

        :param str      identifier:      the webhook identifier
        :rtype: dict
        """

        response = self.client.get("/webhook/%s" % (identifier, ))

        return response.json()

    def setup_webhook(self, url, identifier=None):
        """
        create a new webhook

        :param str      url:            the url to receive the webhook events
        :param str      identifier:     a unique identifier to associate with this webhook (optional)
        :rtype: dict
        """
        response = self.client.post("/webhook", data={'url': url, 'identifier': identifier}, auth=True)

        return response.json()

    def update_webhook(self, identifier, new_url=None, new_identifier=None):
        """
        update an existing webhook

        :param str      identifier:     the webhook identifier
        :param str      new_url:        the new webhook url
        :param str      new_identifier: the new webhook identifier
        :rtype: dict
        """
        response = self.client.put("/webhook/%s" % (identifier, ),
                                   data={'url': new_url, 'identifier': new_identifier},
                                   auth=True)

        return response.json()

    def delete_webhook(self, identifier):
        """
        deletes an existing webhook and any event subscriptions associated with it

        :param str      identifier:     the webhook identifier
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s" % (identifier, ), auth=True)

        return response.json()

    def webhook_events(self, identifier, page=1, limit=20):
        """
        get a paginated list of all the events a webhook is subscribed to

        :param str      identifier:     the webhook identifier
        :param int      page:           pagination page, starting at 1
        :param int      limit:          the amount of webhooks per page, can be between 1 and 200
        :rtype: dict
        """

        response = self.client.get("/webhook/%s/events" % (identifier, ), params={'page': page, 'limit': limit})

        return response.json()

    def subscribe_address_transactions(self, identifier, address, confirmations=6):
        """
        subscribes a webhook to transaction events on a particular address

        :param str      identifier:     the webhook identifier
        :param str      address:        the address hash
        :param str      confirmations:  the amount of confirmations to send
        :rtype: dict
        """
        response = self.client.post(
            "/webhook/%s/events" % (identifier, ),
            data={
                'event_type': 'address-transactions',
                'address': address,
                'confirmations': confirmations
            },
            auth=True
        )

        return response.json()

    def batch_subscribe_address_transactions(self, identifier, batch_data):
        """
        batch subscribes a webhook to multiple transaction events

        :param str      identifier:     the webhook identifier
        :param list     batch_data:
        :rtype: dict
        """
        for record in batch_data:
            record['event_type'] = 'address-transactions'

        response = self.client.post("/webhook/%s/events/batch" % (identifier, ), data=batch_data, auth=True)

        return response.json()

    def subscribe_new_blocks(self, identifier):
        """
        subscribes a webhook to new blocks

        :param str      identifier:     the webhook identifier
        :rtype: dict
        """
        response = self.client.post(
            "/webhook/%s/events" % (identifier, ),
            data={
                'event_type': 'block'
            },
            auth=True
        )

        return response.json()

    def subscribe_transaction(self, identifier, transaction, confirmations=6):
        """
        subscribes a webhook to events on a particular transaction

        :param str      identifier:     the webhook identifier
        :param str      transaction:    the transaction hash
        :param str      confirmations:  the amount of confirmations to send
        :rtype: dict
        """
        response = self.client.post(
            "/webhook/%s/events" % (identifier, ),
            data={
                'event_type': 'transaction',
                'transaction': transaction,
                'confirmations': confirmations
            },
            auth=True
        )

        return response.json()

    def unsubscribe_address_transactions(self, identifier, address):
        """
        unsubscribes a webhook to transaction events from a particular address

        :param str      identifier:     the webhook identifier
        :param str      address:        the address hash
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s/address-transactions/%s" % (identifier, address), auth=True)

        return response.json()

    def unsubscribe_new_blocks(self, identifier):
        """
        unsubscribes a webhook from new blocks

        :param str      identifier:     the webhook identifier
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s/block" % (identifier, ), auth=True)

        return response.json()

    def unsubscribe_transaction(self, identifier, transaction):
        """
        unsubscribes a webhook to to events on a particular transaction

        :param str      identifier:     the webhook identifier
        :param str      transaction:        the address hash
        :rtype: dict
        """
        response = self.client.delete("/webhook/%s/transaction/%s" % (identifier, transaction), auth=True)

        return response.json()

    def price(self):
        """
        get the current price index

        :rtype: dict
        """

        response = self.client.get("/price")

        return response.json()

    def verify_message(self, message, address, signature):
        """
        verify message signed bitcoin-core style

        :param str      message:
        :param str      address:
        :param str      signature:
        :rtype: dict
        """

        response = self.client.post("/verify_message", dict(
            message=message,
            address=address,
            signature=signature
        ))

        return response.json()['result']

    def all_wallets(self, page=1, limit=20):
        """
        get all wallets (paginated)

        :param int      page:            pagination page, starting at 1
        :param int      limit:           the amount of wallets per page, can be between 1 and 200
        :rtype: dict
        """

        response = self.client.get("/wallets", params={'page': page, 'limit': limit}, auth=True)

        return response.json()

    def create_new_wallet(self, identifier, passphrase, key_index=0):
        netcode = "XTN" if self.testnet else "BTC"

        primary_mnemonic = Mnemonic(language='english').generate(strength=512)
        primary_seed = Mnemonic.to_seed(primary_mnemonic, passphrase)
        primary_private_key = BIP32Node.from_master_secret(primary_seed, netcode=netcode)

        primary_public_key = primary_private_key.subkey_for_path("%d'.pub" % key_index)

        backup_mnemonic = Mnemonic(language='english').generate(strength=512)
        backup_seed = Mnemonic.to_seed(backup_mnemonic, "")
        backup_public_key = BIP32Node.from_master_secret(backup_seed, netcode=netcode).public_copy()

        checksum = self.create_checksum(primary_private_key)

        result = self._create_new_wallet(
            identifier=identifier,
            primary_public_key=(primary_public_key.as_text(), "M/%d'" % key_index),
            backup_public_key=(backup_public_key.as_text(), "M"),
            primary_mnemonic=primary_mnemonic,
            checksum=checksum,
            key_index=key_index
        )

        blocktrail_public_keys = result['blocktrail_public_keys']
        key_index = result['key_index']

        return Wallet(
            client=self,
            identifier=identifier,
            primary_mnemonic=primary_mnemonic,
            primary_private_key=primary_private_key,
            backup_public_key=backup_public_key,
            blocktrail_public_keys=blocktrail_public_keys,
            key_index=key_index,
            testnet=self.testnet
        ), primary_mnemonic, backup_mnemonic, blocktrail_public_keys

    def _create_new_wallet(self, identifier, primary_public_key, backup_public_key, primary_mnemonic, checksum, key_index):
        response = self.client.post("/wallet", data={
            'identifier': identifier,
            'primary_public_key': primary_public_key,
            'backup_public_key': backup_public_key,
            'primary_mnemonic': primary_mnemonic,
            'checksum': checksum,
            'key_index': key_index,
        }, auth=True)

        return response.json()

    def init_wallet(self, identifier, passphrase):
        netcode = "XTN" if self.testnet else "BTC"

        data = self.get_wallet(identifier)

        primary_seed = Mnemonic.to_seed(data['primary_mnemonic'], passphrase)
        primary_private_key = BIP32Node.from_master_secret(primary_seed, netcode=netcode)

        backup_public_key = BIP32Node.from_hwif(data['backup_public_key'][0])

        checksum = self.create_checksum(primary_private_key)
        if checksum != data['checksum']:
            raise Exception("Checksum [%s] does not match expected checksum [%s], most likely due to incorrect password" % (checksum, data['checksum']))

        blocktrail_public_keys = data['blocktrail_public_keys']
        key_index = data['key_index']

        return Wallet(
            client=self,
            identifier=identifier,
            primary_mnemonic=data['primary_mnemonic'],
            primary_private_key=primary_private_key,
            backup_public_key=backup_public_key,
            blocktrail_public_keys=blocktrail_public_keys,
            key_index=key_index,
            testnet=self.testnet
        )

    @staticmethod
    def create_checksum(key):
        key = CBitcoinSecret(key.wif())
        address = P2PKHBitcoinAddress.from_pubkey(key.pub)

        return str(address)

    def get_wallet(self, identifier):
        response = self.client.get("/wallet/%s" % (identifier, ), auth=True)

        return response.json()

    def get_wallet_balance(self, identifier):
        response = self.client.get("/wallet/%s/balance" % (identifier, ), auth=True)

        return response.json()

    def wallet_discovery(self, identifier, gap=200):
        # @TODO: 360s timeout
        response = self.client.get("/wallet/%s/discovery" % (identifier, ), params=dict(gap=gap), auth=True)

        return response.json()

    def get_new_derivation(self, identifier, path):
        response = self.client.post("/wallet/%s/path" % (identifier, ), data={
            'path': path,
        }, auth=True)

        return response.json()

    def upgrade_key_index(self, identifier, key_index, primary_public_key):
        response = self.client.post(
            "/wallet/%s/upgrade" % (identifier, ),
            data=dict(
                key_index=key_index,
                primary_public_key=primary_public_key
            ),
            auth=True
        )

        return response.json()

    def coin_selection(self, identifier, outputs, lockUTXO=False, allow_zero_conf=False):
        response = self.client.post(
            "/wallet/%s/coin-selection" % (identifier, ),
            params={
                'lock': lockUTXO,
                'zeroconf': allow_zero_conf
            },
            data=outputs,
            auth=True
        )

        return response.json()

    def send_transaction(self, identifier, raw_tx, paths, check_fee=False):
        response = self.client.post(
            "/wallet/%s/send" % (identifier, ),
            params={
                'check_fee': check_fee
            },
            data={
                'raw_transaction': raw_tx,
                'paths': paths
            },
            auth=True
        )

        return response.json()

    def wallet_transactions(self, identifier, page=1, limit=20):
        response = self.client.get("/wallet/%s/transactions" % (identifier, ), params={'page': page, 'limit': limit}, auth=True)

        return response.json()

    def wallet_addresses(self, identifier, page=1, limit=20):
        response = self.client.get("/wallet/%s/addresses" % (identifier, ), params={'page': page, 'limit': limit}, auth=True)

        return response.json()

    def setup_wallet_webhook(self, wallet_identifier, webhook_identifier, url):
        """
        create a new webhook for a wallet

        :param str      wallet_identifier:      the wallet identifier which which to create te webhook
        :param str      webhook_identifier:     a unique identifier to associate with this webhook
        :param str      url:                    the url to receive the webhook events
        :rtype: dict
        """
        response = self.client.post("/wallet/%s/webhook" % (wallet_identifier, ), data={'url': url, 'identifier': webhook_identifier}, auth=True)

        return response.json()

    def delete_wallet_webhook(self, wallet_identifier, webhook_identifier):
        """
        deletes an existing webhook for a wallet

        :param str      wallet_identifier:      the wallet identifier which which to create te webhook
        :param str      webhook_identifier:     a unique identifier to associate with this webhook
        :rtype: dict
        """
        response = self.client.delete("/wallet/%s/webhook/%s" % (wallet_identifier, webhook_identifier, ), auth=True)

        return response.json()
