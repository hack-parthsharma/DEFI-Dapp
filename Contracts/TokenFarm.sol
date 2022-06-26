// SPDX-License-Identifier: MIT

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

pragma solidity ^0.8.0;

contract TokenFarm is Ownable {
    address[] public allowedTokens;

    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    address[] public stakers;

    IERC20 public dappToken;
    mapping(address => address) public tokenPriceFeed;

    constructor(address _dappToken) public {
        dappToken = IERC20(_dappToken);
    }

    function issueTokens() public onlyOwner {
        for (uint256 i = 0; i < stakers.length; i++) {
            address recipient = stakers[i];
            uint256 recipientValue = getUserValue(recipient);
            require(
                1000000000000000000000000 > recipientValue,
                " is too large!"
            );
            dappToken.transfer(recipient, recipientValue);
        }
    }

    function getUserValue(address _user) public view returns (uint256) {
        uint256 totalValue = 0;
        require(uniqueTokensStaked[_user] >= 0, "You have no tokens staked!");
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            totalValue += getUserTokenValue(_user, allowedTokens[i]);
        }
        return totalValue;
    }

    function getUserTokenValue(address _user, address _token)
        public
        view
        returns (uint256)
    {
        uint256 userTokens = stakingBalance[_token][_user];
        if (userTokens <= 0) return 0;

        (uint256 price, uint256 decimals) = getTokenValue(_token);

        return (userTokens * price) / 10**decimals;
    }

    function getTokenValue(address _token)
        public
        view
        returns (uint256, uint256)
    {
        address priceFeedAddress = tokenPriceFeed[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(
            priceFeedAddress
        );
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 decimals = priceFeed.decimals();
        return (uint256(price), decimals);
    }

    function addAllowedToken(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    function setPriceFeedContract(address _token, address _priceFeed)
        public
        onlyOwner
    {
        tokenPriceFeed[_token] = _priceFeed;
    }

    function stakeToken(address _token, uint256 _amount) public {
        require(_amount > 0, "Amount should be greater than 0!");
        require(tokenIsAllowed(_token), "Token is currently not allowed");

        IERC20(_token).transferFrom(msg.sender, address(this), _amount);

        updateUniqueTokensStaked(msg.sender, _token);

        stakingBalance[_token][msg.sender] += _amount;

        if (uniqueTokensStaked[msg.sender] == 1) stakers.push(msg.sender);
    }

    function tokenIsAllowed(address _token) public returns (bool) {
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if (allowedTokens[i] == _token) {
                return true;
            }
        }
        return false;
    }

    function updateUniqueTokensStaked(address _staker, address _token)
        internal
    {
        if (stakingBalance[_token][_staker] <= 0) uniqueTokensStaked[_staker]++;
    }

    function unstakeTokens(address _token) public {
        uint256 balance = stakingBalance[_token][msg.sender];
        require(balance > 0, "Staking balance cannot be 0");

        require(uniqueTokensStaked[msg.sender] > 0, "No unique tokens staked!");
        uniqueTokensStaked[msg.sender]--;

        IERC20(_token).transfer(msg.sender, balance);
        stakingBalance[_token][msg.sender] = 0;
    }
}
