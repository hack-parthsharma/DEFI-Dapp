import { useEthers, useTokenBalance } from "@usedapp/core";
import { formatUnits } from "ethers/lib/utils";
import { Token } from "../Main";
import { BalanceMsg } from "./BalanceMsg";

export interface BalanceProps {
  token: Token;
}

export const Balance = ({ token }: BalanceProps) => {
  const { name, address, image } = token;
  console.log(`tokenAddress=${address}`);
  const { account } = useEthers();
  console.log(`account=${account}`);
  const tokenBalance = useTokenBalance(address, account);
  console.log(`tokenBalance=${tokenBalance}`);

  const formattedTokenBalance: number = tokenBalance
    ? parseFloat(formatUnits(tokenBalance, 18))
    : 0;
  return (
    <BalanceMsg
      label={`Your unstaked ${name} balance`}
      amount={formattedTokenBalance}
      tokenImg={image}
    />
  );
};
