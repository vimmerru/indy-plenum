from plenum.test.pool_transactions.helper import \
    disconnect_node_and_ensure_disconnected, \
    reconnect_node_and_ensure_connected
from plenum.test.test_node import ensure_node_disconnected
from stp_core.common.log import getlogger
from plenum.test.helper import sdk_send_random_and_check
from plenum.test.node_catchup.helper import waitNodeDataEquality, \
    waitNodeDataInequality, checkNodeDataForEquality

# Do not remove the next import
from plenum.test.node_catchup.conftest import whitelist

logger = getlogger()
txnCount = 5


# TODO: Refactor tests to minimize module-scoped fixtures.They make tests
# depend on each other
def testNodeCatchupAfterLostConnection(sdk_new_node_caught_up, txnPoolNodeSet,
                                       sdk_node_set_with_node_added_after_some_txns):
    """
    A node that has poor internet connection and got unsynced after some
    transactions should eventually get the transactions which happened while
    it was not accessible
    :return:
    """
    looper, new_node, sdk_pool_handle, new_steward_wallet_handle = \
        sdk_node_set_with_node_added_after_some_txns
    logger.debug("Disconnecting node {}, ledger size {}".
                 format(new_node, new_node.domainLedger.size))
    disconnect_node_and_ensure_disconnected(looper, txnPoolNodeSet, new_node,
                                            stopNode=False)

    # TODO: Check if the node has really stopped processing requests?
    logger.debug("Sending requests")
    sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle,
                              new_steward_wallet_handle, 5)
    # Make sure new node got out of sync
    waitNodeDataInequality(looper, new_node, *txnPoolNodeSet[:-1])

    # logger.debug("Ensure node {} gets disconnected".format(newNode))
    ensure_node_disconnected(looper, new_node, txnPoolNodeSet[:-1])

    logger.debug("Connecting the node {} back, ledger size {}".
                 format(new_node, new_node.domainLedger.size))
    reconnect_node_and_ensure_connected(looper, txnPoolNodeSet, new_node)

    logger.debug("Waiting for the node to catch up, {}".format(new_node))
    waitNodeDataEquality(looper, new_node, *txnPoolNodeSet[:-1])

    logger.debug("Sending more requests")
    sdk_send_random_and_check(looper, txnPoolNodeSet, sdk_pool_handle,
                              new_steward_wallet_handle, 10)
    checkNodeDataForEquality(new_node, *txnPoolNodeSet[:-1])
