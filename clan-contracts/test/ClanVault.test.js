const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ClanVault", function () {
  let ClanFactory, clanFactory;
  let ClanVault, clanVault;
  let owner, manager, member1, member2, nonMember;
  
  beforeEach(async function () {
    [owner, manager, member1, member2, nonMember] = await ethers.getSigners();
    
    // Deploy factory
    ClanFactory = await ethers.getContractFactory("ClanFactory");
    clanFactory = await ClanFactory.deploy();
    await clanFactory.waitForDeployment();
    
    // Create a clan
    const tx = await clanFactory.connect(owner).createClan("Test Clan");
    const receipt = await tx.wait();
    
    // Get clan address from event
    const event = receipt.logs.find(log => {
      try {
        return clanFactory.interface.parseLog(log).name === "ClanCreated";
      } catch (e) {
        return false;
      }
    });
    const clanAddress = clanFactory.interface.parseLog(event).args.clanAddress;
    
    // Get clan contract instance
    ClanVault = await ethers.getContractFactory("ClanVault");
    clanVault = ClanVault.attach(clanAddress);
  });
  
  describe("Deployment", function () {
    it("Should set the correct clan name", async function () {
      expect(await clanVault.clanName()).to.equal("Test Clan");
    });
    
    it("Should set the owner as OWNER role", async function () {
      const member = await clanVault.members(owner.address);
      expect(member.role).to.equal(3); // Role.OWNER = 3
      expect(member.isActive).to.be.true;
    });
    
    it("Should have 1 member initially (owner)", async function () {
      expect(await clanVault.getMemberCount()).to.equal(1);
    });
  });
  
  describe("Joining Clan", function () {
    it("Should allow non-members to join", async function () {
      await clanVault.connect(member1).joinClan();
      
      const member = await clanVault.members(member1.address);
      expect(member.role).to.equal(1); // Role.MEMBER = 1
      expect(member.isActive).to.be.true;
      expect(await clanVault.getMemberCount()).to.equal(2);
    });
    
    it("Should not allow joining twice", async function () {
      await clanVault.connect(member1).joinClan();
      await expect(
        clanVault.connect(member1).joinClan()
      ).to.be.revertedWith("Already a member");
    });
  });
  
  describe("Deposits", function () {
    beforeEach(async function () {
      await clanVault.connect(member1).joinClan();
    });
    
    it("Should allow members to deposit", async function () {
      const depositAmount = ethers.parseEther("1.0");
      
      await expect(
        clanVault.connect(member1).deposit({ value: depositAmount })
      ).to.emit(clanVault, "FundsDeposited")
        .withArgs(member1.address, depositAmount, await ethers.provider.getBlockNumber() + 1);
      
      const member = await clanVault.members(member1.address);
      expect(member.totalContributed).to.equal(depositAmount);
      expect(await clanVault.totalVaultBalance()).to.equal(depositAmount);
    });
    
    it("Should not allow non-members to deposit", async function () {
      await expect(
        clanVault.connect(nonMember).deposit({ value: ethers.parseEther("1.0") })
      ).to.be.revertedWith("Not a clan member");
    });
    
    it("Should track multiple deposits", async function () {
      await clanVault.connect(member1).deposit({ value: ethers.parseEther("1.0") });
      await clanVault.connect(member1).deposit({ value: ethers.parseEther("0.5") });
      
      const member = await clanVault.members(member1.address);
      expect(member.totalContributed).to.equal(ethers.parseEther("1.5"));
    });
  });
  
  describe("Withdrawals", function () {
    beforeEach(async function () {
      await clanVault.connect(member1).joinClan();
      await clanVault.connect(member2).joinClan();
      
      // Member1 deposits 2 ETH, Member2 deposits 1 ETH
      await clanVault.connect(member1).deposit({ value: ethers.parseEther("2.0") });
      await clanVault.connect(member2).deposit({ value: ethers.parseEther("1.0") });
    });
    
    it("Should allow members to withdraw their share", async function () {
      const member1Share = await clanVault.calculateMemberShare(member1.address);
      expect(member1Share).to.equal(ethers.parseEther("2.0"));
      
      const balanceBefore = await ethers.provider.getBalance(member1.address);
      const tx = await clanVault.connect(member1).withdraw(ethers.parseEther("1.0"));
      const receipt = await tx.wait();
      const gasUsed = receipt.gasUsed * receipt.gasPrice;
      const balanceAfter = await ethers.provider.getBalance(member1.address);
      
      expect(balanceAfter - balanceBefore + gasUsed).to.equal(ethers.parseEther("1.0"));
    });
    
    it("Should not allow withdrawing more than share", async function () {
      await expect(
        clanVault.connect(member1).withdraw(ethers.parseEther("3.0"))
      ).to.be.revertedWith("Insufficient balance");
    });
    
    it("Should calculate correct contribution percentage", async function () {
      // Member1: 2 ETH out of 3 ETH total = 66.66%
      const percentage = await clanVault.getContributionPercentage(member1.address);
      expect(percentage).to.equal(6666); // 66.66% in basis points
    });
  });
  
  describe("Manager Promotion", function () {
    beforeEach(async function () {
      await clanVault.connect(member1).joinClan();
    });
    
    it("Should allow owner to promote member to manager", async function () {
      await expect(
        clanVault.connect(owner).promoteToManager(member1.address)
      ).to.emit(clanVault, "ManagerPromoted")
        .withArgs(member1.address, await ethers.provider.getBlockNumber() + 1);
      
      const member = await clanVault.members(member1.address);
      expect(member.role).to.equal(2); // Role.MANAGER = 2
    });
    
    it("Should not allow non-owner to promote", async function () {
      await clanVault.connect(member2).joinClan();
      
      await expect(
        clanVault.connect(member2).promoteToManager(member1.address)
      ).to.be.revertedWith("Not the clan owner");
    });
  });
  
  describe("Fund Allocation", function () {
    beforeEach(async function () {
      await clanVault.connect(member1).joinClan();
      await clanVault.connect(owner).promoteToManager(member1.address);
      await clanVault.connect(owner).deposit({ value: ethers.parseEther("10.0") });
    });
    
    it("Should allow owner to allocate funds to manager", async function () {
      await expect(
        clanVault.connect(owner).allocateFunds(member1.address, ethers.parseEther("5.0"))
      ).to.emit(clanVault, "FundsAllocated")
        .withArgs(member1.address, ethers.parseEther("5.0"), await ethers.provider.getBlockNumber() + 1);
      
      const available = await clanVault.getManagerAvailableFunds(member1.address);
      expect(available).to.equal(ethers.parseEther("5.0"));
    });
    
    it("Should not allocate more than vault balance", async function () {
      await expect(
        clanVault.connect(owner).allocateFunds(member1.address, ethers.parseEther("20.0"))
      ).to.be.revertedWith("Insufficient vault balance");
    });
  });
  
  describe("Trade Recording", function () {
    beforeEach(async function () {
      await clanVault.connect(member1).joinClan();
      await clanVault.connect(owner).promoteToManager(member1.address);
      await clanVault.connect(owner).deposit({ value: ethers.parseEther("10.0") });
      await clanVault.connect(owner).allocateFunds(member1.address, ethers.parseEther("5.0"));
    });
    
    it("Should allow manager to record profitable trade", async function () {
      const profit = ethers.parseEther("1.0");
      
      await expect(
        clanVault.connect(member1).recordTrade(ethers.parseEther("2.0"), profit)
      ).to.emit(clanVault, "TradeExecuted");
      
      expect(await clanVault.totalVaultBalance()).to.equal(ethers.parseEther("11.0"));
    });
    
    it("Should allow manager to record losing trade", async function () {
      const loss = ethers.parseEther("-0.5");
      
      await clanVault.connect(member1).recordTrade(ethers.parseEther("2.0"), loss);
      
      expect(await clanVault.totalVaultBalance()).to.equal(ethers.parseEther("9.5"));
    });
    
    it("Should not allow using more than allocated", async function () {
      await expect(
        clanVault.connect(member1).recordTrade(ethers.parseEther("6.0"), 0)
      ).to.be.revertedWith("Exceeds allocated funds");
    });
  });
  
  describe("Vault Statistics", function () {
    beforeEach(async function () {
      await clanVault.connect(member1).joinClan();
      await clanVault.connect(member2).joinClan();
      await clanVault.connect(member1).deposit({ value: ethers.parseEther("2.0") });
      await clanVault.connect(member2).deposit({ value: ethers.parseEther("1.0") });
    });
    
    it("Should return correct vault stats", async function () {
      const stats = await clanVault.getVaultStats();
      
      expect(stats.balance).to.equal(ethers.parseEther("3.0"));
      expect(stats.contributions).to.equal(ethers.parseEther("3.0"));
      expect(stats.memberCount).to.equal(3); // owner + 2 members
    });
    
    it("Should return correct member details", async function () {
      const details = await clanVault.getMemberDetails(member1.address);
      
      expect(details.role).to.equal(1); // MEMBER
      expect(details.totalContributed).to.equal(ethers.parseEther("2.0"));
      expect(details.currentShare).to.equal(ethers.parseEther("2.0"));
      expect(details.contributionPercentage).to.equal(6666); // 66.66%
      expect(details.isActive).to.be.true;
    });
  });
});
