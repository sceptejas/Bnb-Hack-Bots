// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ClanVault {
    enum Role { NONE, MEMBER, MANAGER, OWNER }
    
    struct Member {
        Role role;
        uint256 contributed;
        bool active;
    }
    
    string public name;
    address public owner;
    uint256 public totalBalance;
    uint256 public totalContributions;
    
    mapping(address => Member) public members;
    mapping(address => uint256) public managerAllocation;
    address[] public memberList;
    
    event Joined(address member);
    event Deposited(address member, uint256 amount);
    event Withdrawn(address member, uint256 amount);
    event Promoted(address manager);
    event Allocated(address manager, uint256 amount);
    event Traded(address manager, uint256 amount, int256 pnl);
    
    modifier onlyMember() {
        require(members[msg.sender].active, "Not member");
        _;
    }
    
    modifier onlyManager() {
        require(members[msg.sender].role >= Role.MANAGER, "Not manager");
        _;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    constructor(string memory _name, address _owner) {
        name = _name;
        owner = _owner;
        members[_owner] = Member(Role.OWNER, 0, true);
        memberList.push(_owner);
    }
    
    function join() external {
        require(!members[msg.sender].active, "Already member");
        members[msg.sender] = Member(Role.MEMBER, 0, true);
        memberList.push(msg.sender);
        emit Joined(msg.sender);
    }
    
    function deposit() external payable onlyMember {
        require(msg.value > 0, "Zero deposit");
        members[msg.sender].contributed += msg.value;
        totalBalance += msg.value;
        totalContributions += msg.value;
        emit Deposited(msg.sender, msg.value);
    }
    
    function withdraw(uint256 amount) external onlyMember {
        uint256 share = getShare(msg.sender);
        require(amount <= share && amount <= totalBalance, "Insufficient balance");
        
        uint256 reduction = (amount * members[msg.sender].contributed) / share;
        members[msg.sender].contributed -= reduction;
        totalBalance -= amount;
        
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        emit Withdrawn(msg.sender, amount);
    }
    
    function getShare(address member) public view returns (uint256) {
        if (totalContributions == 0) return 0;
        return (totalBalance * members[member].contributed) / totalContributions;
    }
    
    function promote(address member) external onlyOwner {
        require(members[member].active && members[member].role == Role.MEMBER, "Invalid");
        members[member].role = Role.MANAGER;
        emit Promoted(member);
    }
    
    function allocate(address manager, uint256 amount) external onlyOwner {
        require(members[manager].role == Role.MANAGER, "Not manager");
        require(amount <= totalBalance, "Insufficient balance");
        managerAllocation[manager] += amount;
        emit Allocated(manager, amount);
    }
    
    function trade(uint256 amount, int256 pnl) external onlyManager {
        require(amount <= managerAllocation[msg.sender], "Exceeds allocation");
        managerAllocation[msg.sender] -= amount;
        
        if (pnl > 0) {
            totalBalance += uint256(pnl);
        } else if (pnl < 0) {
            uint256 loss = uint256(-pnl);
            require(loss <= totalBalance, "Loss exceeds balance");
            totalBalance -= loss;
        }
        emit Traded(msg.sender, amount, pnl);
    }
    
    function getMemberCount() external view returns (uint256) {
        return memberList.length;
    }
    
    receive() external payable {
        totalBalance += msg.value;
    }
}

contract ClanFactory {
    address[] public clans;
    mapping(address => address[]) public userClans;
    
    event Created(address clan, string name, address owner);
    
    function create(string memory _name) external returns (address) {
        ClanVault clan = new ClanVault(_name, msg.sender);
        address clanAddr = address(clan);
        clans.push(clanAddr);
        userClans[msg.sender].push(clanAddr);
        emit Created(clanAddr, _name, msg.sender);
        return clanAddr;
    }
    
    function getClans() external view returns (address[] memory) {
        return clans;
    }
    
    function getUserClans(address user) external view returns (address[] memory) {
        return userClans[user];
    }
}
