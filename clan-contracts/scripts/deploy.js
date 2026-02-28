const hre = require("hardhat");

async function main() {
  console.log("Deploying Clan Contracts...\n");

  // Get the deployer account
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying contracts with account:", deployer.address);
  
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatEther(balance), "ETH\n");

  // Deploy ClanFactory (from Clan.sol)
  console.log("Deploying ClanFactory...");
  const ClanFactory = await hre.ethers.getContractFactory("ClanFactory");
  const clanFactory = await ClanFactory.deploy();
  await clanFactory.waitForDeployment();
  
  const factoryAddress = await clanFactory.getAddress();
  console.log("✓ ClanFactory deployed to:", factoryAddress);

  // Wait for a few block confirmations
  console.log("\nWaiting for block confirmations...");
  await clanFactory.deploymentTransaction().wait(5);
  
  console.log("\n" + "=".repeat(60));
  console.log("DEPLOYMENT SUMMARY");
  console.log("=".repeat(60));
  console.log("Network:", hre.network.name);
  console.log("ClanFactory Address:", factoryAddress);
  console.log("Deployer:", deployer.address);
  console.log("=".repeat(60));
  
  // Save deployment info
  const fs = require('fs');
  const deploymentInfo = {
    network: hre.network.name,
    clanFactory: factoryAddress,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber()
  };
  
  fs.writeFileSync(
    `deployments/${hre.network.name}.json`,
    JSON.stringify(deploymentInfo, null, 2)
  );
  
  console.log("\n✓ Deployment info saved to deployments/" + hre.network.name + ".json");
  
  // Verification instructions
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("\nTo verify the contract, run:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${factoryAddress}`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
