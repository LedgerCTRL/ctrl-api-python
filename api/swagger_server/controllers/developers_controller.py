# core
import connexion
import six
import ipfsapi
import redis
import ast
import random
import json
import redis
import secrets
from enum import Enum
import requests
import sys
import os

# web3
from web3 import Web3, HTTPProvider
from solc import compile_source
from solc.exceptions import SolcError
from web3.contract import ConciseContract
from web3.middleware import geth_poa_middleware

# telegram
import logging
#from telegram.ext import Updater
#from telegram.ext import CommandHandler

# flask
import flask
from functools import wraps
from flask import redirect, send_file, request, abort
from werkzeug.utils import secure_filename

# swagger
from swagger_server.models.inventory_item import InventoryItem  # noqa: E501
from swagger_server.util.solidinterpret import eventsCode, integrateCode, readContract, CustomContract
from swagger_server import util


IPFS_HOST = '172.16.66.5'  # http left out ON PURPOSE
IPFS_PORT = 5001

REDIS_HOST = '172.16.66.6'
REDIS_PORT = 6379
REDIS_PASS = "Secrets should be stored in local files."

WEB3_HOST = "http://172.16.66.3"
WEB3_PORT = 8545

w3 = Web3(HTTPProvider(WEB3_HOST + ":" + str(WEB3_PORT)))

# ONLY USED FOR TESTING ON DEV NETWORK
w3.middleware_stack.inject(geth_poa_middleware, layer=0)

# TODO: use redis to store this dynamically
# potential bug: new deployment has bad offset & doesn't retrieve any results
BASE_BLOCK = 1


def getRedis():
    return redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def newApp(user):
    red = getRedis()
    red.set("users:" + user['email'], json.dumps(user))
    red.set(user['appId'], json.dumps(user))


# decorator function
def requires_key(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        red = getRedis()
        key = request.headers.get('key')
        appId = request.headers.get('appId')
        user = json.loads(red.get(appId))
        if key and key == user['key']:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function


def itembaseInstance():  # TODO: make itembase modular to user
    c = CustomContract.Itembase
    return w3.eth.contract(address=get_itembase(), abi=getAbi(c['code'], c['name']))


def erc20Instance(address):
    c = CustomContract.ERC20
    return w3.eth.contract(address=address, abi=getAbi(c['code'], c['name']))


def getAbi(source, contractName):
    compiledSol = compile_source(source)
    contract_interface = compiledSol['<stdin>:' + contractName]

    return contract_interface['abi']


def deployContract(source, contractName):
    w3.eth.defaultAccount = w3.eth.accounts[0]

    try:
        compiledSol = compile_source(source)
        contractInterface = compiledSol['<stdin>:' + contractName]

        contract = w3.eth.contract(
            abi=contractInterface['abi'], bytecode=contractInterface['bin'])

        txHash = contract.constructor().transact()

        tx_receipt = w3.eth.waitForTransactionReceipt(txHash)
        return tx_receipt
    except SolcError as e:
        abort(400, e.message)


def deployItembase():
    c = CustomContract.Itembase
    return deployContract(c['code'], c['name'])


def deployERC20(contractName, events=None, options=None):
    c = CustomContract.ERC20
    # TODO: let users name their token
    code = c['code']
    # if events are passed, write them into the code
    if (events):
        code = integrateCode(CustomContract.ERC20, eventsCode(events), options)
        print(code)
    return deployContract(code, c['name'])


def ipfsAdd(item, isFile=True):
    api = ipfsapi.connect(IPFS_HOST, IPFS_PORT)

    if (isFile):
        res = api.add(item)
    elif (type(item) == str):
        res = api.add_str(item)
    elif (type(item) == dict):
        res = api.add_json(item)
    elif (type(item) == bytes):
        res = api.add_bytes(item)
    else:
        try:
            res = api.add_pyobj(item)
        except Exception as e:
            res = None

    return res


def ipfsGetItem(itemhash):
    api = ipfsapi.connect(IPFS_HOST, IPFS_PORT)

    return api.get_json(itemhash)


# item: str (IPFS hash)
# address: str
def ethAdd(item, userIndex):
    userIndex = int(userIndex)
    uacct = w3.eth.accounts[userIndex]

    w3.eth.defaultAccount = w3.eth.accounts[0]  # sign tx with master

    itembase = itembaseInstance()
    txHash = itembase.functions.newItem(item, uacct).transact()

    receipt = w3.eth.waitForTransactionReceipt(txHash)

    print(receipt['blockNumber'])

    if (receipt):
        return receipt
    return "ERROR"


# eth items "owned by" userIndex
def ethItems(userIndex):
    userIndex = int(userIndex)
    userAcct = w3.eth.accounts[userIndex]
    print(w3.eth.accounts[0])

    itembase = itembaseInstance()

    # items transferred to user
    transInputFilter = itembase.events.TransferLog.createFilter(
        fromBlock=BASE_BLOCK, argument_filters={'_newOwner': userAcct})

    # items transferred from user
    transOutputFilter = itembase.events.TransferLog.createFilter(
        fromBlock=BASE_BLOCK, argument_filters={'_fromOwner': userAcct})

    transferInputs = transInputFilter.get_all_entries()
    transferOutputs = transOutputFilter.get_all_entries()

    # if count(in(ID)) > count(out(ID)): I own this
    cin = {}
    for i in transferInputs:
        iid = i['args']['_itemID']
        if (iid in cin):
            cin[iid] += 1
        else:
            cin[iid] = 1

    for i in transferOutputs:
        iid = i['args']['_itemID']
        if (iid in cin):
            cin[iid] -= 1

    out = []
    for i in transferInputs:
        iid = i['args']['_itemID']
        if (cin[iid] > 0):
            out.append(i)

    print("Tx INPUTS\n%s\nTx OUTPUTS\n\n%s\nOUT\n%s\n\n" %
          (transferInputs, transferOutputs, out))

    return out


def ethItem(itemId, userIndex):
    userIndex = int(userIndex)
    acct = w3.eth.accounts[userIndex]
    itembase = itembaseInstance()

    return itembase.call({'from': acct}).items(itemId)


def getItemEthID(itemhash):
    item = ipfsGetItem(itemhash)

    try:
        ethid = item["ethId"]
        return int(ethid)
    except KeyError as e:
        print("this item does not have ethID mapped.\n%s" % e)
        return -1
    except Exception as e:
        print("SOMETHING WENT WRONG -- THIS SHOULD NEVER HAPPEN\n%s" % e)
    return -2


def getItems(userIndex):
    items = ethItems(userIndex)

    # fetch items by creator
    out = []

    for i in items:
        # parse out just itemID from result
        args = i['args']
        out.append(args['_itemID'])

    # retrieve item hashes from ETH
    iout = []
    for itemId in out:
        xi = ethItem(itemId, userIndex)
        iout.append(xi)

    # strip off binary BS from results
    txout = []
    for obj in iout:
        txout.append(str(obj[2]).replace('b', '', 1).strip("'"))

    # uniquify item list
    s = set(txout)
    a = list(s)

    dout = []

    # get item names/hashes
    api = ipfsapi.connect(IPFS_HOST, IPFS_PORT)
    for i in a:
        ffile = api.get_json(i)
        filename = ffile['fileHash']['Name']
        filehash = ffile['fileHash']['Hash']
        ethId = ffile['ethId']
        dout.append(
            {'itemhash': i, 'ethId': ethId, 'filename': filename, 'filehash': filehash})

    return dout


def generateAppId():
    return secrets.token_urlsafe(32)


def generateKey():
    return secrets.token_urlsafe(64)


# transfer some ETH to user for making transactions
def initUser(userIndex):
    user = w3.eth.accounts[userIndex]
    admin = w3.eth.accounts[0]
    payload = {"from": admin, "to": user, "value": w3.toWei(1, "ether")}
    tx = w3.eth.sendTransaction(payload)

    return tx


def newEthUser(password):
    account = w3.personal.newAccount(password['password'])
    index = len(ethUsers()) - 1

    tx = initUser(index)

    data = {"address": account, "index": index}
    return data


def ethUsers():
    return w3.personal.listAccounts


# ROUTES ======================================================================
def new_api_key(email):
    _email = email['email']

    # generate keys
    appId = generateAppId()
    key = generateKey()
    apiUser = {"appId": appId, "key": key, "email": _email}

    # store key associations in DB
    newApp(apiUser)

    return apiUser


@requires_key
def new_eth_user(password):
    return newEthUser(password)


@requires_key
def eth_users():
    return ethUsers()


@requires_key
def eth_user(userIndex):
    userIndex = int(userIndex)
    return eth_users()[userIndex]


@requires_key
def eth_balance(userIndex):
    return w3.eth.getBalance(w3.eth.accounts[userIndex])


@requires_key
def eth_latestItemID():
    itembase = itembaseInstance()
    w3.eth.defaultAccount = w3.eth.accounts[0]
    num = itembase.functions.numItems().call(
        {'from': w3.eth.defaultAccount})
    return num


@requires_key
def add_inventory(inventoryItem, userIndex, upfile=None, public=False):  # noqa: E501
    """adds an inventory item

    Adds an item to the system # noqa: E501

    :param inventoryItem: JSON-encoded item detail
    :type inventoryItem: str
    :param userIndex: User's ETH index
    :type userIndex: str
    :param upfile: The file to upload
    :type upfile: werkzeug.datastructures.FileStorage

    :rtype: str
    """

    item = {}

    # convert inventoryItem to dict since it's passed as a string
    item['inventoryItem'] = json.loads(inventoryItem)

    # if we have a file, add that first
    fileHash = None
    if (upfile):
        filename = secure_filename(upfile.filename)
        # save file locally (temporary)
        upfile.save(filename)
        # upload to IPFS
        fileHash = ipfsAdd(filename)

    # if we stored a file, add its hash to iItem
    if (fileHash):
        item['fileHash'] = fileHash

    # add eth index to item
    item['ethId'] = eth_latestItemID()  # THIS MIGHT BE BUGGY (TODO)

    if (public):
        item['public'] = True
    else:
        item['public'] = False

    # add item to IPFS
    i = ipfsAdd(item, False)

    # add hash to ETH
    e = ethAdd(bytes(i, 'utf-8'), userIndex)

    if (i and e):
        result = {"status": "success",
                  "itemHash": i,
                  "txHash": (e['transactionHash']).hex(),
                  "ethId": item['ethId']}
    else:
        result = {"status": "failed"}

    # return resI
    return result


@requires_key
def get_file(id):  # noqa: E501
    """fetches file associated with item ID

    fetches file associated with item ID # noqa: E501

    :param id: unique item ID
    :type id: str

    :rtype: str
    """

    api = ipfsapi.connect(IPFS_HOST, IPFS_PORT)

    ffile = api.get_json(id)
    filename = ffile['fileHash']['Name']
    filehash = ffile['fileHash']['Hash']

    api.get(filehash)
    fpr = open(filehash, "rb")

    return send_file(fpr, as_attachment=True, attachment_filename=filename)


@requires_key
def get_item(id):  # noqa: E501
    """fetches individual item by id

    fetches individual item by id # noqa: E501

    :param id: unique item ID
    :type id: str

    :rtype: InventoryItem
    """
    api = ipfsapi.connect(IPFS_HOST, IPFS_PORT)
    return api.get_json(id)


@requires_key
def get_items(userIndex):
    """ fetches items by userId

    :param userId: unique user ID
    :type userId: str

    :rtype: array
    """
    return getItems(userIndex)


@requires_key
def scan_item(data):
    itemID = data['itemId']
    scanData = data['scanData']

    itemID = bytes(itemID, "utf-8")

    # add data (json) to IPFS
    datahash = ipfsAdd(json.loads(scanData), False)
    datahash = bytes(datahash, "utf-8")

    # get itembase
    itembase = itembaseInstance()
    w3.eth.defaultAccount = w3.eth.accounts[0]  # sign tx with master

    # call ETH scan function & return hash
    txhash = itembase.functions.scanItem(
        itemID, datahash).transact()

    return str(txhash.hex())


@requires_key
def get_scans(itemhash):
    itembase = itembaseInstance()

    itemhash = str(itemhash)

    eventFilter = itembase.events.ItemScanLog.createFilter(
        fromBlock=BASE_BLOCK)
    # TODO: figure out argument_filters={"_itemhash": itemhash}
    # TODO: dynamically set fromBlock

    result = eventFilter.get_all_entries()

    o = []
    for r in result:
        if (r['args']['_itemhash'] == itemhash):
            t = str(r['args']['_datahash']).strip("'b")
            o.append(t)

    ipfs = ipfsapi.connect(IPFS_HOST)
    scans = []
    for scan in o:
        s = ipfs.get_json(scan)
        scans.append(s)
    return scans


@requires_key
def transfer_item(request):
    userIndex = request['userIndex']
    userPass = request['userPass']
    itemhash = request['itemhash']
    newOwnerIndex = request['newOwnerIndex']
    newOwner = request['newOwner']

    # get og item
    item = ipfsGetItem(itemhash)
    ethid = item['ethId']

    # modify item to reflect new owner
    item['inventoryItem']['owner'] = newOwner

    # upload new item to ipfs
    newItem = ipfsAdd(item, False)

    print("newItem: " + str(newItem))

    if (ethid >= 0):
        return eth_transfer_item(userIndex, userPass, ethid, newOwnerIndex, newItem)
    else:
        return "Could not transfer"


@requires_key
def eth_modify_data(itemId, newData):
    itembase = itembaseInstance()

    w3.eth.defaultAccount = w3.eth.accounts[0]
    tx = itembase.functions.modifyData(itemId, newData).transact({
        "from": w3.eth.defaultAccount})
    return tx


@requires_key
def eth_transfer_item(userIndex, userPass, itemID, newOwnerIndex, newItemhash):
    # get itembase
    itembase = itembaseInstance()

    # get users' addresses from geth
    userAddress = w3.eth.accounts[userIndex]
    newOwnerAddress = w3.eth.accounts[newOwnerIndex]

    if (w3.personal.unlockAccount(userAddress, userPass, 3)):
        # IDEA: estimate gas & transfer it from admin to user

        # call ETH transferOwnership function
        tx = itembase.functions.transferOwnership(
            itemID, newOwnerAddress).transact({"gas": 90000, "from": userAddress})

        # mod ETH data
        eth_modify_data(itemID, bytes(newItemhash, 'utf-8'))

        return tx.hex()
    else:
        return "incorrect password"


@requires_key
def get_transfers(itemhash):
    itembase = itembaseInstance()
    itemID = getItemEthID(itemhash)
    transfilter = itembase.events.TransferLog.createFilter(
        fromBlock=BASE_BLOCK, argument_filters={'_itemID': itemID})

    transfers = transfilter.get_all_entries()

    o = []
    for t in transfers:
        print(t)
        _fromOwner = t['args']['_fromOwner']
        _newOwner = t['args']['_newOwner']
        _block = t['blockNumber']
        data = {'from': _fromOwner, 'to': _newOwner, 'block': _block}
        o.append(data)

    return o


@requires_key
def new_itembase(userId):
    if userId['userId'] != "Gypsy Magic 42069!!!":
        print(userId)
        print("Gypsy Magic 42069!!!")
        return "This call is restricted to admins only."
    contract = deployItembase()
    contractAddress = contract['contractAddress']
    red = getRedis()
    red.set('itembase', contractAddress)
    print("Set new itembase: %s" % contractAddress)
    return contractAddress


@requires_key
def new_erc20(data):
    userId = data['userId']
    tokenName = data['tokenName']
    events = None
    options = None

    if ('options' in data):
        options = data['options']
    if ('events' in data):
        events = data['events']

    contract = deployERC20(tokenName, events, options)
    contractAddress = contract['contractAddress']
    red = getRedis()
    red.set('erc20:%s.%s' % (userId, tokenName), contractAddress)
    print("Deployed new ERC20 token: %s" % contractAddress)
    return contractAddress


@requires_key
def new_contract(data):
    source = data['source']
    name = data['name']
    contract = deployContract(source, name)
    contractAddress = contract['contractAddress']
    print("Deployed new smart contract: %s" % contractAddress)
    return contractAddress


@requires_key
def get_itembase():
    red = getRedis()
    res = red.get('itembase')
    if (res):
        print("Found existing itembase: %s" % res)
        return res
    else:
        print("Itembase does not exist. Deploying new contract...")
        itembase = new_itembase(0)
        red.set('itembase', itembase)
        return itembase


# telegram thing
# updater.idle()
