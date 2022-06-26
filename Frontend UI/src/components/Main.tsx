import { useEthers } from "@usedapp/core";
import deploymentMappings from "../deployments/deployments.json";
import chainIdMappings from "../deployments/chain_id.json";
import brownieConfig from "../brownie-config.json";
import { constants } from "ethers";

import dappImage from "./images/dapp.png";
import ethImage from "./images/ethereum.png";
import daiImage from "./images/dai.png";
import { Wallet } from "./Wallet/Wallet";
import { makeStyles } from "@material-ui/core";

import logo from "./images/logo.png";

export type Token = {
  name: string;
  address: string;
  image: string;
};

const useStyles = makeStyles((theme) => ({
  title: {
    color: theme.palette.common.white,
    textAlign: "center",
    padding: theme.spacing(4),
  },
  tokenImg: {
    width: "64px",
    alignItems: "left",
  },
}));

export const Main = () => {
  const classes = useStyles();

  const { chainId } = useEthers();
  const networkName = chainId ? chainIdMappings[String(chainId)] : "N/A";

  const dappTokenAddress = chainId
    ? deploymentMappings[String(chainId)]["DappToken"][0]
    : constants.AddressZero;

  const wethTokenAddress = chainId
    ? brownieConfig["networks"][networkName]["weth_token"]
    : constants.AddressZero;

  const fauTokenAddress = chainId
    ? brownieConfig["networks"][networkName]["fau_token"]
    : constants.AddressZero;

  const supportedTokens: Array<Token> = [
    {
      name: "DAPP",
      address: dappTokenAddress,
      image: dappImage,
    },
    {
      name: "ETH",
      address: wethTokenAddress,
      image: ethImage,
    },
    {
      name: "DAI",
      address: fauTokenAddress,
      image: daiImage,
    },
  ];

  return (
    <>
      <div>
        <h2 className={classes.title}>
          <img src={logo} className={classes.tokenImg}></img>
          My DaPP Manager!
        </h2>
      </div>
      <Wallet supportedTokens={supportedTokens} />
    </>
  );
};
