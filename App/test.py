from brownie import network,rpc, web3,accounts,Contract

def main():
    network.connect('avax-main-fork')
    print(network.show_active())


main()
pool = Contract.from_explorer('0x60aE616a2155Ee3d9A68541Ba4544862310933d4')
joe = Contract.from_explorer('0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd')
joe.approve(pool,10000000000000000,{'from':accounts[0]})
wavax = Contract.from_explorer('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')
wavax.approve(pool, 10000000000000000, {'from': accounts[0]})

plove = Contract.from_explorer('0x82A7625653AdC6507B2dF7501668509B8BE23A07')
plove.approve(pool,10000000000000000,{'from':accounts[0]})


#test = pool.swapExactTokensForTokensSupportingFeeOnTransferTokens(1,0,[wavax.address,joe.address],accounts[0],1645505646,{'from':accounts[0]})

#pool.swapExactTokensForTokensSupportingFeeOnTransferTokens(1,0,[wavax.address,plove.address],accounts[0],1645505646,{'from':accounts[0]})

