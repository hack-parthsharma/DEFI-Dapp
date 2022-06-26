import {
  Button,
  CircularProgress,
  Container,
  Input,
  Snackbar,
} from "@material-ui/core";
import { useEthers, useNotifications } from "@usedapp/core";
// import { formatUnits } from "ethers/lib/utils"
import React, { useEffect, useState } from "react";
import { Token } from "../Main";
import { useStakeTokens } from "../../hooks";
import { utils } from "ethers";
import { LoadingButton } from "@mui/lab";
import { Alert } from "@material-ui/lab";

export interface StakeProps {
  token: Token;
}

export const Stake = ({ token }: StakeProps) => {
  const { address: tokenAddress, name } = token;
  const { account } = useEthers();
  const { notifications } = useNotifications();

  const [amount, setAmount] = useState<
    number | string | Array<number | string>
  >(0);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newAmount =
      event.target.value === "" ? "" : Number(event.target.value);
    setAmount(newAmount);
    console.log(newAmount);
  };

  const { approve, state: approveAndStakeErc20State } =
    useStakeTokens(tokenAddress);

  const isMining = approveAndStakeErc20State.status === "Mining";

  const handleStakeSubmit = () => {
    const amountAsWei = utils.parseEther(amount.toString());
    return approve(amountAsWei.toString());
  };

  const [showERC20ApprovalSuccess, setShowERC20ApprovalSuccess] =
    useState(false);
  const [showStakeTokenSuccess, setShowStakeTokenSuccess] = useState(false);

  useEffect(() => {
    if (
      notifications.filter(
        (notification) =>
          notification.type === "transactionSucceed" &&
          notification.transactionName === "Approve ERC20 transfer"
      ).length > 0
    ) {
      setShowERC20ApprovalSuccess(true);
      setShowStakeTokenSuccess(false);
    }
    if (
      notifications.filter(
        (notification) =>
          notification.type === "transactionSucceed" &&
          notification.transactionName === "Stake Tokens"
      ).length > 0
    ) {
      setShowERC20ApprovalSuccess(false);
      setShowStakeTokenSuccess(true);
    }
  }, [notifications, showStakeTokenSuccess, showERC20ApprovalSuccess]);

  const handleCloseSnack = () => {
    setShowERC20ApprovalSuccess(false);
    setShowStakeTokenSuccess(false);
  };

  return (
    <>
      <div>
        <Input onChange={handleInputChange} />
        <Button
          onClick={handleStakeSubmit}
          color="primary"
          size="medium"
          disabled={isMining}
        >
          {isMining ? <CircularProgress size={26} /> : `Stake ${name}`}
        </Button>
      </div>
      <Snackbar
        open={showERC20ApprovalSuccess}
        autoHideDuration={5000}
        onClose={handleCloseSnack}
      >
        <Alert onClose={handleCloseSnack} severity="success">
          ERC-20 Token Transfer Approved!
        </Alert>
      </Snackbar>
      <Snackbar
        open={showStakeTokenSuccess}
        autoHideDuration={5000}
        onClose={handleCloseSnack}
      >
        <Alert onClose={handleCloseSnack} severity="success">
          Tokens Staked!
        </Alert>
      </Snackbar>
    </>
  );
};
