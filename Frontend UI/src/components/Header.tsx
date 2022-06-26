import { Button, makeStyles } from "@material-ui/core";
import { useEthers } from "@usedapp/core";

const useStyles = makeStyles((theme) => ({
  container: {
    padding: theme.spacing(4),
    display: "flex",
    justifyContent: "flex-end",
    gap: theme.spacing(1),
  },
}));

export const Header = () => {
  const { account, activateBrowserWallet, deactivate } = useEthers();
  const isConnected = account !== undefined;

  const classes = useStyles();

  return (
    <div className={classes.container}>
      <div>
        {isConnected ? (
          <Button color="secondary" onClick={deactivate} variant="contained">
            Disconnect
          </Button>
        ) : (
          <Button
            color="secondary"
            onClick={() => activateBrowserWallet()}
            variant="outlined"
          >
            Connect
          </Button>
        )}
      </div>
    </div>
  );
};
