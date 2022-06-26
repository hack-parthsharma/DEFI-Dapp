import { useContractFunction, useEthers } from "@usedapp/core";
import networkMapping from "../deployments/deployments.json";
import TokenFarm from "./abi/TokenFarm.json";
import ERC20 from "./abi/MockERC20.json";
import { constants, utils } from "ethers";
import { Contract } from "@ethersproject/contracts";
import { useEffect, useState } from "react";

export const useStakeTokens = (tokenAddress: string) => {
  // address
  // abi
  // chainId
  const { chainId } = useEthers();
  const { abi } = TokenFarm;
  const tokenFarmAddress = chainId
    ? networkMapping[String(chainId)]["TokenFarm"][0]
    : constants.AddressZero;
  const tokenFarmInterface = new utils.Interface(abi);
  const tokenFarmContract = new Contract(tokenFarmAddress, tokenFarmInterface);

  const erc20ABI = ERC20.abi;
  const erc20Interface = new utils.Interface(erc20ABI);
  const erc20Contract = new Contract(tokenAddress, erc20Interface);

  console.log(`erc20contract ${tokenAddress.toString()}`);

  const { send: approveErc20Send, state: approveAndStakeErc20State } =
    useContractFunction(erc20Contract, "approve", {
      transactionName: "Approve ERC20 transfer",
    });

  const approveAndStake = (amount: string) => {
    setAmountToStake(amount);
    return approveErc20Send(tokenFarmAddress, amount);
  };

  const { send: stakeSend, state: stakeState } = useContractFunction(
    tokenFarmContract,
    "stakeToken",
    {
      transactionName: "Stake Tokens",
    }
  );

  const [amountToStake, setAmountToStake] = useState("0");

  useEffect(() => {
    if (approveAndStakeErc20State.status === "Success") {
      stakeSend(tokenAddress, amountToStake);
    }
  }, [approveAndStakeErc20State, tokenAddress, amountToStake]);

  const [state, setState] = useState(approveAndStakeErc20State);

  useEffect(() => {
    setState(
      approveAndStakeErc20State.status === "Success"
        ? stakeState
        : approveAndStakeErc20State
    );
  }, [approveAndStakeErc20State, stakeState]);

  return { approve: approveAndStake, state };
};
