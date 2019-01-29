pragma solidity ^0.4.20;

contract ItemBase {
    modifier onlyBy(address _addr) {
        require(msg.sender == _addr);
        _;
    }

    struct Item {
        address company;
        address owner;
        bytes data;
    }

    uint public numItems;
    mapping (uint => Item) public items;

    event ItemLog(address indexed _company, address _owner, uint _itemID);
    event TransferLog(address _fromOwner, address _newOwner, uint _itemID);
    event DataModLog(address _sender, bytes _newData, bytes _oldData);
    event ItemScanLog(string _itemhash, bytes _datahash);//TODO: double check this

    function newItem(bytes data, address owner) public returns (uint itemID) {
        itemID = numItems++;
        items[itemID] = Item(msg.sender, owner, data);
        emit ItemLog(msg.sender, owner, itemID);
        emit TransferLog(msg.sender, owner, itemID);
    }

    function transferOwnership(uint itemID, address newOwner) public onlyBy(items[itemID].owner) {
        items[itemID].owner = newOwner;
        emit TransferLog(msg.sender, newOwner, itemID);
    }

    function modifyData(uint itemID, bytes newData) public onlyBy(items[itemID].company) {
        emit DataModLog(msg.sender, newData, items[itemID].data);
        items[itemID].data = newData;
    }

    function scanItem(string itemhash, bytes datahash) public {
        emit ItemScanLog(itemhash, datahash);
    }

    function getOwner(uint itemID) public returns (address) {
        return items[itemID].owner;
    }
}