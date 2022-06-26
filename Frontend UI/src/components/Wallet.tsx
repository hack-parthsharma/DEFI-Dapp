import { Box, makeStyles, Tab } from "@material-ui/core";
import { TabContext, TabList, TabPanel } from "@material-ui/lab";
import React, { useState } from "react";
import { Token } from "../Main";
import { Balance } from "./Balance";
import { Stake } from "./Stake";

const useStyles = makeStyles((theme) => ({
  tabContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: theme.spacing(4),
  },
  box: {
    backgroundColor: "white",
    borderRadius: "25px",
  },
  header: {
    color: "white",
  },
}));

interface WalletProps {
  supportedTokens: Array<Token>;
}

export const Wallet = ({ supportedTokens }: WalletProps) => {
  const classes = useStyles();

  const [selectedTokenIndex, setSelectedTokenIndex] = useState<number>(0);

  const handleChange = (event: React.ChangeEvent<{}>, newValue: string) => {
    setSelectedTokenIndex(parseInt(newValue));
  };

  return (
    <Box>
      <h1 className={classes.header}> Your Wallet!</h1>
      <Box className={classes.box}>
        <TabContext value={selectedTokenIndex.toString()}>
          <TabList aria-label="state form tabs" onChange={handleChange}>
            {supportedTokens.map((token, index) => {
              return (
                <Tab label={token.name} value={index.toString()} key={index} />
              );
            })}
          </TabList>
          {supportedTokens.map((token, index) => {
            return (
              <TabPanel value={index.toString()} key={index}>
                <div className={classes.tabContent}>
                  <Balance token={supportedTokens[selectedTokenIndex]} />
                  <Stake token={supportedTokens[selectedTokenIndex]} />
                </div>
              </TabPanel>
            );
          })}
        </TabContext>
      </Box>
    </Box>
  );
};
